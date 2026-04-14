"""Tests for GitHub API client."""

from datetime import datetime

import pytest
import responses

from src.github_api import GitHubAPI, GitHubAPIError


class TestGitHubAPIInit:
    """Test GitHubAPI initialization."""

    def test_init_with_username_only(self):
        """Test initialization with just username."""
        api = GitHubAPI("testuser")
        assert api.username == "testuser"
        assert api.token is None

    def test_init_with_token(self):
        """Test initialization with token."""
        api = GitHubAPI("testuser", token="ghp_test123")
        assert api.username == "testuser"
        assert api.token == "ghp_test123"
        assert "Authorization" in api.session.headers

    def test_init_with_custom_cache_duration(self):
        """Test initialization with custom cache duration."""
        api = GitHubAPI("testuser", cache_duration=7200)
        assert api.cache_duration == 7200


class TestTokenFromEnv:
    """Test token loading from environment."""

    def test_token_from_cyber_bonsai_token(self, monkeypatch):
        """Test CYBER_BONSAI_TOKEN environment variable."""
        monkeypatch.setenv("CYBER_BONSAI_TOKEN", "ghp_env_token")
        api = GitHubAPI("testuser")
        assert api.token == "ghp_env_token"

    def test_token_from_github_token(self, monkeypatch):
        """Test GITHUB_TOKEN environment variable."""
        monkeypatch.setenv("GITHUB_TOKEN", "ghp_github_token")
        api = GitHubAPI("testuser")
        assert api.token == "ghp_github_token"

    def test_token_priority_cyber_bonsai_over_github(self, monkeypatch):
        """Test CYBER_BONSAI_TOKEN takes priority."""
        monkeypatch.setenv("CYBER_BONSAI_TOKEN", "ghp_cyber")
        monkeypatch.setenv("GITHUB_TOKEN", "ghp_github")
        api = GitHubAPI("testuser")
        assert api.token == "ghp_cyber"


class TestCache:
    """Test caching functionality."""

    def test_cache_key_generation(self):
        """Test cache key format."""
        api = GitHubAPI("testuser")
        key = api._get_cache_key(30)
        today = datetime.now().strftime("%Y-%m-%d")
        assert key == f"testuser_30_{today}"

    def test_cache_save_and_load(self, tmp_path, monkeypatch):
        """Test saving and loading from cache."""
        monkeypatch.setattr(GitHubAPI, "cache_dir", tmp_path)

        api = GitHubAPI("testuser")
        test_data = [{"type": "PushEvent", "id": "1"}]

        # Save to cache
        api._save_cache(30, test_data)

        # Load from cache
        loaded = api._load_cache(30)
        assert loaded == test_data

    def test_cache_expired(self, tmp_path, monkeypatch):
        """Test that expired cache returns None."""
        monkeypatch.setattr(GitHubAPI, "cache_dir", tmp_path)

        api = GitHubAPI("testuser", cache_duration=0)
        test_data = [{"type": "PushEvent"}]

        api._save_cache(30, test_data)
        loaded = api._load_cache(30)
        assert loaded is None  # Expired immediately


class TestCalculateContributions:
    """Test contribution calculation."""

    def test_empty_events(self):
        """Test calculation with no events."""
        api = GitHubAPI("testuser")
        result = api.calculate_contributions([])

        assert result.commits == 0
        assert result.issues == 0
        assert result.pull_requests == 0
        assert result.reviews == 0
        assert result.total_score == 0.0

    def test_push_event_commits(self):
        """Test counting commits in PushEvent."""
        api = GitHubAPI("testuser")
        events = [{
            "type": "PushEvent",
            "payload": {"commits": [{"sha": "abc"}, {"sha": "def"}]}
        }]

        result = api.calculate_contributions(events)
        assert result.commits == 2
        assert result.total_score == 2.0  # 2 * 1.0

    def test_issues_event_opened(self):
        """Test counting opened issues."""
        api = GitHubAPI("testuser")
        events = [{
            "type": "IssuesEvent",
            "payload": {"action": "opened"}
        }]

        result = api.calculate_contributions(events)
        assert result.issues == 1
        assert result.total_score == 1.5  # 1 * 1.5

    def test_issues_event_closed_not_counted(self):
        """Test that closed issues are not counted."""
        api = GitHubAPI("testuser")
        events = [{
            "type": "IssuesEvent",
            "payload": {"action": "closed"}
        }]

        result = api.calculate_contributions(events)
        assert result.issues == 0

    def test_pull_request_event(self):
        """Test counting opened PRs."""
        api = GitHubAPI("testuser")
        events = [{
            "type": "PullRequestEvent",
            "payload": {"action": "opened"}
        }]

        result = api.calculate_contributions(events)
        assert result.pull_requests == 1
        assert result.total_score == 2.0  # 1 * 2.0

    def test_review_event(self):
        """Test counting PR reviews."""
        api = GitHubAPI("testuser")
        events = [{"type": "PullRequestReviewEvent"}]

        result = api.calculate_contributions(events)
        assert result.reviews == 1
        assert result.total_score == 0.5  # 1 * 0.5

    def test_mixed_events(self):
        """Test calculation with mixed event types."""
        api = GitHubAPI("testuser")
        events = [
            {"type": "PushEvent", "payload": {"commits": [{"sha": "a"}]}},
            {"type": "IssuesEvent", "payload": {"action": "opened"}},
            {"type": "PullRequestEvent", "payload": {"action": "opened"}},
            {"type": "PullRequestReviewEvent"},
        ]

        result = api.calculate_contributions(events)
        assert result.commits == 1
        assert result.issues == 1
        assert result.pull_requests == 1
        assert result.reviews == 1
        assert result.total_score == 5.0  # 1 + 1.5 + 2.0 + 0.5


class TestErrorHandling:
    """Test error handling."""

    def test_rate_limit_error(self):
        """Test rate limit error detection."""
        api = GitHubAPI("testuser")

        class MockResponse:
            status_code = 403
            headers = {"X-RateLimit-Remaining": "0", "X-RateLimit-Reset": "1234567890"}

        with pytest.raises(GitHubAPIError) as exc_info:
            api._handle_rate_limit(MockResponse())

        assert exc_info.value.exit_code == 2
        assert "rate limit" in str(exc_info.value).lower()

    def test_auth_error(self):
        """Test authentication error."""
        api = GitHubAPI("testuser")

        class MockResponse:
            status_code = 401
            headers = {}

        with pytest.raises(GitHubAPIError) as exc_info:
            api._handle_rate_limit(MockResponse())

        assert exc_info.value.exit_code == 3
        assert "authentication" in str(exc_info.value).lower()

    def test_not_found_error(self):
        """Test user not found error."""
        api = GitHubAPI("testuser")

        class MockResponse:
            status_code = 404
            headers = {}

        with pytest.raises(GitHubAPIError) as exc_info:
            api._handle_rate_limit(MockResponse())

        assert exc_info.value.exit_code == 4
        assert "not found" in str(exc_info.value).lower()


@responses.activate
class TestFetchEvents:
    """Test fetching events from API."""

    def test_successful_fetch(self):
        """Test successful API fetch."""
        api = GitHubAPI("testuser")

        # Mock API response
        responses.add(
            responses.GET,
            "https://api.github.com/users/testuser/events/public",
            json=[{"type": "PushEvent", "id": "1", "created_at": "2024-01-15T10:00:00Z"}],
            status=200
        )

        events = api.fetch_events(days=30)
        assert len(events) == 1
        assert events[0]["type"] == "PushEvent"

    def test_network_error(self):
        """Test network error handling."""
        api = GitHubAPI("testuser")

        # Don't add mock response - will cause connection error
        with pytest.raises(GitHubAPIError) as exc_info:
            events = api.fetch_events(days=30)

        assert exc_info.value.exit_code == 1
        assert "network" in str(exc_info.value).lower()
