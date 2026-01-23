"""
Review Command

Review code with pattern awareness.
"""

import sys
from pathlib import Path
from typing import List, Optional

import click
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

# Add project root to path
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))


@click.command()
@click.argument("file_path", type=click.Path(exists=True), required=False)
@click.option("--pattern", "-p", help="Check specific pattern")
@click.option("--fix", is_flag=True, help="Show suggested fixes")
@click.pass_context
def review(ctx, file_path, pattern, fix):
    """👁️ Review code with patterns.

    Review code files for pattern violations and suggest improvements.

    Examples:

      \b
      # Review a file
      feedback-loop review path/to/file.py

      \b
      # Review with specific pattern
      feedback-loop review path/to/file.py --pattern numpy_type_conversion

      \b
      # Review and show fixes
      feedback-loop review path/to/file.py --fix
    """
    console = ctx.obj.get("console", Console())

    if not file_path:
        console.print("[red]Error:[/red] Please provide a file path to review")
        console.print("[cyan]Usage: feedback-loop review <file_path>[/cyan]")
        sys.exit(1)

    file_path = Path(file_path)

    if not file_path.exists():
        # Use error recovery if available
        try:
            from shared_ai_utils.errors import ErrorRecovery

            recovery = ErrorRecovery("FileNotFoundError", {"path": str(file_path)})
            console.print(f"[red]Error:[/red] File not found: {file_path}")
            console.print("\n[bold yellow]💡 Recovery Steps:[/bold yellow]")
            for i, step in enumerate(recovery.get_steps()[:3], 1):
                console.print(f"  {i}. {step.description}")
                if step.command:
                    console.print(f"     [dim]Run: {step.command}[/dim]")
        except ImportError:
            console.print(f"[red]Error:[/red] File not found: {file_path}")
            console.print("[yellow]Tip:[/yellow] Check the file path and try again")
        sys.exit(1)

    if not file_path.is_file():
        console.print(f"[red]Error:[/red] Path is not a file: {file_path}")
        console.print("[yellow]Tip:[/yellow] Provide a file path, not a directory")
        sys.exit(1)

    # Read file content
    try:
        code_content = file_path.read_text()
    except PermissionError as e:
        try:
            from shared_ai_utils.errors import ErrorRecovery

            recovery = ErrorRecovery("PermissionError", {"path": str(file_path)})
            console.print(f"[red]Error:[/red] Permission denied: {file_path}")
            console.print("\n[bold yellow]💡 Recovery Steps:[/bold yellow]")
            for i, step in enumerate(recovery.get_steps()[:3], 1):
                console.print(f"  {i}. {step.description}")
        except ImportError:
            console.print(f"[red]Error:[/red] Permission denied: {file_path}")
        sys.exit(1)
    except Exception as e:
        try:
            from shared_ai_utils.errors import ErrorRecovery

            recovery = ErrorRecovery(type(e).__name__, {"path": str(file_path), "error": str(e)})
            console.print(f"[red]Error reading file: {e}[/red]")
            console.print("\n[bold yellow]💡 Recovery Steps:[/bold yellow]")
            for i, step in enumerate(recovery.get_steps()[:2], 1):
                console.print(f"  {i}. {step.description}")
        except ImportError:
            console.print(f"[red]Error reading file: {e}[/red]")
        sys.exit(1)

    # Try to use shared-ai-utils pattern checks
    try:
        from shared_ai_utils.assessment.pattern_checks import (
            detect_pattern_violations,
            violations_to_metadata,
        )

        console.print(f"[cyan]Reviewing: {file_path}[/cyan]\n")

        # Detect violations
        violations = detect_pattern_violations(code_content, file_path=str(file_path))

        # Filter by pattern if specified
        if pattern:
            violations = [v for v in violations if v.pattern_name == pattern]

        if not violations:
            console.print("[green]✓[/green] No pattern violations found!")
            return

        # Display violations
        console.print(f"[yellow]Found {len(violations)} pattern violation(s)[/yellow]\n")

        table = Table(show_header=True, header_style="bold magenta")
        table.add_column("Pattern", style="cyan")
        table.add_column("Severity", style="yellow")
        table.add_column("Line", style="green")
        table.add_column("Description", style="white")

        for violation in violations:
            severity_icon = {
                "error": "[red]●[/red]",
                "warning": "[yellow]●[/yellow]",
                "info": "[blue]●[/blue]",
            }.get(violation.severity, "○")

            table.add_row(
                violation.pattern_name,
                severity_icon,
                str(violation.line_number) if violation.line_number else "N/A",
                violation.description[:60] + "..." if len(violation.description) > 60 else violation.description,
            )

        console.print(table)

        # Show fixes if requested
        if fix:
            console.print("\n[bold]Suggested Fixes:[/bold]\n")
            for violation in violations:
                console.print(f"[cyan]{violation.pattern_name}[/cyan] (line {violation.line_number})")
                console.print(f"  [dim]{violation.description}[/dim]")
                if violation.suggestion:
                    console.print(f"  [green]Fix:[/green] {violation.suggestion}")
                console.print()

        # Show summary
        error_count = sum(1 for v in violations if v.severity == "error")
        warning_count = sum(1 for v in violations if v.severity == "warning")

        if error_count > 0:
            console.print(f"\n[red]✗ {error_count} error(s) found[/red]")
        if warning_count > 0:
            console.print(f"[yellow]⚠ {warning_count} warning(s) found[/yellow]")

    except ImportError:
        # Fallback: try to use local pattern checks
        console.print("[yellow]shared-ai-utils not available, using basic review[/yellow]")
        console.print(f"[cyan]Reviewing: {file_path}[/cyan]")

        # Basic file checks
        issues: List[str] = []

        # Check for common issues
        if "except:" in code_content:
            issues.append("Bare except clause found (use specific exceptions)")

        if "print(" in code_content and "logger" not in code_content:
            issues.append("print() statements found (use logging instead)")

        if issues:
            console.print(f"\n[yellow]Found {len(issues)} potential issue(s):[/yellow]\n")
            for issue in issues:
                console.print(f"  • {issue}")
        else:
            console.print("[green]✓[/green] No obvious issues found")

        console.print("\n[yellow]Tip:[/yellow] Install shared-ai-utils for comprehensive pattern checking")
        console.print("[dim]Run: pip install shared-ai-utils[/dim]")
