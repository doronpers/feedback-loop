"""
Analyze Command

Analyze test failures and patterns.
"""

import json
import sys
from pathlib import Path
from typing import Dict, List, Optional

import click
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

# Add project root to path
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))


@click.command()
@click.option("--metrics-file", type=click.Path(exists=True), help="Path to metrics JSON file")
@click.option("--output", type=click.Path(), help="Save analysis results to file")
@click.option("--format", type=click.Choice(["table", "json"]), default="table", help="Output format")
@click.pass_context
def analyze(ctx, metrics_file, output, format):
    """📊 Analyze test failures and patterns.

    Analyze collected metrics and update the pattern library.

    Examples:

      \b
      # Analyze default metrics
      feedback-loop analyze

      \b
      # Analyze specific metrics file
      feedback-loop analyze --metrics-file data/custom_metrics.json

      \b
      # Save analysis results
      feedback-loop analyze --output analysis.json --format json
    """
    console = ctx.obj.get("console", Console())

    console.print("[cyan]Analyzing metrics and patterns...[/cyan]\n")

    # Try to use shared-ai-utils metrics and insights
    try:
        from shared_ai_utils.metrics import MetricsCollector
        from shared_ai_utils.insights import InsightsEngine

        # Load metrics
        collector = MetricsCollector()

        if metrics_file:
            metrics_path = Path(metrics_file)
            if metrics_path.exists():
                try:
                    collector.import_from_json(str(metrics_path))
                    console.print(f"[green]✓[/green] Loaded metrics from {metrics_path}")
                except Exception as e:
                    try:
                        from shared_ai_utils.errors import ErrorRecovery

                        recovery = ErrorRecovery(type(e).__name__, {"path": str(metrics_path), "error": str(e)})
                        console.print(f"[red]Error loading metrics: {e}[/red]")
                        console.print("\n[bold yellow]💡 Recovery Steps:[/bold yellow]")
                        for i, step in enumerate(recovery.get_steps()[:2], 1):
                            console.print(f"  {i}. {step.description}")
                    except ImportError:
                        console.print(f"[red]Error loading metrics: {e}[/red]")
                    sys.exit(1)
            else:
                console.print(f"[red]Metrics file not found: {metrics_path}[/red]")
                sys.exit(1)
        else:
            # Try to find default metrics file
            default_metrics = project_root / "data" / "metrics.json"
            if default_metrics.exists():
                try:
                    collector.import_from_json(str(default_metrics))
                    console.print(f"[green]✓[/green] Loaded metrics from {default_metrics}")
                except Exception:
                    console.print("[yellow]Could not load default metrics file[/yellow]")
            else:
                console.print("[yellow]No metrics file specified and default not found[/yellow]")
                console.print("[dim]Run tests with --enable-metrics to collect data[/dim]")

        # Analyze with insights engine
        insights = InsightsEngine(collector)
        analysis = insights.analyze_patterns()

        # Display results
        if format == "json":
            results = {
                "summary": analysis.get("summary", {}),
                "patterns": analysis.get("patterns", []),
                "recommendations": analysis.get("recommendations", []),
            }
            output_text = json.dumps(results, indent=2)

            if output:
                Path(output).write_text(output_text)
                console.print(f"[green]✓[/green] Saved analysis to {output}")
            else:
                console.print(output_text)
        else:
            # Table format
            console.print("[bold]Analysis Summary[/bold]\n")

            # Pattern frequency table
            if "patterns" in analysis and analysis["patterns"]:
                table = Table(show_header=True, header_style="bold magenta")
                table.add_column("Pattern", style="cyan")
                table.add_column("Frequency", style="green")
                table.add_column("Severity", style="yellow")
                table.add_column("Trend", style="dim")

                for pattern in analysis["patterns"][:10]:  # Top 10
                    table.add_row(
                        pattern.get("name", "Unknown"),
                        str(pattern.get("count", 0)),
                        pattern.get("severity", "info"),
                        pattern.get("trend", "stable"),
                    )

                console.print(table)

            # Recommendations
            if "recommendations" in analysis and analysis["recommendations"]:
                console.print("\n[bold]Recommendations:[/bold]\n")
                for i, rec in enumerate(analysis["recommendations"][:5], 1):
                    console.print(f"  {i}. {rec}")

            # Summary stats
            if "summary" in analysis:
                summary = analysis["summary"]
                console.print("\n[bold]Summary Statistics:[/bold]\n")
                console.print(f"  Total Metrics: {summary.get('total_metrics', 0)}")
                console.print(f"  Patterns Detected: {summary.get('patterns_detected', 0)}")
                console.print(f"  Error Rate: {summary.get('error_rate', 0):.1%}")

            if output:
                # Save as JSON even if displaying as table
                results = {
                    "summary": analysis.get("summary", {}),
                    "patterns": analysis.get("patterns", []),
                    "recommendations": analysis.get("recommendations", []),
                }
                Path(output).write_text(json.dumps(results, indent=2))
                console.print(f"\n[green]✓[/green] Saved analysis to {output}")

    except ImportError:
        # Fallback: basic analysis
        console.print("[yellow]shared-ai-utils not available, using basic analysis[/yellow]")

        if metrics_file:
            metrics_path = Path(metrics_file)
            if metrics_path.exists():
                try:
                    with open(metrics_path) as f:
                        metrics_data = json.load(f)

                    console.print(f"[green]✓[/green] Loaded {len(metrics_data)} metric(s)")

                    # Basic analysis
                    error_count = sum(1 for m in metrics_data if m.get("type") == "error")
                    pattern_count = sum(1 for m in metrics_data if "pattern" in m.get("type", ""))

                    console.print(f"\n[bold]Basic Analysis:[/bold]")
                    console.print(f"  Errors: {error_count}")
                    console.print(f"  Pattern Violations: {pattern_count}")

                    if output:
                        results = {
                            "errors": error_count,
                            "pattern_violations": pattern_count,
                            "total_metrics": len(metrics_data),
                        }
                        Path(output).write_text(json.dumps(results, indent=2))
                        console.print(f"\n[green]✓[/green] Saved analysis to {output}")

                except Exception as e:
                    try:
                        from shared_ai_utils.errors import ErrorRecovery

                        recovery = ErrorRecovery(type(e).__name__, {"error": str(e), "context": "metrics_analysis"})
                        console.print(f"[red]Error analyzing metrics: {e}[/red]")
                        console.print("\n[bold yellow]💡 Recovery Steps:[/bold yellow]")
                        for i, step in enumerate(recovery.get_steps()[:2], 1):
                            console.print(f"  {i}. {step.description}")
                    except ImportError:
                        console.print(f"[red]Error analyzing metrics: {e}[/red]")
                    sys.exit(1)
            else:
                console.print(f"[red]Metrics file not found: {metrics_path}[/red]")
                sys.exit(1)
        else:
            console.print("[yellow]No metrics file specified[/yellow]")
            console.print("[dim]Tip: Install shared-ai-utils for advanced analysis[/dim]")
            console.print("[dim]Run: pip install shared-ai-utils[/dim]")
