"""
Start Command

Start feedback-loop dashboard and services.
"""

import sys
from pathlib import Path

import click
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn

# Add project root to path
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))


@click.command()
@click.option("--port", default=8000, type=int, help="Port for dashboard server")
@click.option("--no-browser", is_flag=True, help="Don't open browser automatically")
@click.option("--demo", is_flag=True, help="Run interactive demo first")
@click.pass_context
def start(ctx, port, no_browser, demo):
    """🚀 Start feedback-loop dashboard and services.

    Launches the analytics dashboard and all backend services.

    Examples:

      \b
      # Start with default settings
      feedback-loop start

      \b
      # Start on custom port
      feedback-loop start --port 8080

      \b
      # Start without opening browser
      feedback-loop start --no-browser

      \b
      # Start with interactive demo
      feedback-loop start --demo
    """
    console = ctx.obj.get("console", Console())

    # Use subprocess to call the existing fl-start script
    import subprocess

    fl_start_script = project_root / "bin" / "fl-start"

    if not fl_start_script.exists():
        console.print("[red]Error:[/red] fl-start script not found")
        console.print("[yellow]Falling back to direct API startup...[/yellow]")

        # Fallback: start API directly
        try:
            import uvicorn
            from src.feedback_loop.api.main import app

            console.print(f"[cyan]Starting API server on port {port}...[/cyan]")
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                console=console,
            ) as progress:
                task = progress.add_task("Starting services...", total=None)
                uvicorn.run(app, host="0.0.0.0", port=port)
        except Exception as e2:
            console.print(f"[red]Error:[/red] {e2}")
            sys.exit(1)
    else:
        # Call the existing script
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:
            task = progress.add_task("Starting services...", total=None)

            try:
                result = subprocess.run(
                    [sys.executable, str(fl_start_script)],
                    cwd=project_root,
                    check=False,
                )
                progress.update(task, completed=True)

                if result.returncode == 0:
                    console.print(
                        Panel.fit(
                            f"[green]✓[/green] Dashboard running on http://localhost:{port}",
                            title="Success",
                            border_style="green",
                        )
                    )
                else:
                    console.print(
                        Panel.fit(
                            "[red]✗[/red] Failed to start dashboard",
                            title="Error",
                            border_style="red",
                        )
                    )
                    sys.exit(result.returncode)
            except KeyboardInterrupt:
                console.print("\n[yellow]Startup interrupted by user[/yellow]")
                sys.exit(130)
