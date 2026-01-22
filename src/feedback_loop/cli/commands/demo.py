"""
Demo Command

Run interactive demo.
"""

import sys
from pathlib import Path

import click
from rich.console import Console

# Add project root to path
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))


@click.command()
@click.pass_context
def demo(ctx):
    """🎭 Run interactive demo.

    Launch an interactive demo showing patterns in action.

    Examples:

      \b
      # Run demo
      feedback-loop demo
    """
    console = ctx.obj.get("console", Console())

    # Import and run the existing fl-demo
    try:
        sys.path.insert(0, str(project_root / "bin"))
        from fl_demo import main as demo_main

        demo_main()
    except ImportError:
        console.print("[yellow]Demo command not available[/yellow]")
        console.print("[cyan]Try running: python3 demo.py[/cyan]")
