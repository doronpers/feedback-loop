"""
Feedback Loop Unified CLI

Single entry point for all feedback-loop commands.
"""

import sys
from pathlib import Path

# Add project root to path for imports
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))

# Load .env file from project root
try:
    from metrics.env_loader import load_env_file
    load_env_file(project_root)
except ImportError:
    pass  # env_loader may not be available in all contexts

import click
from rich.console import Console
from rich.table import Table

console = Console()


@click.group(invoke_without_command=True)
@click.version_option(version="1.0.0", prog_name="feedback-loop")
@click.option("--verbose", "-v", is_flag=True, help="Enable verbose output")
@click.option("--quiet", "-q", is_flag=True, help="Suppress non-essential output")
@click.pass_context
def cli(ctx, verbose, quiet):
    """Feedback Loop - AI-Assisted Development Framework

    Learn from test failures, build pattern libraries, and improve AI code generation.
    """
    # Ensure context object exists
    ctx.ensure_object(dict)
    ctx.obj["verbose"] = verbose
    ctx.obj["quiet"] = quiet
    ctx.obj["console"] = console

    # If no command provided, show help
    if ctx.invoked_subcommand is None:
        show_command_help(console)


def show_command_help(console_instance: Console):
    """Show interactive help for commands."""
    console_instance.print("\n[bold cyan]Feedback Loop CLI[/bold cyan]\n")

    table = Table(title="Available Commands", show_header=True, header_style="bold magenta")
    table.add_column("Command", style="cyan", no_wrap=True)
    table.add_column("Aliases", style="dim")
    table.add_column("Description", style="green")

    commands = [
        ("start", "s, launch", "Start dashboard and services"),
        ("chat", "c, ask", "Interactive AI chat assistant"),
        ("dashboard", "dash, d", "Open analytics dashboard"),
        ("review", "r, check", "Review code with patterns"),
        ("analyze", "a, metrics", "Analyze test failures and patterns"),
        ("patterns", "p, list-patterns", "List and manage patterns"),
        ("config", "cfg, settings", "Manage configuration"),
        ("doctor", "diagnose", "Run diagnostics and health checks"),
        ("demo", "example", "Run interactive demo"),
    ]

    for cmd, aliases, desc in commands:
        table.add_row(cmd, aliases, desc)

    console_instance.print(table)
    console_instance.print(
        "\n[yellow]Tip:[/yellow] Use [cyan]feedback-loop <command> --help[/cyan] for detailed help\n"
    )


# Import subcommands (lazy loading to avoid circular imports)
def _register_commands():
    """Register all CLI subcommands."""
    # Try both relative and absolute imports to work as package or script
    def _import_command(module_name, command_name):
        """Try to import a command using relative or absolute import."""
        # Try absolute import first (works when running as script or installed package)
        try:
            module = __import__(f"feedback_loop.cli.commands.{module_name}", fromlist=[command_name])
            return getattr(module, command_name)
        except (ImportError, AttributeError):
            # Try relative import (works when installed as package)
            try:
                from importlib import import_module
                module = import_module(f".commands.{module_name}", package="feedback_loop.cli")
                return getattr(module, command_name)
            except (ImportError, AttributeError):
                return None

    commands = [
        ("start", "start"),
        ("chat", "chat"),
        ("dashboard", "dashboard"),
        ("doctor", "doctor"),
        ("review", "review"),
        ("analyze", "analyze"),
        ("patterns", "patterns"),
        ("config", "config"),
        ("demo", "demo"),
    ]

    for module_name, command_name in commands:
        cmd = _import_command(module_name, command_name)
        if cmd:
            cli.add_command(cmd)


# Register commands after cli group and helper functions are defined
_register_commands()


if __name__ == "__main__":
    cli()
