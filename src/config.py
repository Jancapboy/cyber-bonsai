"""Configuration management for cyber bonsai."""

import json
import os
from pathlib import Path

from pydantic import BaseModel, Field


class Config(BaseModel):
    """Configuration model for cyber bonsai.
    
    Attributes:
        username: GitHub username.
        token: Optional GitHub Personal Access Token.
        cache_duration: Cache validity in seconds.
        time_window: Number of days to look back.
        color_scheme: Color output preference.
    """

    username: str | None = None
    token: str | None = None
    cache_duration: int = Field(default=3600, ge=60, le=86400)
    time_window: int = Field(default=30, ge=1, le=365)
    color_scheme: str = Field(default="auto", pattern="^(auto|always|never)$")

    @classmethod
    def get_config_dir(cls) -> Path:
        """Get configuration directory."""
        config_dir = Path.home() / ".config" / "cyber-bonsai"
        config_dir.mkdir(parents=True, exist_ok=True)
        return config_dir

    @classmethod
    def get_config_path(cls) -> Path:
        """Get configuration file path."""
        return cls.get_config_dir() / "config.json"

    @classmethod
    def load(cls) -> "Config":
        """Load configuration from file.
        
        Returns:
            Config instance with loaded values.
        """
        config_path = cls.get_config_path()

        if config_path.exists():
            try:
                with open(config_path) as f:
                    data = json.load(f)
                return cls(**data)
            except (json.JSONDecodeError, ValueError):
                pass

        # Try environment variables
        return cls.from_env()

    @classmethod
    def from_env(cls) -> "Config":
        """Load configuration from environment variables.
        
        Returns:
            Config instance with environment values.
        """
        return cls(
            username=os.environ.get("CYBER_BONSAI_USERNAME"),
            token=os.environ.get("CYBER_BONSAI_TOKEN") or os.environ.get("GITHUB_TOKEN"),
            cache_duration=int(os.environ.get("CYBER_BONSAI_CACHE_DURATION", "3600")),
            time_window=int(os.environ.get("CYBER_BONSAI_TIME_WINDOW", "30")),
            color_scheme=os.environ.get("CYBER_BONSAI_COLOR_SCHEME", "auto"),
        )

    def save(self) -> None:
        """Save configuration to file."""
        config_path = self.get_config_path()

        # Don't save token to file for security
        data = self.model_dump()
        if data.get("token"):
            data["token"] = None

        with open(config_path, "w") as f:
            json.dump(data, f, indent=2)

        # Set restrictive permissions
        os.chmod(config_path, 0o600)

    def get_effective_username(self) -> str | None:
        """Get username from config or environment."""
        return self.username or os.environ.get("USER") or os.environ.get("USERNAME")

    def get_effective_token(self) -> str | None:
        """Get token from config or environment."""
        return self.token or os.environ.get("CYBER_BONSAI_TOKEN") or os.environ.get("GITHUB_TOKEN")
