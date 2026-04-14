"""Tests for bonsai growth logic."""

import pytest

from src.bonsai import BonsaiData, BonsaiGrowth, GrowthStage


@pytest.fixture
def growth():
    """Fixture for BonsaiGrowth instance."""
    return BonsaiGrowth()


class TestCalculateStage:
    """Test growth stage calculation."""

    def test_sprout_stage_boundary_low(self, growth):
        """Test that 0 contributions maps to sprout."""
        assert growth.calculate_stage(0) == GrowthStage.SPROUT

    def test_sprout_stage_boundary_high(self, growth):
        """Test that 10 contributions maps to sprout."""
        assert growth.calculate_stage(10) == GrowthStage.SPROUT

    def test_sprout_stage_mid(self, growth):
        """Test that 5 contributions maps to sprout."""
        assert growth.calculate_stage(5) == GrowthStage.SPROUT

    def test_growth_stage_boundary_low(self, growth):
        """Test that 11 contributions maps to growth."""
        assert growth.calculate_stage(11) == GrowthStage.GROWTH

    def test_growth_stage_boundary_high(self, growth):
        """Test that 30 contributions maps to growth."""
        assert growth.calculate_stage(30) == GrowthStage.GROWTH

    def test_growth_stage_mid(self, growth):
        """Test that 20 contributions maps to growth."""
        assert growth.calculate_stage(20) == GrowthStage.GROWTH

    def test_mature_stage_boundary_low(self, growth):
        """Test that 31 contributions maps to mature."""
        assert growth.calculate_stage(31) == GrowthStage.MATURE

    def test_mature_stage_boundary_high(self, growth):
        """Test that 60 contributions maps to mature."""
        assert growth.calculate_stage(60) == GrowthStage.MATURE

    def test_full_stage_boundary(self, growth):
        """Test that 61 contributions maps to full."""
        assert growth.calculate_stage(61) == GrowthStage.FULL

    def test_full_stage_high(self, growth):
        """Test that high contributions maps to full."""
        assert growth.calculate_stage(100) == GrowthStage.FULL

    def test_full_stage_very_high(self, growth):
        """Test that very high contributions maps to full."""
        assert growth.calculate_stage(1000) == GrowthStage.FULL


class TestErrorHandling:
    """Test error handling."""

    def test_negative_contributions(self, growth):
        """Test that negative contributions raise ValueError."""
        with pytest.raises(ValueError, match="cannot be negative"):
            growth.calculate_stage(-1)

    def test_negative_contributions_message(self, growth):
        """Test that error message is descriptive."""
        with pytest.raises(ValueError) as exc_info:
            growth.calculate_stage(-10)
        assert "negative" in str(exc_info.value).lower()


class TestGetProgress:
    """Test progress calculation."""

    def test_sprout_progress(self, growth):
        """Test progress in sprout stage."""
        current, next_level = growth.get_progress(5)
        assert current == 5
        assert next_level == 11

    def test_growth_progress(self, growth):
        """Test progress in growth stage."""
        current, next_level = growth.get_progress(20)
        assert current == 20
        assert next_level == 31

    def test_mature_progress(self, growth):
        """Test progress in mature stage."""
        current, next_level = growth.get_progress(45)
        assert current == 45
        assert next_level == 61

    def test_full_progress(self, growth):
        """Test progress in full stage (same value)."""
        current, next_level = growth.get_progress(80)
        assert current == 80
        assert next_level == 80


class TestGetStageData:
    """Test complete stage data retrieval."""

    def test_stage_data_structure(self, growth):
        """Test that BonsaiData has correct structure."""
        activity = [{"type": "commit", "count": 5}]
        data = growth.get_stage_data(15, activity)

        assert isinstance(data, BonsaiData)
        assert data.stage == GrowthStage.GROWTH
        assert data.current_score == 15
        assert data.next_threshold == 31
        assert len(data.recent_activity) == 1

    def test_stage_data_activity_limit(self, growth):
        """Test that activity is limited to 5 items."""
        activity = [{"type": "commit", "count": i} for i in range(10)]
        data = growth.get_stage_data(25, activity)

        assert len(data.recent_activity) == 5

    def test_stage_data_empty_activity(self, growth):
        """Test handling of empty activity list."""
        data = growth.get_stage_data(8, [])

        assert data.stage == GrowthStage.SPROUT
        assert data.recent_activity == []


class TestThresholds:
    """Test threshold definitions."""

    def test_thresholds_defined(self, growth):
        """Test that all stages have thresholds."""
        assert len(growth.THRESHOLDS) == 4
        assert GrowthStage.SPROUT in growth.THRESHOLDS
        assert GrowthStage.GROWTH in growth.THRESHOLDS
        assert GrowthStage.MATURE in growth.THRESHOLDS
        assert GrowthStage.FULL in growth.THRESHOLDS

    def test_threshold_ranges_valid(self, growth):
        """Test that threshold ranges are valid."""
        sprout_min, sprout_max = growth.THRESHOLDS[GrowthStage.SPROUT]
        growth_min, growth_max = growth.THRESHOLDS[GrowthStage.GROWTH]
        mature_min, mature_max = growth.THRESHOLDS[GrowthStage.MATURE]
        full_min, full_max = growth.THRESHOLDS[GrowthStage.FULL]

        # Check continuity
        assert sprout_max + 1 == growth_min
        assert growth_max + 1 == mature_min
        assert mature_max + 1 == full_min

        # Check full stage is unbounded
        assert full_max == float('inf')
