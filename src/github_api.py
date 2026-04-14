"""GitHub API client for fetching contribution data."""

import json
import os
import time
from dataclasses import dataclass
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional

import requests


@dataclass
class ContributionData:
    """Data class for GitHub contribution statistics."""
    
    commits: int
    issues: int
    pull_requests: int
    reviews: int
    total_score: float
    raw_events: list[dict]


class GitHubAPIError(Exception):
    """Base exception for GitHub API errors."""
    
    def __init__(self, message: str, exit_code: int = 1):
        super().__init__(message)
        self.exit_code = exit_code


class GitHubAPI:
    """GitHub API client for contribution data.
    
    Fetches and caches GitHub activity data.
    
    Attributes:
        username: GitHub username to fetch data for.
        token: Optional GitHub Personal Access Token.
        cache_dir: Directory for caching API responses.
        cache_duration: Cache validity in seconds (default 1 hour).
    """
    
    BASE_URL = "https://api.github.com"
    
    # Scoring weights from PRD
    WEIGHTS = {
        "PushEvent": 1.0,
        "IssuesEvent": 1.5,
        "PullRequestEvent": 2.0,
        "PullRequestReviewEvent": 0.5,
    }
    
    def __init__(
        self,
        username: str,
        token: Optional[str] = None,
        cache_duration: int = 3600,
    ):
        """Initialize GitHub API client.
        
        Args:
            username: GitHub username.
            token: Optional PAT for authentication.
            cache_duration: Cache validity in seconds.
        """
        self.username = username
        self.token = token or self._get_token_from_env()
        self.cache_duration = cache_duration
        self.cache_dir = Path.home() / ".cache" / "cyber-bonsai"
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        
        self.session = requests.Session()
        if self.token:
            self.session.headers["Authorization"] = f"token {self.token}"
        self.session.headers["Accept"] = "application/vnd.github.v3+json"
    
    def _get_token_from_env(self) -> Optional[str]:
        """Get token from environment variables."""
        return os.environ.get("CYBER_BONSAI_TOKEN") or os.environ.get("GITHUB_TOKEN")
    
    def _get_cache_key(self, days: int) -> str:
        """Generate cache key for request."""
        today = datetime.now().strftime("%Y-%m-%d")
        return f"{self.username}_{days}_{today}"
    
    def _get_cache_path(self, days: int) -> Path:
        """Get cache file path."""
        key = self._get_cache_key(days)
        return self.cache_dir / f"{key}.json"
    
    def _load_cache(self, days: int) -> Optional[list]:
        """Load cached data if valid."""
        cache_path = self._get_cache_path(days)
        
        if not cache_path.exists():
            return None
        
        # Check cache age
        stat = cache_path.stat()
        age = time.time() - stat.st_mtime
        
        if age > self.cache_duration:
            return None
        
        try:
            with open(cache_path, "r") as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            return None
    
    def _save_cache(self, days: int, data: list) -> None:
        """Save data to cache."""
        cache_path = self._get_cache_path(days)
        
        try:
            with open(cache_path, "w") as f:
                json.dump(data, f)
            # Set restrictive permissions
            os.chmod(cache_path, 0o600)
        except IOError:
            pass  # Cache failure is non-fatal
    
    def _handle_rate_limit(self, response: requests.Response) -> None:
        """Handle rate limit errors."""
        if response.status_code == 403:
            remaining = response.headers.get("X-RateLimit-Remaining")
            if remaining == "0":
                reset_time = int(response.headers.get("X-RateLimit-Reset", 0))
                reset_str = datetime.fromtimestamp(reset_time).strftime("%H:%M:%S")
                raise GitHubAPIError(
                    f"API rate limit exceeded. Resets at {reset_str}. "
                    "Consider using a Personal Access Token.",
                    exit_code=2,
                )
        
        if response.status_code == 401:
            raise GitHubAPIError(
                "Authentication failed. Please check your GitHub token.",
                exit_code=3,
            )
        
        if response.status_code == 404:
            raise GitHubAPIError(
                f"User '{self.username}' not found.",
                exit_code=4,
            )
    
    def fetch_events(self, days: int = 30) -> list[dict]:
        """Fetch GitHub events for user.
        
        Args:
            days: Number of days to look back.
            
        Returns:
            List of GitHub event dictionaries.
            
        Raises:
            GitHubAPIError: On API errors.
        """
        # Check cache first
        cached = self._load_cache(days)
        if cached is not None:
            return cached
        
        # Calculate since date
        since = datetime.now() - timedelta(days=days)
        
        events = []
        page = 1
        per_page = 100
        
        while True:
            url = f"{self.BASE_URL}/users/{self.username}/events/public"
            params = {"page": page, "per_page": per_page}
            
            try:
                response = self.session.get(url, params=params, timeout=10)
            except requests.RequestException as e:
                raise GitHubAPIError(
                    f"Network error: {e}. Please check your internet connection.",
                    exit_code=1,
                )
            
            self._handle_rate_limit(response)
            
            if response.status_code != 200:
                raise GitHubAPIError(
                    f"GitHub API error: {response.status_code}",
                    exit_code=1,
                )
            
            page_events = response.json()
            if not page_events:
                break
            
            # Filter by date
            for event in page_events:
                event_time = datetime.fromisoformat(
                    event["created_at"].replace("Z", "+00:00")
                )
                if event_time >= since:
                    events.append(event)
            
            # Check if we've reached old events
            if page_events:
                last_event_time = datetime.fromisoformat(
                    page_events[-1]["created_at"].replace("Z", "+00:00")
                )
                if last_event_time < since:
                    break
            
            page += 1
            
            # Safety limit
            if page > 10:
                break
        
        # Save to cache
        self._save_cache(days, events)
        
        return events
    
    def calculate_contributions(self, events: list[dict]) -> ContributionData:
        """Calculate contribution score from events.
        
        Args:
            events: List of GitHub events.
            
        Returns:
            ContributionData with statistics.
        """
        counts = {"commits": 0, "issues": 0, "pull_requests": 0, "reviews": 0}
        
        for event in events:
            event_type = event.get("type", "")
            
            if event_type == "PushEvent":
                # Count commits in push
                payload = event.get("payload", {})
                commits = payload.get("commits", [])
                counts["commits"] += len(commits)
            
            elif event_type == "IssuesEvent":
                payload = event.get("payload", {})
                action = payload.get("action", "")
                if action in ["opened", "reopened"]:
                    counts["issues"] += 1
            
            elif event_type == "PullRequestEvent":
                payload = event.get("payload", {})
                action = payload.get("action", "")
                if action in ["opened", "reopened"]:
                    counts["pull_requests"] += 1
            
            elif event_type == "PullRequestReviewEvent":
                counts["reviews"] += 1
        
        # Calculate weighted score
        total_score = (
            counts["commits"] * self.WEIGHTS["PushEvent"] +
            counts["issues"] * self.WEIGHTS["IssuesEvent"] +
            counts["pull_requests"] * self.WEIGHTS["PullRequestEvent"] +
            counts["reviews"] * self.WEIGHTS["PullRequestReviewEvent"]
        )
        
        return ContributionData(
            commits=counts["commits"],
            issues=counts["issues"],
            pull_requests=counts["pull_requests"],
            reviews=counts["reviews"],
            total_score=total_score,
            raw_events=events[:20],  # Keep last 20 for display
        )
    
    def fetch_contributions(self, days: int = 30) -> ContributionData:
        """Fetch and calculate contributions.
        
        Args:
            days: Number of days to look back.
            
        Returns:
            ContributionData with statistics.
        """
        events = self.fetch_events(days)
        return self.calculate_contributions(events)
