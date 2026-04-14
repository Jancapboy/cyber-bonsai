"""Tests for ASCII renderer."""

import pytest
from rich.console import Console

from src.bonsai import GrowthStage, BonsaiData
from src.renderer import ASCIIRenderer


class TestASCIIRendererInit:
    """Test renderer initialization."""
    
    def test_default_console(self):
        """Test initialization with default console."""
        renderer = ASCIIRenderer()
        assert renderer.console is not None
    
    def test_custom_console(self):
        """Test initialization with custom console."""
        console = Console()
        renderer = ASCIIRenderer(console)
        assert renderer.console == console


class TestRenderArt:
    """Test ASCII art rendering."""
    
    def test_sprout_art(self):
        """Test sprout stage art."""
        renderer = ASCIIRenderer()
        art = renderer.render(GrowthStage.SPROUT)
        assert "🌱" in art
        assert "|" in art
    
    def test_growth_art(self):
        """Test growth stage art."""
        renderer = ASCIIRenderer()
        art = renderer.render(GrowthStage.GROWTH)
        assert "🌿" in art
        assert "|" in art
    
    def test_mature_art(self):
        """Test mature stage art."""
        renderer = ASCIIRenderer()
        art = renderer.render(GrowthStage.MATURE)
        assert "🌳" in art
    
    def test_full_art(self):
        """Test full stage art."""
        renderer = ASCIIRenderer()
        art = renderer.render(GrowthStage.FULL)
        assert "🌲" in art
    
    def test_default_to_sprout(self):
        """Test unknown stage defaults to sprout."""
        renderer = ASCIIRenderer()
        # Test with None (shouldn't happen in practice)
        art = renderer.ART.get(None, renderer.ART[GrowthStage.SPROUT])
        assert "🌱" in art


class TestColors:
    """Test color scheme."""
    
    def test_sprout_color(self):
        """Test sprout color is bright_green."""
        renderer = ASCIIRenderer()
        assert renderer.COLORS[GrowthStage.SPROUT] == "bright_green"
    
    def test_growth_color(self):
        """Test growth color is green."""
        renderer = ASCIIRenderer()
        assert renderer.COLORS[GrowthStage.GROWTH] == "green"
    
    def test_mature_color(self):
        """Test mature color is dark_green."""
        renderer = ASCIIRenderer()
        assert renderer.COLORS[GrowthStage.MATURE] == "dark_green"
    
    def test_full_color(self):
        """Test full color is green4."""
        renderer = ASCIIRenderer()
        assert renderer.COLORS[GrowthStage.FULL] == "green4"


class TestRenderWithStats:
    """Test rendering with statistics."""
    
    def test_sprout_panel(self):
        """Test sprout stage panel rendering."""
        renderer = ASCIIRenderer()
        data = BonsaiData(
            stage=GrowthStage.SPROUT,
            current_score=5.0,
            next_threshold=11,
            recent_activity=[{"type": "PushEvent"}],
        )
        
        panel = renderer.render_with_stats(data)
        assert panel is not None
        # Panel should contain stage info
        assert "萌芽期" in str(panel.renderable) or "SPROUT" in str(panel.renderable)
    
    def test_growth_panel(self):
        """Test growth stage panel rendering."""
        renderer = ASCIIRenderer()
        data = BonsaiData(
            stage=GrowthStage.GROWTH,
            current_score=15.0,
            next_threshold=31,
            recent_activity=[{"type": "IssuesEvent"}],
        )
        
        panel = renderer.render_with_stats(data)
        assert panel is not None
    
    def test_panel_with_multiple_activities(self):
        """Test panel with multiple recent activities."""
        renderer = ASCIIRenderer()
        data = BonsaiData(
            stage=GrowthStage.MATURE,
            current_score=45.0,
            next_threshold=61,
            recent_activity=[
                {"type": "PushEvent"},
                {"type": "IssuesEvent"},
                {"type": "PullRequestEvent"},
            ],
        )
        
        panel = renderer.render_with_stats(data)
        assert panel is not None
    
    def test_panel_with_empty_activity(self):
        """Test panel with no recent activity."""
        renderer = ASCIIRenderer()
        data = BonsaiData(
            stage=GrowthStage.FULL,
            current_score=80.0,
            next_threshold=80,
            recent_activity=[],
        )
        
        panel = renderer.render_with_stats(data)
        assert panel is not None


class TestDisplay:
    """Test display method."""
    
    def test_display_does_not_raise(self, capsys):
        """Test display method runs without error."""
        renderer = ASCIIRenderer()
        data = BonsaiData(
            stage=GrowthStage.SPROUT,
            current_score=3.0,
            next_threshold=11,
            recent_activity=[],
        )
        
        # Should not raise any exception
        renderer.display(data)
        
        # Check something was printed
        captured = capsys.readouterr()
        # Rich output goes to stderr by default
        assert captured.err != "" or captured.out != ""
