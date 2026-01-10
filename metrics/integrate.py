"""
Integration Module

Orchestrates the metrics collection and pattern-aware code generation system.
Provides CLI interface for all system operations.
"""

import argparse
import json
import logging
import os
import re
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

# Load .env file from project root
project_root = Path(__file__).parent.parent
from metrics.env_loader import load_env_file

load_env_file(project_root)

from metrics.analyzer import MetricsAnalyzer
from metrics.code_generator import PatternAwareGenerator
from metrics.collector import MetricsCollector
from metrics.pattern_manager import PatternManager
from metrics.sync_client import LocalSyncClient, SyncClient
from metrics.synthesizer import CodeSynthesizer

logger = logging.getLogger(__name__)


class MetricsIntegration:
    """Orchestrates the metrics collection and analysis system."""

    def __init__(
        self,
        metrics_file: str = "data/metrics_data.json",
        patterns_file: str = "data/patterns.json",
        ai_patterns_md: str = "docs/AI_PATTERNS_GUIDE.md",
        sync_client: Optional[SyncClient] = None,
    ):
        """Initialize the integration system.

        Args:
            metrics_file: Path to store collected metrics
            patterns_file: Path to pattern library JSON
            ai_patterns_md: Path to AI_PATTERNS_GUIDE.md file
            sync_client: Optional SyncClient for cloud sync (defaults to LocalSyncClient)
        """
        self.metrics_file = metrics_file
        self.patterns_file = patterns_file
        self.ai_patterns_md = ai_patterns_md

        self.collector = MetricsCollector()
        self.pattern_manager = PatternManager(patterns_file)

        # Initialize sync client (defaults to local file system)
        self.sync_client = sync_client or LocalSyncClient(
            patterns_file=patterns_file, metrics_file=metrics_file
        )

    def collect_metrics(self) -> None:
        """Collect and save current metrics."""
        logger.debug("Starting metrics collection")

        # Load existing metrics if available
        if Path(self.metrics_file).exists():
            try:
                with open(self.metrics_file, "r") as f:
                    existing_data = json.load(f)
                    # Validate loaded data structure
                    if not isinstance(existing_data, dict):
                        logger.debug("Invalid metrics data format, starting fresh")
                        existing_data = {}
                    # Validate expected keys using MetricsCollector getter
                    for key in MetricsCollector.get_metric_categories():
                        if key not in existing_data:
                            existing_data[key] = []
                        elif not isinstance(existing_data[key], list):
                            logger.debug(
                                f"Invalid data type for {key}, resetting to empty list"
                            )
                            existing_data[key] = []
                    self.collector.data = existing_data
                logger.debug(f"Loaded existing metrics from {self.metrics_file}")
            except (json.JSONDecodeError, IOError) as e:
                logger.debug(f"Could not load existing metrics: {e}")

        # Save metrics
        with open(self.metrics_file, "w") as f:
            f.write(self.collector.export_json())

        summary = self.collector.get_summary()
        print(f"✓ Metrics collected and saved to {self.metrics_file}")
        print(f"  Total entries: {summary['total']}")
        print(f"  - Bugs: {summary['bugs']}")
        print(f"  - Test failures: {summary['test_failures']}")
        print(f"  - Code reviews: {summary['code_reviews']}")
        print(f"  - Performance metrics: {summary['performance_metrics']}")
        print(f"  - Deployment issues: {summary['deployment_issues']}")
        print(f"  - Code generation: {summary['code_generation']}")

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

        try:
            with open(self.metrics_file, "r") as f:
                metrics_data = json.load(f)

            # Validate metrics data structure
            if not isinstance(metrics_data, dict):
                print(f"✗ Invalid metrics data format in {self.metrics_file}")
                return
        except json.JSONDecodeError as e:
            print(f"✗ Failed to parse metrics file: {e}")
            return

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
        print("\n✓ Pattern Effectiveness:")
        for pattern, metrics in list(effectiveness.items())[:5]:
            print(f"  - {pattern}: {metrics['score']:.2%} ({metrics['trend']})")

        # Rank by severity
        ranked = analyzer.rank_patterns_by_severity()
        print("\n✓ Patterns Ranked by Severity:")
        for item in ranked[:5]:
            print(
                f"  - {item['pattern']}: {item['severity']} "
                f"(count: {item['count']})"
            )

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
        min_confidence: float = 0.8,
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
            with open(self.metrics_file, "r") as f:
                metrics_data = json.load(f)
            analyzer = MetricsAnalyzer(metrics_data)
            metrics_context = analyzer.get_context()

        # Load patterns
        if not self.pattern_manager.patterns:
            # Try to load from AI_PATTERNS_GUIDE.md
            if Path(self.ai_patterns_md).exists():
                self.pattern_manager.load_from_ai_patterns_md(self.ai_patterns_md)
                self.pattern_manager.save_patterns()

        # Generate code
        generator = PatternAwareGenerator(
            self.pattern_manager.get_all_patterns(), pattern_library_version="1.0.0"
        )

        result = generator.generate(
            prompt=prompt,
            metrics_context=metrics_context,
            apply_patterns=apply_patterns,
            min_confidence=min_confidence,
        )

        # Print results
        print("\n" + "=" * 60)
        print("GENERATED CODE:")
        print("=" * 60)
        print(result.code)
        print("\n" + "=" * 60)
        print("REPORT:")
        print("=" * 60)
        print(result.report)

        # Save to file if requested
        if output_file:
            with open(output_file, "w") as f:
                f.write(result.code)
            print(f"\n✓ Code saved to {output_file}")

        # Save metadata
        metadata_file = (
            output_file + ".meta.json" if output_file else "generated_code.meta.json"
        )
        with open(metadata_file, "w") as f:
            json.dump(
                {
                    "metadata": result.metadata,
                    "patterns_applied": result.patterns_applied,
                    "patterns_suggested": result.patterns_suggested,
                    "confidence": float(result.confidence),
                },
                f,
                indent=2,
            )
        print(f"✓ Metadata saved to {metadata_file}")

    def synthesize_code(
        self,
        prompt: str,
        num_candidates: int = 3,
        output_file: Optional[str] = None,
        input_files: Optional[List[str]] = None,
    ) -> None:
        """Synthesize optimal code from multiple candidates.

        Args:
            prompt: User prompt
            num_candidates: Number of candidates to generate (ignored if input_files provided)
            output_file: Optional file to save result
            input_files: Optional list of file paths to use as candidates
        """
        logger.debug(f"Synthesizing code for: {prompt}")

        # Load metrics context
        metrics_context = None
        if Path(self.metrics_file).exists():
            with open(self.metrics_file, "r") as f:
                metrics_data = json.load(f)
            analyzer = MetricsAnalyzer(metrics_data)
            metrics_context = analyzer.get_context()

        # Initialize generator
        if not self.pattern_manager.patterns and Path(self.ai_patterns_md).exists():
            self.pattern_manager.load_from_ai_patterns_md(self.ai_patterns_md)

        generator = PatternAwareGenerator(
            self.pattern_manager.get_all_patterns(), pattern_library_version="1.0.0"
        )

        # Initialize synthesizer
        synthesizer = CodeSynthesizer(generator)

        # Determine input mode
        if input_files:
            print(f"\n🔄 Synthesizing {len(input_files)} provided files...")
            result = synthesizer.synthesize(
                prompt=prompt,
                num_candidates=num_candidates,
                metrics_context=metrics_context,
                input_files=input_files,
            )
        else:
            # Check if we should read from stdin (interactive paste)
            print(f"\n🔄 Generating {num_candidates} candidates...")
            result = synthesizer.synthesize(
                prompt=prompt,
                num_candidates=num_candidates,
                metrics_context=metrics_context,
            )

        # Print Result
        print("\n" + "=" * 60)
        print("SYNTHESIZED CODE:")
        print("=" * 60)
        print(result.final_code)
        print("\n" + "=" * 60)
        print("REPORT:")
        print("=" * 60)
        print(result.report)

        # Save to file
        if output_file:
            with open(output_file, "w") as f:
                f.write(result.final_code)
            print(f"\n✓ Synthesized code saved to {output_file}")

            # Save report
            report_file = output_file + ".report.txt"
            with open(report_file, "w") as f:
                f.write(result.report)
            print(f"✓ Synthesis report saved to {report_file}")

    def generate_report(
        self,
        period: str = "all",
        output_file: Optional[str] = None,
        format: str = "text",
    ) -> None:
        """Generate analysis report.

        Args:
            period: Time period for report (all/month/week)
            output_file: Optional file to save report
            format: Output format (text or markdown)
        """
        logger.debug(f"Generating {period} report")

        # Load metrics
        if not Path(self.metrics_file).exists():
            print(f"✗ Metrics file not found: {self.metrics_file}")
            return

        with open(self.metrics_file, "r") as f:
            metrics_data = json.load(f)

        # Analyze
        analyzer = MetricsAnalyzer(metrics_data)
        report = analyzer.generate_report()

        # Format report
        report_text = self._format_report(report, period, format)

        # Print report
        print("\n" + report_text)

        # Save to file if requested
        if output_file:
            with open(output_file, "w") as f:
                f.write(report_text)
            print(f"\n✓ Report saved to {output_file}")

    def analyze_commit(
        self, base_sha: str, head_sha: str, output_file: Optional[str] = None
    ) -> None:
        """Analyze commit diff for pattern violations.

        Args:
            base_sha: Base commit SHA
            head_sha: Head commit SHA
            output_file: Optional file to save analysis results
        """
        import subprocess

        logger.debug(f"Analyzing commit diff: {base_sha}..{head_sha}")

        try:
            # Get git diff
            result = subprocess.run(
                ["git", "diff", f"{base_sha}..{head_sha}"],
                capture_output=True,
                text=True,
                check=True,
            )
            diff = result.stdout

            # Get changed files
            result = subprocess.run(
                ["git", "diff", "--name-only", f"{base_sha}..{head_sha}"],
                capture_output=True,
                text=True,
                check=True,
            )
            files = result.stdout.strip().split("\n")

            # Analyze for pattern violations
            violations = self._detect_violations(files, diff)

            # Generate report
            analysis = {
                "base_sha": base_sha,
                "head_sha": head_sha,
                "files_changed": len(files),
                "violations": violations,
                "timestamp": datetime.now().isoformat(),
            }

            # Print summary
            print(f"\n✓ Commit Analysis: {base_sha[:8]}..{head_sha[:8]}")
            print(f"  Files changed: {len(files)}")
            print(f"  Pattern violations: {len(violations)}")

            if violations:
                print("\n  Top violations:")
                for v in violations[:5]:
                    print(f"    - {v['file']}:{v.get('line', '?')} - {v['pattern']}")

            # Save to file if requested
            if output_file:
                with open(output_file, "w") as f:
                    json.dump(analysis, f, indent=2)
                print(f"\n✓ Analysis saved to {output_file}")

        except subprocess.CalledProcessError as e:
            print(f"✗ Failed to analyze commit: {e}")
            logger.exception("Commit analysis failed")

    def _detect_violations(self, files: List[str], diff: str) -> List[Dict[str, Any]]:
        """Detect pattern violations in code.

        Args:
            files: List of changed files
            diff: Git diff content

        Returns:
            List of violations
        """
        violations = []

        # Pattern detection rules
        patterns = {
            "numpy_json_serialization": {
                "regex": r"json\.dumps\([^)]*np\.|json\.dumps\([^)]*numpy",
                "description": "NumPy types may not be JSON serializable",
                "suggestion": "Convert NumPy types: float(np_value)",
            },
            "bounds_checking": {
                "regex": r"\w+\[0\](?!\s+if\s+\w+)",
                "description": "List access without bounds checking",
                "suggestion": "Check length: if items: first = items[0]",
            },
            "bare_except": {
                "regex": r"except\s*:",
                "description": "Bare except clause",
                "suggestion": "Use specific exceptions",
            },
            "print_statement": {
                "regex": r"\bprint\s*\(",
                "description": "Print instead of logger",
                "suggestion": "Use logger.debug()",
            },
        }

        # Analyze each Python file
        for file in files:
            if not file.endswith(".py") or not os.path.exists(file):
                continue

            try:
                with open(file, "r") as f:
                    content = f.read()

                for pattern_name, pattern_info in patterns.items():
                    matches = re.finditer(pattern_info["regex"], content)
                    for match in matches:
                        line_num = content[: match.start()].count("\n") + 1

                        violations.append(
                            {
                                "file": file,
                                "line": line_num,
                                "pattern": pattern_name,
                                "description": pattern_info["description"],
                                "suggestion": pattern_info["suggestion"],
                            }
                        )
            except Exception as e:
                logger.warning(f"Could not analyze {file}: {e}", exc_info=True)

        return violations

    def sync_patterns_to_markdown(self) -> None:
        """Sync patterns from data/patterns.json to AI_PATTERNS_GUIDE.md."""
        logger.debug("Syncing patterns to markdown")

        try:
            self.pattern_manager.load_patterns()
            self.pattern_manager.sync_to_markdown(self.ai_patterns_md)
            print(f"✓ Patterns synced to {self.ai_patterns_md}")
        except Exception as e:
            print(f"✗ Failed to sync patterns: {e}")
            logger.exception("Pattern sync failed")

    def _format_report(self, report: dict, period: str, format: str = "text") -> str:
        """Format report for display.

        Args:
            report: Report dictionary
            period: Time period
            format: Output format

        Returns:
            Formatted report string
        """
        if format not in {"text", "markdown"}:
            logger.debug(f"Unknown report format '{format}', defaulting to text")
            format = "text"

        if format == "markdown":
            lines = [
                f"# Metrics Analysis Report — {period.title()}",
                f"_Generated: {report['generated_at']}_",
                "",
                "## Summary",
                f"- **Total Bugs:** {report['summary']['total_bugs']}",
                f"- **Total Test Failures:** {report['summary']['total_test_failures']}",
                f"- **Total Code Reviews:** {report['summary']['total_code_reviews']}",
                f"- **Total Performance Metrics:** {report['summary']['total_performance_metrics']}",
                f"- **Total Deployment Issues:** {report['summary']['total_deployment_issues']}",
                "",
                f"## High Frequency Patterns ({len(report['high_frequency_patterns'])})",
            ]

            for pattern in report["high_frequency_patterns"][:10]:
                lines.append(
                    f"- `{pattern['pattern']}` ({pattern['count']} occurrences)"
                )

            lines.append("")
            lines.append(
                f"## Patterns Ranked by Severity ({len(report['ranked_patterns'])})"
            )

            for pattern in report["ranked_patterns"][:10]:
                lines.append(
                    f"- `{pattern['pattern']}` — {pattern['severity']} (count: {pattern['count']})"
                )

            return "\n".join(lines)

        lines = [
            "=" * 60,
            f"METRICS ANALYSIS REPORT - {period.upper()}",
            f"Generated: {report['generated_at']}",
            "=" * 60,
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

        for pattern in report["high_frequency_patterns"][:10]:
            lines.append(f"  - {pattern['pattern']}: {pattern['count']} occurrences")

        lines.append("")
        lines.append(f"PATTERNS RANKED BY SEVERITY: {len(report['ranked_patterns'])}")

        for pattern in report["ranked_patterns"][:10]:
            lines.append(
                f"  - {pattern['pattern']}: {pattern['severity']} (count: {pattern['count']})"
            )

        lines.append("")
        lines.append("=" * 60)

        return "\n".join(lines)


def _handle_login(api_url: str) -> None:
    """Handle login to cloud backend.

    Args:
        api_url: Base URL of the cloud API
    """
    import getpass

    print("=== Feedback Loop - Cloud Login ===")
    print(f"API URL: {api_url}\n")

    # Get credentials
    email = input("Email: ").strip()
    password = getpass.getpass("Password: ")

    try:
        import requests

        # Make login request
        response = requests.post(
            f"{api_url}/api/v1/auth/login", json={"email": email, "password": password}
        )

        if response.status_code == 200:
            data = response.json()

            # Save API key to local config
            config_dir = Path.home() / ".feedback-loop"
            config_dir.mkdir(exist_ok=True)
            config_file = config_dir / "auth.json"

            with open(config_file, "w") as f:
                json.dump(
                    {
                        "api_url": api_url,
                        "api_key": data["access_token"],
                        "username": data["username"],
                        "user_id": data["user_id"],
                        "organization_id": data["organization_id"],
                        "logged_in_at": datetime.now().isoformat(),
                    },
                    f,
                    indent=2,
                )

            print("\n✓ Login successful!")
            print(f"  Username: {data['username']}")
            print(f"  Role: {data['role']}")
            print(f"  Organization ID: {data['organization_id']}")
            print(f"\n✓ Credentials saved to {config_file}")
            print("\nYou can now use cloud sync features:")
            print("  - Patterns will sync with your team")
            print("  - Metrics will be aggregated for analytics")
            print("  - Team settings will be enforced")
        else:
            error_detail = response.json().get("detail", "Unknown error")
            print(f"\n✗ Login failed: {error_detail}")

    except ImportError:
        print("\n✗ Error: 'requests' library not installed")
        print("  Install with: pip install requests")
    except Exception as e:
        print(f"\n✗ Login failed: {e}")


async def _handle_memory_sync(patterns_file: str) -> None:
    """Handle memory sync command.

    Args:
        patterns_file: Path to patterns file
    """
    from metrics.memory_service import FeedbackLoopMemory

    print("=== Feedback Loop - Memory Sync ===\n")

    # Check if memory is enabled
    if not os.getenv("FEEDBACK_LOOP_MEMORY_ENABLED"):
        print("⚠  Memory integration is not enabled")
        print("   Set FEEDBACK_LOOP_MEMORY_ENABLED=true to enable")
        return

    try:
        # Initialize memory service
        memory = FeedbackLoopMemory(
            storage_type=os.getenv("FEEDBACK_LOOP_MEMORY_STORAGE", "inmemory"),
            openai_api_key=os.getenv("OPENAI_API_KEY"),
        )

        if not await memory.initialize():
            print("✗ Failed to initialize memory service")
            print("  Make sure MemU is installed: pip install memu-py")
            return

        # Load patterns
        pattern_manager = PatternManager(patterns_file, use_memory=False)
        pattern_manager.memory = memory

        print(f"📚 Syncing {len(pattern_manager.patterns)} patterns to memory...")
        synced_count = await pattern_manager.sync_patterns_to_memory()

        print(f"\n✓ Synced {synced_count} patterns to MemU memory")
        print("  Storage:", memory.storage_type)

    except Exception as e:
        print(f"\n✗ Sync failed: {e}")
        logger.exception("Memory sync failed")


async def _handle_memory_query(query: str, limit: int) -> None:
    """Handle memory query command.

    Args:
        query: Search query
        limit: Maximum number of results
    """
    from metrics.memory_service import FeedbackLoopMemory

    print("=== Feedback Loop - Memory Query ===\n")
    print(f"Query: {query}")
    print(f"Limit: {limit}\n")

    # Check if memory is enabled
    if not os.getenv("FEEDBACK_LOOP_MEMORY_ENABLED"):
        print("⚠  Memory integration is not enabled")
        print("   Set FEEDBACK_LOOP_MEMORY_ENABLED=true to enable")
        return

    try:
        # Initialize memory service
        memory = FeedbackLoopMemory(
            storage_type=os.getenv("FEEDBACK_LOOP_MEMORY_STORAGE", "inmemory"),
            openai_api_key=os.getenv("OPENAI_API_KEY"),
        )

        if not await memory.initialize():
            print("✗ Failed to initialize memory service")
            return

        # Query patterns
        print("🔍 Searching patterns...")
        result = await memory.retrieve_patterns(query, method="rag", limit=limit)

        if not result or not result.get("results"):
            print("\n✗ No patterns found")
            return

        print(f"\n✓ Found {len(result['results'])} patterns:\n")
        for idx, pattern in enumerate(result["results"], 1):
            metadata = pattern.get("metadata", {})
            score = pattern.get("score", 0.0)
            print(
                f"{idx}. {metadata.get('pattern_name', 'Unknown')} (score: {score:.2f})"
            )
            print(f"   {pattern.get('content', '')[:100]}...")
            print()

    except Exception as e:
        print(f"\n✗ Query failed: {e}")
        logger.exception("Memory query failed")


async def _handle_memory_recommend(context: str, limit: int) -> None:
    """Handle memory recommend command.

    Args:
        context: Development context
        limit: Maximum number of recommendations
    """
    from metrics.memory_service import FeedbackLoopMemory

    print("=== Feedback Loop - Pattern Recommendations ===\n")
    print(f"Context: {context}")
    print(f"Limit: {limit}\n")

    # Check if memory is enabled
    if not os.getenv("FEEDBACK_LOOP_MEMORY_ENABLED"):
        print("⚠  Memory integration is not enabled")
        print("   Set FEEDBACK_LOOP_MEMORY_ENABLED=true to enable")
        return

    try:
        # Initialize memory service
        memory = FeedbackLoopMemory(
            storage_type=os.getenv("FEEDBACK_LOOP_MEMORY_STORAGE", "inmemory"),
            openai_api_key=os.getenv("OPENAI_API_KEY"),
        )

        if not await memory.initialize():
            print("✗ Failed to initialize memory service")
            return

        # Get recommendations
        print("💡 Getting recommendations...")
        recommendations = await memory.get_pattern_recommendations(context, limit)

        if not recommendations:
            print("\n✗ No recommendations found")
            return

        print(f"\n✓ Recommended {len(recommendations)} patterns:\n")
        for idx, rec in enumerate(recommendations, 1):
            print(f"{idx}. {rec['pattern_name']} (score: {rec['score']:.2f})")
            print(f"   {rec['content'][:100]}...")
            print()

    except Exception as e:
        print(f"\n✗ Recommendation failed: {e}")
        logger.exception("Memory recommendation failed")


async def _handle_memory_stats() -> None:
    """Handle memory stats command."""
    from metrics.memory_service import FeedbackLoopMemory

    print("=== Feedback Loop - Memory Statistics ===\n")

    # Check if memory is enabled
    if not os.getenv("FEEDBACK_LOOP_MEMORY_ENABLED"):
        print("⚠  Memory integration is not enabled")
        print("   Set FEEDBACK_LOOP_MEMORY_ENABLED=true to enable")
        return

    try:
        # Initialize memory service
        memory = FeedbackLoopMemory(
            storage_type=os.getenv("FEEDBACK_LOOP_MEMORY_STORAGE", "inmemory"),
            openai_api_key=os.getenv("OPENAI_API_KEY"),
        )

        if not await memory.initialize():
            print("✗ Failed to initialize memory service")
            return

        # Get statistics
        stats = await memory.get_memory_stats()

        if not stats:
            print("✗ Failed to retrieve statistics")
            return

        print("📊 Memory Statistics:")
        print(f"  Total memories: {stats.get('total_memories', 0)}")
        print(f"  Patterns: {stats.get('patterns_count', 0)}")
        print(f"  Sessions: {stats.get('sessions_count', 0)}")
        print(f"  Reviews: {stats.get('reviews_count', 0)}")
        print(f"  Storage type: {stats.get('storage_type', 'unknown')}")
        print(
            f"  Status: {'✓ Initialized' if stats.get('initialized') else '✗ Not initialized'}"
        )

    except Exception as e:
        print(f"\n✗ Failed to get statistics: {e}")
        logger.exception("Memory stats failed")


def main() -> int:
    """Main CLI entry point.

    Returns:
        Exit code (0 for success, 1 for error)
    """
    parser = argparse.ArgumentParser(
        description="Metrics Collection and Pattern-Aware Code Generation System"
    )

    subparsers = parser.add_subparsers(dest="command", help="Command to execute")

    # Collect command
    collect_parser = subparsers.add_parser("collect", help="Collect current metrics")
    collect_parser.add_argument(
        "--metrics-file",
        default="data/metrics_data.json",
        help="Path to metrics file (default: data/metrics_data.json)",
    )

    # Analyze command
    analyze_parser = subparsers.add_parser(
        "analyze", help="Analyze metrics and update patterns"
    )
    analyze_parser.add_argument(
        "--metrics-file",
        default="data/metrics_data.json",
        help="Path to metrics file (default: data/metrics_data.json)",
    )
    analyze_parser.add_argument(
        "--patterns-file",
        default="data/patterns.json",
        help="Path to patterns file (default: data/patterns.json)",
    )
    analyze_parser.add_argument(
        "--no-update", action="store_true", help="Don't update pattern library"
    )

    # Generate command
    generate_parser = subparsers.add_parser(
        "generate", help="Generate pattern-aware code"
    )
    generate_parser.add_argument("prompt", help="Prompt for code generation")
    generate_parser.add_argument("--output", help="Output file for generated code")
    generate_parser.add_argument(
        "--no-apply", action="store_true", help="Don't apply patterns automatically"
    )
    generate_parser.add_argument(
        "--min-confidence",
        type=float,
        default=0.8,
        help="Minimum confidence to apply patterns (default: 0.8)",
    )
    generate_parser.add_argument(
        "--metrics-file",
        default="data/metrics_data.json",
        help="Path to metrics file (default: data/metrics_data.json)",
    )
    generate_parser.add_argument(
        "--patterns-file",
        default="data/patterns.json",
        help="Path to patterns file (default: data/patterns.json)",
    )

    # Synthesize command
    synthesize_parser = subparsers.add_parser(
        "synthesize", help="Synthesize optimal code from candidates"
    )
    synthesize_parser.add_argument("prompt", help="Prompt for code generation")
    synthesize_parser.add_argument(
        "--candidates",
        type=int,
        default=3,
        help="Number of candidates to generate (default: 3, ignored if --inputs provided)",
    )
    synthesize_parser.add_argument(
        "--inputs",
        nargs="+",
        help="Input files to use as candidates (instead of generating)",
    )
    synthesize_parser.add_argument("--output", help="Output file for synthesized code")
    synthesize_parser.add_argument(
        "--metrics-file",
        default="data/metrics_data.json",
        help="Path to metrics file (default: data/metrics_data.json)",
    )
    synthesize_parser.add_argument(
        "--patterns-file",
        default="data/patterns.json",
        help="Path to patterns file (default: data/patterns.json)",
    )

    # Report command
    report_parser = subparsers.add_parser("report", help="Generate analysis report")
    report_parser.add_argument(
        "--period",
        choices=["all", "month", "week"],
        default="all",
        help="Time period for report (default: all)",
    )
    report_parser.add_argument("--output", help="Output file for report")
    report_parser.add_argument(
        "--metrics-file",
        default="data/metrics_data.json",
        help="Path to metrics file (default: data/metrics_data.json)",
    )
    report_parser.add_argument(
        "--format",
        choices=["text", "markdown"],
        default="text",
        help="Report format (default: text)",
    )

    # Analyze commit command
    analyze_commit_parser = subparsers.add_parser(
        "analyze-commit", help="Analyze commit diff for pattern violations"
    )
    analyze_commit_parser.add_argument("--base", required=True, help="Base commit SHA")
    analyze_commit_parser.add_argument("--head", required=True, help="Head commit SHA")
    analyze_commit_parser.add_argument(
        "--output", help="Output file for analysis results"
    )

    # Sync patterns command
    sync_parser = subparsers.add_parser(
        "sync-to-markdown",
        help="Sync patterns from data/patterns.json to docs/AI_PATTERNS_GUIDE.md",
    )
    sync_parser.add_argument(
        "--patterns-file",
        default="data/patterns.json",
        help="Path to patterns file (default: data/patterns.json)",
    )
    sync_parser.add_argument(
        "--markdown-file",
        default="docs/AI_PATTERNS_GUIDE.md",
        help="Path to markdown file (default: docs/AI_PATTERNS_GUIDE.md)",
    )

    # Memory commands (for MemU integration)
    memory_parser = subparsers.add_parser(
        "memory", help="Memory operations (MemU integration)"
    )
    memory_subparsers = memory_parser.add_subparsers(
        dest="memory_command", help="Memory command"
    )

    # memory sync - Sync patterns to memory
    memory_sync_parser = memory_subparsers.add_parser(
        "sync", help="Sync all patterns to MemU memory"
    )
    memory_sync_parser.add_argument(
        "--patterns-file",
        default="data/patterns.json",
        help="Path to patterns file (default: data/patterns.json)",
    )

    # memory query - Semantic pattern search
    memory_query_parser = memory_subparsers.add_parser(
        "query", help="Query patterns using semantic search"
    )
    memory_query_parser.add_argument("query", help="Natural language query")
    memory_query_parser.add_argument(
        "--limit", type=int, default=5, help="Maximum number of results (default: 5)"
    )

    # memory recommend - Get pattern recommendations
    memory_recommend_parser = memory_subparsers.add_parser(
        "recommend", help="Get pattern recommendations for context"
    )
    memory_recommend_parser.add_argument(
        "--context", required=True, help="Current development context"
    )
    memory_recommend_parser.add_argument(
        "--limit",
        type=int,
        default=3,
        help="Maximum number of recommendations (default: 3)",
    )

    # memory stats - Show memory statistics
    memory_subparsers.add_parser("stats", help="Show memory statistics")

    # Login command (for cloud sync)
    login_parser = subparsers.add_parser(
        "login", help="Login to feedback-loop cloud for team collaboration"
    )
    login_parser.add_argument(
        "--api-url",
        default="http://localhost:8000",
        help="API URL (default: http://localhost:8000)",
    )

    args = parser.parse_args()

    # Configure logging
    # Use DEBUG level if --verbose flag is present, else INFO
    log_level = (
        logging.DEBUG if "--verbose" in sys.argv or "-v" in sys.argv else logging.INFO
    )
    logging.basicConfig(
        level=log_level, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
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
                metrics_file=args.metrics_file, patterns_file=args.patterns_file
            )
            integration.analyze_metrics(update_patterns=not args.no_update)

        elif args.command == "generate":
            integration = MetricsIntegration(
                metrics_file=args.metrics_file, patterns_file=args.patterns_file
            )
            integration.generate_code(
                prompt=args.prompt,
                output_file=args.output,
                apply_patterns=not args.no_apply,
                min_confidence=args.min_confidence,
            )

        elif args.command == "synthesize":
            integration = MetricsIntegration(
                metrics_file=args.metrics_file, patterns_file=args.patterns_file
            )
            integration.synthesize_code(
                prompt=args.prompt,
                num_candidates=args.candidates,
                output_file=args.output,
                input_files=args.inputs,
            )

        elif args.command == "report":
            integration = MetricsIntegration(metrics_file=args.metrics_file)
            integration.generate_report(
                period=args.period, output_file=args.output, format=args.format
            )

        elif args.command == "analyze-commit":
            integration = MetricsIntegration()
            integration.analyze_commit(
                base_sha=args.base, head_sha=args.head, output_file=args.output
            )

        elif args.command == "sync-to-markdown":
            integration = MetricsIntegration(
                patterns_file=args.patterns_file, ai_patterns_md=args.markdown_file
            )
            integration.sync_patterns_to_markdown()

        elif args.command == "login":
            _handle_login(args.api_url)

        elif args.command == "memory":
            if not args.memory_command:
                print(
                    "Error: memory command requires a subcommand (sync, query, recommend, stats)"
                )
                return 1

            import asyncio

            if args.memory_command == "sync":
                asyncio.run(_handle_memory_sync(args.patterns_file))
            elif args.memory_command == "query":
                asyncio.run(_handle_memory_query(args.query, args.limit))
            elif args.memory_command == "recommend":
                asyncio.run(_handle_memory_recommend(args.context, args.limit))
            elif args.memory_command == "stats":
                asyncio.run(_handle_memory_stats())

        return 0

    except Exception as e:
        print(f"✗ Error: {e}", file=sys.stderr)
        logger.exception("Command failed")
        return 1


if __name__ == "__main__":
    sys.exit(main())
