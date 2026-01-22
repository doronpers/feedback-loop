"""
Review Command

Review code with pattern awareness.
"""

import sys
from pathlib import Path

import click
from rich.console import Console

# Add project root to path
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))


@click.command()
@click.argument("file_path", type=click.Path(exists=True), required=False)
@click.option("--pattern", "-p", help="Check specific pattern")
@click.pass_context
def review(ctx, file_path, pattern):
    """👁️ Review code with patterns.

    Review code files for pattern violations and suggest improvements.

    Examples:

      \b
      # Review a file
      feedback-loop review path/to/file.py

      \b
      # Review with specific pattern
      feedback-loop review path/to/file.py --pattern numpy_type_conversion
    """
    console = ctx.obj.get("console", Console())

    # Import and run the existing fl-review
    try:
        sys.path.insert(0, str(project_root / "bin"))
        from fl_review import main as review_main

        if file_path:
            sys.argv = ["fl-review", str(file_path)]
            if pattern:
                sys.argv.extend(["--pattern", pattern])
        review_main()
    except ImportError:
        console.print("[yellow]Review command not yet fully implemented[/yellow]")
        if file_path:
            console.print(f"[cyan]Would review:[/cyan] {file_path}")
        if pattern:
            console.print(f"[cyan]Pattern filter:[/cyan] {pattern}")
