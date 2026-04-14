"""Test configuration and shared fixtures."""

import pytest

from src.bonsai import BonsaiGrowth


@pytest.fixture
def growth():
    """Fixture providing a BonsaiGrowth instance."""
    return BonsaiGrowth()


@pytest.fixture
def sample_activity():
    """Fixture providing sample activity data."""
    return [
        {"type": "PushEvent", "count": 3},
        {"type": "IssuesEvent", "count": 1},
        {"type": "PullRequestEvent", "count": 2},
    ]
