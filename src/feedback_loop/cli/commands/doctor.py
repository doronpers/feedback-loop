"""
Doctor Command

Run diagnostics and health checks.
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
def doctor(ctx):
    """🩺 Run diagnostics and health checks.

    Checks your environment, dependencies, and configuration.

    Examples:

      \b
      # Run full diagnostics
      feedback-loop doctor
    """
    console = ctx.obj.get("console", Console())

    # Import and run the existing fl-doctor
    try:
        sys.path.insert(0, str(project_root / "bin"))
        from fl_doctor import main as doctor_main

        doctor_main()
    except ImportError:
        console.print("[yellow]Doctor command not available. Using basic checks...[/yellow]")
        # Basic fallback checks
        console.print("[cyan]Checking Python version...[/cyan]")
        console.print(f"  Python: {sys.version}")
        console.print("[cyan]Checking project structure...[/cyan]")
        console.print(f"  Project root: {project_root}")
        console.print(f"  Exists: {project_root.exists()}")
