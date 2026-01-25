"""
Chat Command

Interactive AI chat assistant.
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
def chat(ctx):
    """💬 Interactive AI chat assistant.

    Chat with AI about patterns, code generation, and feedback-loop usage.

    Examples:

      \b
      # Start chat session
      feedback-loop chat
    """
    console = ctx.obj.get("console", Console())

    # Import and run the existing fl-chat
    try:
        sys.path.insert(0, str(project_root / "bin"))
        from fl_chat import main as chat_main

        chat_main()
    except ImportError:
        console.print("[red]Error:[/red] Chat command not available")
        console.print("[yellow]Please ensure fl-chat is available in bin/[/yellow]")
        sys.exit(1)
