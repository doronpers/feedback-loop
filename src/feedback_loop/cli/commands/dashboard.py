"""
Dashboard Command

Open or manage the analytics dashboard.
"""

import sys
import webbrowser
from pathlib import Path

import click
from rich.console import Console
from rich.panel import Panel

# Add project root to path
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))


@click.command()
@click.option("--port", default=8000, type=int, help="Port for dashboard server")
@click.option("--open/--no-open", default=True, help="Open dashboard in browser")
@click.pass_context
def dashboard(ctx, port, open):
    open_browser = open  # Rename for clarity
    """📊 Open analytics dashboard.

    Opens the feedback-loop analytics dashboard in your browser.

    Examples:

      \b
      # Open dashboard (default)
      feedback-loop dashboard

      \b
      # Open dashboard on custom port
      feedback-loop dashboard --port 8080

      \b
      # Get dashboard URL without opening
      feedback-loop dashboard --no-open
    """
    console = ctx.obj.get("console", Console())

    url = f"http://localhost:{port}/dashboard/"

    if open_browser:
        console.print(f"[cyan]Opening dashboard at {url}...[/cyan]")
        try:
            webbrowser.open(url)
            console.print(Panel.fit("[green]✓[/green] Dashboard opened in browser", border_style="green"))
        except Exception as e:
            console.print(f"[yellow]Warning:[/yellow] Could not open browser: {e}")
            console.print(f"[cyan]Please open:[/cyan] {url}")
    else:
        console.print(Panel.fit(f"[cyan]Dashboard URL:[/cyan] {url}", border_style="cyan"))
