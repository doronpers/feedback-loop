"""
Integration Module

Orchestrates the metrics collection and pattern-aware code generation system.
Provides CLI interface for all system operations.
"""

import argparse
import json
import logging
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional

from metrics.collector import MetricsCollector
from metrics.analyzer import MetricsAnalyzer
from metrics.pattern_manager import PatternManager
from metrics.code_generator import PatternAwareGenerator

logger = logging.getLogger(__name__)


class MetricsIntegration:
    """Orchestrates the metrics collection and analysis system."""
    
    def __init__(
        self,
        metrics_file: str = "metrics_data.json",
        patterns_file: str = "patterns.json",
        ai_patterns_md: str = "AI_PATTERNS.md"
    ):
        """Initialize the integration system.
        
        Args:
            metrics_file: Path to store collected metrics
            patterns_file: Path to pattern library JSON
            ai_patterns_md: Path to AI_PATTERNS.md file
        """
        self.metrics_file = metrics_file
        self.patterns_file = patterns_file
        self.ai_patterns_md = ai_patterns_md
        
        self.collector = MetricsCollector()
        self.pattern_manager = PatternManager(patterns_file)
    
    def collect_metrics(self) -> None:
        """Collect and save current metrics."""
        logger.debug("Starting metrics collection")
        
        # Load existing metrics if available
        if Path(self.metrics_file).exists():
            try:
                with open(self.metrics_file, 'r') as f:
                    existing_data = json.load(f)
                    self.collector.data = existing_data
                logger.debug(f"Loaded existing metrics from {self.metrics_file}")
            except (json.JSONDecodeError, IOError) as e:
                logger.debug(f"Could not load existing metrics: {e}")
        
        # Save metrics
        with open(self.metrics_file, 'w') as f:
            f.write(self.collector.export_json())
        
        summary = self.collector.get_summary()
        print(f"✓ Metrics collected and saved to {self.metrics_file}")
        print(f"  Total entries: {summary['total']}")
        print(f"  - Bugs: {summary['bugs']}")
        print(f"  - Test failures: {summary['test_failures']}")
        print(f"  - Code reviews: {summary['code_reviews']}")
        print(f"  - Performance metrics: {summary['performance_metrics']}")
        print(f"  - Deployment issues: {summary['deployment_issues']}")
    
    def analyze_metrics(self, update_patterns: bool = True) -> None:
        """Analyze metrics and optionally update pattern library.
        
        Args:
            update_patterns: Whether to update pattern library based on analysis
        """
        logger.debug("Starting metrics analysis")
        
        # Load metrics
        if not Path(self.metrics_file).exists():
            print(f"✗ Metrics file not found: {self.metrics_file}")
            print("  Run 'collect' command first")
            return
        
        with open(self.metrics_file, 'r') as f:
            metrics_data = json.load(f)
        
        # Analyze
        analyzer = MetricsAnalyzer(metrics_data)
        
        # Get high frequency patterns
        high_freq = analyzer.get_high_frequency_patterns(threshold=1)
        print(f"\n✓ High Frequency Patterns: {len(high_freq)}")
        for pattern in high_freq[:10]:
            print(f"  - {pattern['pattern']}: {pattern['count']} occurrences")
        
        # Detect new patterns
        known_patterns = self.pattern_manager.get_pattern_names()
        new_patterns = analyzer.detect_new_patterns(known_patterns)
        print(f"\n✓ New Patterns Detected: {len(new_patterns)}")
        for pattern in new_patterns[:5]:
            print(f"  - {pattern['pattern']}: {pattern['count']} occurrences")
        
        # Calculate effectiveness
        effectiveness = analyzer.calculate_effectiveness()
        print(f"\n✓ Pattern Effectiveness:")
        for pattern, metrics in list(effectiveness.items())[:5]:
            print(f"  - {pattern}: {metrics['score']:.2%} ({metrics['trend']})")
        
        # Rank by severity
        ranked = analyzer.rank_patterns_by_severity()
        print(f"\n✓ Patterns Ranked by Severity:")
        for item in ranked[:5]:
            print(f"  - {item['pattern']}: {item['severity']} (count: {item['count']})")
        
        # Update patterns if requested
        if update_patterns:
            print("\n✓ Updating pattern library...")
            
            # Update frequencies
            self.pattern_manager.update_frequencies(high_freq)
            
            # Add new patterns
            self.pattern_manager.add_new_patterns(new_patterns)
            
            # Archive unused patterns
            archived = self.pattern_manager.archive_unused_patterns(days=90)
            if archived:
                print(f"  Archived {len(archived)} unused patterns")
            
            # Save patterns
            self.pattern_manager.save_patterns()
            print(f"  Pattern library saved to {self.patterns_file}")
    
    def generate_code(
        self,
        prompt: str,
        output_file: Optional[str] = None,
        apply_patterns: bool = True,
        min_confidence: float = 0.8
    ) -> None:
        """Generate pattern-aware code.
        
        Args:
            prompt: User prompt for code generation
            output_file: Optional file to save generated code
            apply_patterns: Whether to apply patterns automatically
            min_confidence: Minimum confidence score to apply patterns
        """
        logger.debug(f"Generating code for: {prompt}")
        
        # Load metrics context if available
        metrics_context = None
        if Path(self.metrics_file).exists():
            with open(self.metrics_file, 'r') as f:
                metrics_data = json.load(f)
            analyzer = MetricsAnalyzer(metrics_data)
            metrics_context = analyzer.get_context()
        
        # Load patterns
        if not self.pattern_manager.patterns:
            # Try to load from AI_PATTERNS.md
            if Path(self.ai_patterns_md).exists():
                self.pattern_manager.load_from_ai_patterns_md(self.ai_patterns_md)
                self.pattern_manager.save_patterns()
        
        # Generate code
        generator = PatternAwareGenerator(
            self.pattern_manager.get_all_patterns(),
            pattern_library_version="1.0.0"
        )
        
        result = generator.generate(
            prompt=prompt,
            metrics_context=metrics_context,
            apply_patterns=apply_patterns,
            min_confidence=min_confidence
        )
        
        # Print results
        print("\n" + "="*60)
        print("GENERATED CODE:")
        print("="*60)
        print(result.code)
        print("\n" + "="*60)
        print("REPORT:")
        print("="*60)
        print(result.report)
        
        # Save to file if requested
        if output_file:
            with open(output_file, 'w') as f:
                f.write(result.code)
            print(f"\n✓ Code saved to {output_file}")
        
        # Save metadata
        metadata_file = output_file + ".meta.json" if output_file else "generated_code.meta.json"
        with open(metadata_file, 'w') as f:
            json.dump({
                "metadata": result.metadata,
                "patterns_applied": result.patterns_applied,
                "patterns_suggested": result.patterns_suggested,
                "confidence": float(result.confidence)
            }, f, indent=2)
        print(f"✓ Metadata saved to {metadata_file}")
    
    def generate_report(self, period: str = "all", output_file: Optional[str] = None) -> None:
        """Generate analysis report.
        
        Args:
            period: Time period for report (all/month/week)
            output_file: Optional file to save report
        """
        logger.debug(f"Generating {period} report")
        
        # Load metrics
        if not Path(self.metrics_file).exists():
            print(f"✗ Metrics file not found: {self.metrics_file}")
            return
        
        with open(self.metrics_file, 'r') as f:
            metrics_data = json.load(f)
        
        # Analyze
        analyzer = MetricsAnalyzer(metrics_data)
        report = analyzer.generate_report()
        
        # Format report
        report_text = self._format_report(report, period)
        
        # Print report
        print("\n" + report_text)
        
        # Save to file if requested
        if output_file:
            with open(output_file, 'w') as f:
                f.write(report_text)
            print(f"\n✓ Report saved to {output_file}")
    
    def _format_report(self, report: dict, period: str) -> str:
        """Format report for display.
        
        Args:
            report: Report dictionary
            period: Time period
            
        Returns:
            Formatted report string
        """
        lines = [
            "="*60,
            f"METRICS ANALYSIS REPORT - {period.upper()}",
            f"Generated: {report['generated_at']}",
            "="*60,
            "",
            "SUMMARY:",
            f"  Total Bugs: {report['summary']['total_bugs']}",
            f"  Total Test Failures: {report['summary']['total_test_failures']}",
            f"  Total Code Reviews: {report['summary']['total_code_reviews']}",
            f"  Total Performance Metrics: {report['summary']['total_performance_metrics']}",
            f"  Total Deployment Issues: {report['summary']['total_deployment_issues']}",
            "",
            f"HIGH FREQUENCY PATTERNS: {len(report['high_frequency_patterns'])}",
        ]
        
        for pattern in report['high_frequency_patterns'][:10]:
            lines.append(f"  - {pattern['pattern']}: {pattern['count']} occurrences")
        
        lines.append("")
        lines.append(f"PATTERNS RANKED BY SEVERITY: {len(report['ranked_patterns'])}")
        
        for pattern in report['ranked_patterns'][:10]:
            lines.append(f"  - {pattern['pattern']}: {pattern['severity']} (count: {pattern['count']})")
        
        lines.append("")
        lines.append("="*60)
        
        return "\n".join(lines)


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Metrics Collection and Pattern-Aware Code Generation System"
    )
    
    subparsers = parser.add_subparsers(dest="command", help="Command to execute")
    
    # Collect command
    collect_parser = subparsers.add_parser("collect", help="Collect current metrics")
    collect_parser.add_argument(
        "--metrics-file",
        default="metrics_data.json",
        help="Path to metrics file (default: metrics_data.json)"
    )
    
    # Analyze command
    analyze_parser = subparsers.add_parser("analyze", help="Analyze metrics and update patterns")
    analyze_parser.add_argument(
        "--metrics-file",
        default="metrics_data.json",
        help="Path to metrics file (default: metrics_data.json)"
    )
    analyze_parser.add_argument(
        "--patterns-file",
        default="patterns.json",
        help="Path to patterns file (default: patterns.json)"
    )
    analyze_parser.add_argument(
        "--no-update",
        action="store_true",
        help="Don't update pattern library"
    )
    
    # Generate command
    generate_parser = subparsers.add_parser("generate", help="Generate pattern-aware code")
    generate_parser.add_argument(
        "prompt",
        help="Prompt for code generation"
    )
    generate_parser.add_argument(
        "--output",
        help="Output file for generated code"
    )
    generate_parser.add_argument(
        "--no-apply",
        action="store_true",
        help="Don't apply patterns automatically"
    )
    generate_parser.add_argument(
        "--min-confidence",
        type=float,
        default=0.8,
        help="Minimum confidence to apply patterns (default: 0.8)"
    )
    generate_parser.add_argument(
        "--metrics-file",
        default="metrics_data.json",
        help="Path to metrics file (default: metrics_data.json)"
    )
    generate_parser.add_argument(
        "--patterns-file",
        default="patterns.json",
        help="Path to patterns file (default: patterns.json)"
    )
    
    # Report command
    report_parser = subparsers.add_parser("report", help="Generate analysis report")
    report_parser.add_argument(
        "--period",
        choices=["all", "month", "week"],
        default="all",
        help="Time period for report (default: all)"
    )
    report_parser.add_argument(
        "--output",
        help="Output file for report"
    )
    report_parser.add_argument(
        "--metrics-file",
        default="metrics_data.json",
        help="Path to metrics file (default: metrics_data.json)"
    )
    
    args = parser.parse_args()
    
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    if not args.command:
        parser.print_help()
        return 1
    
    try:
        if args.command == "collect":
            integration = MetricsIntegration(metrics_file=args.metrics_file)
            integration.collect_metrics()
        
        elif args.command == "analyze":
            integration = MetricsIntegration(
                metrics_file=args.metrics_file,
                patterns_file=args.patterns_file
            )
            integration.analyze_metrics(update_patterns=not args.no_update)
        
        elif args.command == "generate":
            integration = MetricsIntegration(
                metrics_file=args.metrics_file,
                patterns_file=args.patterns_file
            )
            integration.generate_code(
                prompt=args.prompt,
                output_file=args.output,
                apply_patterns=not args.no_apply,
                min_confidence=args.min_confidence
            )
        
        elif args.command == "report":
            integration = MetricsIntegration(metrics_file=args.metrics_file)
            integration.generate_report(
                period=args.period,
                output_file=args.output
            )
        
        return 0
    
    except Exception as e:
        print(f"✗ Error: {e}", file=sys.stderr)
        logger.exception("Command failed")
        return 1


if __name__ == "__main__":
    sys.exit(main())
