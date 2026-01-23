"""
Config Command

Manage configuration.
"""

import os
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
@click.option("--set", "set_key", help="Set configuration (format: FL_KEY=value)")
@click.option("--env-file", type=click.Path(), help="Path to .env file to update")
@click.pass_context
def config(ctx, show, set_key, env_file):
    """⚙️ Manage configuration.

    View and modify feedback-loop configuration.

    Configuration is managed via environment variables with FL_ prefix.
    Use --set to show how to set values (actual setting requires .env file or export).

    Examples:

      \b
      # Show current config
      feedback-loop config --show

      \b
      # Show how to set a config value
      feedback-loop config --set FL_API_PORT=8080

      \b
      # Update .env file
      feedback-loop config --set FL_API_PORT=8080 --env-file .env
    """
    console = ctx.obj.get("console", Console())

    if set_key:
        # Parse key=value
        if "=" not in set_key:
            console.print("[red]Error:[/red] Use format FL_KEY=value")
            console.print("[dim]Example: FL_API_PORT=8080[/dim]")
            sys.exit(1)

        key, value = set_key.split("=", 1)

        # Validate key format
        if not key.startswith("FL_"):
            console.print(f"[yellow]Warning:[/yellow] Key should start with FL_ prefix")
            console.print(f"[dim]Did you mean FL_{key}?[/dim]")

        # Show current value if exists
        current_value = os.getenv(key)
        if current_value:
            console.print(f"[dim]Current value: {current_value}[/dim]")

        # Update .env file if provided
        if env_file:
            env_path = Path(env_file)
            if not env_path.exists():
                console.print(f"[yellow]Creating .env file: {env_path}[/yellow]")
                env_path.parent.mkdir(parents=True, exist_ok=True)
                env_path.write_text("")

            # Read existing .env
            env_content = env_path.read_text()
            lines = env_content.split("\n")

            # Update or add the key
            updated = False
            for i, line in enumerate(lines):
                if line.startswith(f"{key}="):
                    lines[i] = f"{key}={value}"
                    updated = True
                    break

            if not updated:
                lines.append(f"{key}={value}")

            # Write back
            env_path.write_text("\n".join(lines))
            console.print(f"[green]✓[/green] Updated {env_path}")
            console.print(f"[green]✓[/green] Set {key} = {value}")
        else:
            # Just show how to set it
            console.print(f"[cyan]To set this value, run:[/cyan]")
            console.print(f"  [bold]export {key}={value}[/bold]")
            console.print(f"\n[dim]Or add to your .env file:[/dim]")
            console.print(f"  [bold]{key}={value}[/bold]")
            console.print(f"\n[yellow]Tip:[/yellow] Use --env-file .env to update .env automatically")

    elif show:
        # Show configuration
        console.print("[bold cyan]Current Configuration[/bold cyan]\n")

        try:
            from feedback_loop.config import get_config

            cfg = get_config()

            table = Table(show_header=True, header_style="bold magenta")
            table.add_column("Category", style="cyan")
            table.add_column("Key", style="yellow")
            table.add_column("Value", style="green")
            table.add_column("Source", style="dim")

            # Database config
            table.add_row(
                "Database",
                "Type",
                cfg.database.type.value,
                "FL_DB_TYPE" if os.getenv("FL_DB_TYPE") else "default",
            )
            table.add_row(
                "Database",
                "URI",
                cfg.database.uri or "(auto-generated)",
                "FL_DB_URI" if os.getenv("FL_DB_URI") else "default",
            )
            table.add_row(
                "Database",
                "Auto Migrate",
                str(cfg.database.auto_migrate),
                "FL_DB_AUTO_MIGRATE" if os.getenv("FL_DB_AUTO_MIGRATE") else "default",
            )

            # API config
            table.add_row(
                "API",
                "Host",
                cfg.api.host,
                "FL_API_HOST" if os.getenv("FL_API_HOST") else "default",
            )
            table.add_row(
                "API",
                "Port",
                str(cfg.api.port),
                "FL_API_PORT" if os.getenv("FL_API_PORT") else "default",
            )
            table.add_row(
                "API",
                "Debug",
                str(cfg.api.debug),
                "FL_API_DEBUG" if os.getenv("FL_API_DEBUG") else "default",
            )

            # LLM config
            table.add_row(
                "LLM",
                "Provider",
                cfg.llm.provider.value,
                "FL_LLM_PROVIDER" if os.getenv("FL_LLM_PROVIDER") else "default",
            )
            table.add_row(
                "LLM",
                "Model",
                cfg.llm.model,
                "FL_LLM_MODEL" if os.getenv("FL_LLM_MODEL") else "default",
            )

            # Metrics
            table.add_row(
                "Metrics",
                "Enabled",
                str(cfg.metrics_enabled),
                "FL_METRICS_ENABLED" if os.getenv("FL_METRICS_ENABLED") else "default",
            )

            console.print(table)
            console.print("\n[dim]Note: Configuration is loaded from environment variables with FL_ prefix[/dim]")
            console.print("[dim]Use --set FL_KEY=value to see how to set values[/dim]")

        except Exception as e:
            try:
                from shared_ai_utils.errors import ErrorRecovery

                recovery = ErrorRecovery(type(e).__name__, {"error": str(e), "context": "config_loading"})
                console.print(f"[red]Error loading config: {e}[/red]")
                console.print("[yellow]Using default configuration[/yellow]")
                console.print("\n[bold yellow]💡 Recovery Steps:[/bold yellow]")
                for i, step in enumerate(recovery.get_steps()[:2], 1):
                    console.print(f"  {i}. {step.description}")
            except ImportError:
                console.print(f"[red]Error loading config: {e}[/red]")
                console.print("[yellow]Using default configuration[/yellow]")
            sys.exit(1)
    else:
        # Show help
        console.print("[cyan]Use --show to view config or --set FL_KEY=value to modify[/cyan]")
        console.print("[dim]Example: feedback-loop config --set FL_API_PORT=8080[/dim]")
