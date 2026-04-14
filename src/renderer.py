"""ASCII art renderer for cyber bonsai."""

from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from rich.table import Table

from src.bonsai import GrowthStage, BonsaiData


class ASCIIRenderer:
    """Renderer for ASCII bonsai art.
    
    Renders bonsai in different growth stages with colors.
    
    Attributes:
        console: Rich console instance.
        colors: Color scheme for each stage.
    """
    
    COLORS = {
        GrowthStage.SPROUT: "bright_green",
        GrowthStage.GROWTH: "green",
        GrowthStage.MATURE: "dark_green",
        GrowthStage.FULL: "green4",
    }
    
    # ASCII art templates
    ART = {
        GrowthStage.SPROUT: """
    🌱
    |
   / \\
  /   \\
""",
        GrowthStage.GROWTH: """
      🌿
     /|\\
    / | \\
   /  |  \\
  /   |   \\
 /    |    \\
""",
        GrowthStage.MATURE: """
        🌳
       /|\\
      / | \\
     /  |  \\
    /   |   \\
   /    |    \\
  /_____|_____\\
     |     |
     |     |
""",
        GrowthStage.FULL: """
           🌲
          /||\\
         / || \\
        /  ||  \\
       /___||___\\
      /    ||    \\
     /_____||_____\\
    /______||______\\
        |      |
        |      |
        |      |
""",
    }
    
    def __init__(self, console: Console = None):
        """Initialize renderer.
        
        Args:
            console: Optional Rich console instance.
        """
        self.console = console or Console()
    
    def render(self, stage: GrowthStage, width: int = 40) -> str:
        """Render ASCII art for growth stage.
        
        Args:
            stage: Growth stage to render.
            width: Maximum width for rendering.
            
        Returns:
            ASCII art string.
        """
        art = self.ART.get(stage, self.ART[GrowthStage.SPROUT])
        return art
    
    def render_with_stats(self, data: BonsaiData) -> Panel:
        """Render bonsai with statistics panel.
        
        Args:
            data: BonsaiData with stage and statistics.
            
        Returns:
            Rich Panel with formatted display.
        """
        # Get color for stage
        color = self.COLORS.get(data.stage, "green")
        
        # Create ASCII art text
        art = self.ART.get(data.stage, self.ART[GrowthStage.SPROUT])
        art_text = Text(art, style=color)
        
        # Create stats table
        stats_table = Table(show_header=False, box=None)
        stats_table.add_column("Label", style="dim")
        stats_table.add_column("Value", style="bold")
        
        stage_names = {
            GrowthStage.SPROUT: "萌芽期 🌱",
            GrowthStage.GROWTH: "生长期 🌿",
            GrowthStage.MATURE: "成熟期 🌳",
            GrowthStage.FULL: "完全体 🌲",
        }
        
        stats_table.add_row("生长阶段:", stage_names.get(data.stage, "未知"))
        stats_table.add_row("贡献积分:", f"{data.current_score:.1f} / {data.next_threshold}")
        
        if data.recent_activity:
            stats_table.add_row("")
            stats_table.add_row("最近活动:", "")
            for i, activity in enumerate(data.recent_activity[:3], 1):
                event_type = activity.get("type", "Unknown")
                stats_table.add_row(f"  {i}.", event_type.replace("Event", ""))
        
        # Combine art and stats
        content = Table.grid()
        content.add_column()
        content.add_column()
        content.add_row(art_text, stats_table)
        
        return Panel(
            content,
            title="[bold]Cyber Bonsai[/bold]",
            border_style=color,
            padding=(1, 2),
        )
    
    def display(self, data: BonsaiData) -> None:
        """Display bonsai to console.
        
        Args:
            data: BonsaiData to display.
        """
        panel = self.render_with_stats(data)
        self.console.print(panel)
