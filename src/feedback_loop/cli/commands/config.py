"""
Config Command

Manage configuration.
"""

import sys
from pathlib import Path

import click
from rich.console import Console
from rich.table import Table

# Add project root to path
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))


@click.command()
@click.option("--show", "-s", is_flag=True, help="Show current configuration")
@click.option("--set", "set_key", help="Set configuration key (format: key=value)")
@click.pass_context
def config(ctx, show, set_key):
    """⚙️ Manage configuration.

    View and modify feedback-loop configuration.

    Examples:

      \b
      # Show current config
      feedback-loop config --show

      \b
      # Set a config value
      feedback-loop config --set api.provider=openai
    """
    console = ctx.obj.get("console", Console())

    if set_key:
        # Parse key=value
        if "=" not in set_key:
            console.print("[red]Error:[/red] Use format key=value")
            sys.exit(1)

        key, value = set_key.split("=", 1)
        console.print(f"[yellow]Config setting not yet implemented[/yellow]")
        console.print(f"[cyan]Would set:[/cyan] {key} = {value}")
    elif show:
        # Show configuration
        console.print("[bold cyan]Current Configuration[/bold cyan]\n")

        table = Table(show_header=True, header_style="bold magenta")
        table.add_column("Key", style="cyan")
        table.add_column("Value", style="green")

        # Load config
        try:
            from src.feedback_loop.config import get_config

            cfg = get_config()
            # Add config items to table
            table.add_row("Config loaded", "✓")
        except Exception:
            table.add_row("Default config", "Using defaults")

        console.print(table)
    else:
        # Show help
        console.print("[cyan]Use --show to view config or --set key=value to modify[/cyan]")
