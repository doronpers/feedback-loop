"""
Patterns Command

List and manage patterns.
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
@click.argument("pattern_name", required=False)
@click.option("--list", "-l", "list_patterns", is_flag=True, help="List all patterns")
@click.pass_context
def patterns(ctx, pattern_name, list_patterns):
    """📚 List and manage patterns.

    View pattern details and manage the pattern library.

    Examples:

      \b
      # List all patterns
      feedback-loop patterns --list

      \b
      # Show specific pattern
      feedback-loop patterns numpy_type_conversion
    """
    console = ctx.obj.get("console", Console())

    if list_patterns or not pattern_name:
        # List all patterns
        console.print("[bold cyan]Available Patterns[/bold cyan]\n")

        table = Table(show_header=True, header_style="bold magenta")
        table.add_column("Pattern", style="cyan")
        table.add_column("Category", style="green")
        table.add_column("Description", style="dim")

        # Load patterns from data/patterns.json
        patterns_file = project_root / "data" / "patterns.json"
        if patterns_file.exists():
            import json

            try:
                with open(patterns_file, "r") as f:
                    patterns_data = json.load(f)
                    if isinstance(patterns_data, dict):
                        for name, pattern in patterns_data.items():
                            table.add_row(
                                name,
                                pattern.get("category", "general"),
                                pattern.get("description", "")[:60] + "..."
                                if len(pattern.get("description", "")) > 60
                                else pattern.get("description", ""),
                            )
            except Exception as e:
                console.print(f"[yellow]Could not load patterns: {e}[/yellow]")
        else:
            table.add_row("No patterns file found", "", "Run 'feedback-loop analyze' first")

        console.print(table)
    else:
        # Show specific pattern
        console.print(f"[cyan]Pattern:[/cyan] {pattern_name}")
        console.print("[yellow]Pattern details view not yet implemented[/yellow]")
