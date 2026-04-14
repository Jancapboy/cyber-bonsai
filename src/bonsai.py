"""Cyber Bonsai - Core growth logic."""

from dataclasses import dataclass
from enum import Enum


class GrowthStage(Enum):
    """Growth stages based on contribution score."""

    SPROUT = "sprout"
    GROWTH = "growth"
    MATURE = "mature"
    FULL = "full"


@dataclass
class BonsaiData:
    """Data class for bonsai state."""

    stage: GrowthStage
    current_score: float
    next_threshold: int
    recent_activity: list[dict]


class BonsaiGrowth:
    """Core growth logic for cyber bonsai.

    Calculates growth stage based on GitHub contribution score.

    Attributes:
        thresholds: Score thresholds for each stage.
    """

    THRESHOLDS = {
        GrowthStage.SPROUT: (0, 10),
        GrowthStage.GROWTH: (11, 30),
        GrowthStage.MATURE: (31, 60),
        GrowthStage.FULL: (61, float('inf')),
    }

    def calculate_stage(self, contributions: float) -> GrowthStage:
        """Calculate growth stage based on contribution score.

        Args:
            contributions: The contribution score (0-100+).

        Returns:
            The corresponding growth stage.

        Raises:
            ValueError: If contributions is negative.
        """
        if contributions < 0:
            raise ValueError("Contributions cannot be negative")

        for stage, (min_score, max_score) in self.THRESHOLDS.items():
            if min_score <= contributions <= max_score:
                return stage

        return GrowthStage.FULL

    def get_progress(self, contributions: float) -> tuple[int, int]:
        """Get progress towards next stage.

        Args:
            contributions: Current contribution score.

        Returns:
            Tuple of (current_score, next_level_threshold).
        """
        stage = self.calculate_stage(contributions)
        _, current_max = self.THRESHOLDS[stage]

        if stage == GrowthStage.FULL:
            return int(contributions), int(contributions)

        return int(contributions), current_max + 1

    def get_stage_data(self, contributions: float, activity: list[dict]) -> BonsaiData:
        """Get complete bonsai data.
        
        Args:
            contributions: Current contribution score.
            activity: List of recent activity items.
            
        Returns:
            BonsaiData object with stage and progress info.
        """
        stage = self.calculate_stage(contributions)
        current, next_threshold = self.get_progress(contributions)

        return BonsaiData(
            stage=stage,
            current_score=current,
            next_threshold=next_threshold,
            recent_activity=activity[:5],  # Last 5 items
        )
