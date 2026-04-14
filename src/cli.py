"""Command line interface for cyber bonsai."""

import sys
from typing import Optional

import click
from rich.console import Console

from src.bonsai import BonsaiGrowth
from src.config import Config
from src.github_api import GitHubAPI, GitHubAPIError
from src.renderer import ASCIIRenderer


@click.group()
@click.option("--username", "-u", help="GitHub username")
@click.option("--token", "-t", help="GitHub Personal Access Token")
@click.option("--window", "-w", type=int, help="Time window in days")
@click.option("--no-cache", is_flag=True, help="Disable cache")
@click.option("--no-color", is_flag=True, help="Disable color output")
@click.option("--verbose", "-v", is_flag=True, help="Verbose output")
@click.pass_context
def cli(
    ctx: click.Context,
    username: Optional[str],
    token: Optional[str],
    window: Optional[int],
    no_cache: bool,
    no_color: bool,
    verbose: bool,
) -> None:
    """Cyber Bonsai - Terminal ASCII bonsai that grows with your GitHub activity."""
    # Load config
    config = Config.load()
    
    # Override with command line options
    if username:
        config.username = username
    if token:
        config.token = token
    if window:
        config.time_window = window
    if no_cache:
        config.cache_duration = 0
    if no_color:
        config.color_scheme = "never"
    
    # Store in context
    ctx.ensure_object(dict)
    ctx.obj["config"] = config
    ctx.obj["verbose"] = verbose
    ctx.obj["console"] = Console(force_terminal=not no_color)


@cli.command()
@click.pass_context
def show(ctx: click.Context) -> None:
    """Show current bonsai status."""
    config: Config = ctx.obj["config"]
    console: Console = ctx.obj["console"]
    verbose: bool = ctx.obj["verbose"]
    
    # Get username
    username = config.get_effective_username()
    if not username:
        console.print("[red]Error: GitHub username not configured.[/red]")
        console.print("Use --username or set CYBER_BONSAI_USERNAME")
        sys.exit(1)
    
    # Initialize API client
    token = config.get_effective_token()
    cache_duration = 0 if config.cache_duration == 0 else config.cache_duration
    
    try:
        api = GitHubAPI(
            username=username,
            token=token,
            cache_duration=cache_duration,
        )
        
        if verbose:
            console.print(f"[dim]Fetching data for {username}...[/dim]")
        
        # Fetch contributions
        contributions = api.fetch_contributions(days=config.time_window)
        
        if verbose:
            console.print(f"[dim]Found {len(contributions.raw_events)} events[/dim]")
            console.print(f"[dim]Score: {contributions.total_score:.1f}[/dim]")
        
        # Calculate growth stage
        growth = BonsaiGrowth()
        data = growth.get_stage_data(
            contributions.total_score,
            contributions.raw_events,
        )
        
        # Render and display
        renderer = ASCIIRenderer(console)
        renderer.display(data)
        
    except GitHubAPIError as e:
        console.print(f"[red]Error: {e}[/red]")
        sys.exit(e.exit_code)
    except Exception as e:
        if verbose:
            console.print_exception()
        else:
            console.print(f"[red]Error: {e}[/red]")
        sys.exit(1)


@cli.command()
@click.pass_context
def history(ctx: click.Context) -> None:
    """Show contribution history."""
    config: Config = ctx.obj["config"]
    console: Console = ctx.obj["console"]
    
    username = config.get_effective_username()
    if not username:
        console.print("[red]Error: GitHub username not configured.[/red]")
        sys.exit(1)
    
    console.print(f"[yellow]History feature coming soon![/yellow]")
    console.print(f"Will show trends for {username} over {config.time_window} days")


@cli.group()
def config_cmd() -> None:
    """Manage configuration."""
    pass


@config_cmd.command("set")
@click.argument("key")
@click.argument("value")
@click.pass_context
def config_set(ctx: click.Context, key: str, value: str) -> None:
    """Set configuration value."""
    console: Console = ctx.obj["console"]
    
    # Load current config
    config = Config.load()
    
    # Update value
    if hasattr(config, key):
        try:
            # Handle type conversion
            current_value = getattr(config, key)
            if isinstance(current_value, int):
                value = int(value)
            elif isinstance(current_value, bool):
                value = value.lower() in ("true", "1", "yes", "on")
            setattr(config, key, value)
            config.save()
            console.print(f"[green]Set {key} = {value}[/green]")
        except (ValueError, TypeError) as e:
            console.print(f"[red]Error setting {key}: {e}[/red]")
            sys.exit(1)
    else:
        console.print(f"[red]Unknown config key: {key}[/red]")
        console.print(f"Available keys: username, cache_duration, time_window, color_scheme")
        sys.exit(1)


@config_cmd.command("show")
@click.pass_context
def config_show(ctx: click.Context) -> None:
    """Show current configuration."""
    console: Console = ctx.obj["console"]
    
    config = Config.load()
    
    from rich.table import Table
    table = Table(title="Configuration")
    table.add_column("Key", style="cyan")
    table.add_column("Value", style="green")
    
    table.add_row("username", config.username or "(not set)")
    table.add_row("token", "***" if config.token else "(not set)")
    table.add_row("cache_duration", f"{config.cache_duration} seconds")
    table.add_row("time_window", f"{config.time_window} days")
    table.add_row("color_scheme", config.color_scheme)
    
    console.print(table)


@cli.command()
def version() -> None:
    """Show version information."""
    from src import __version__
    console = Console()
    console.print(f"Cyber Bonsai version [bold]{__version__}[/bold]")


def main() -> None:
    """Entry point for the CLI."""
    cli()


if __name__ == "__main__":
    main()
