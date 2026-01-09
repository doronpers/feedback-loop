"""
Pytest plugin for automatic test failure metrics collection.

This plugin automatically collects test failures and logs them to the metrics system.
"""

import logging
import os
import re
from pathlib import Path

import pytest

logger = logging.getLogger(__name__)


def pytest_configure(config):
    """Register the metrics plugin."""
    config.pluginmanager.register(MetricsPlugin(config), "metrics_plugin")


def pytest_addoption(parser):
    """Add command-line options for metrics collection."""
    parser.addoption(
        "--metrics-output",
        action="store",
        default=None,
        help="Output file for collected metrics"
    )
    parser.addoption(
        "--enable-metrics",
        action="store_true",
        default=False,
        help="Enable automatic metrics collection"
    )


class MetricsPlugin:
    """Plugin to collect test failure metrics."""

    def __init__(self, config):
        """Initialize the metrics plugin.

        Args:
            config: pytest config object
        """
        self.config = config
        self.metrics_output = config.getoption("--metrics-output")
        self.enable_metrics = config.getoption("--enable-metrics")

        # Auto-enable if metrics output is specified
        if self.metrics_output:
            self.enable_metrics = True

        # Auto-enable metrics based on configuration or environment
        if not self.enable_metrics:
            try:
                from metrics.config_manager import ConfigManager
                config_manager = ConfigManager.get_instance()
                if config_manager.should_auto_enable_metrics():
                    self.enable_metrics = True
                    logger.info("Auto-enabled metrics collection (config or history detected)")
            except ImportError:
                # Config manager not available, check environment variable
                import os
                if os.getenv("FEEDBACK_LOOP_AUTO_METRICS") == "1":
                    self.enable_metrics = True
                # Also check if metrics_data.json exists
                elif Path("metrics_data.json").exists():
                    self.enable_metrics = True
                # Check for .feedback-loop/auto-metrics marker
                elif Path(".feedback-loop/auto-metrics").exists():
                    self.enable_metrics = True

        # Default output file if metrics enabled but no file specified
        if self.enable_metrics and not self.metrics_output:
            try:
                from metrics.config_manager import ConfigManager
                config_manager = ConfigManager.get_instance()
                self.metrics_output = config_manager.get("auto_metrics.output_file", "metrics_data.json")
            except ImportError:
                self.metrics_output = "metrics_data.json"

        self.collector = None
        if self.enable_metrics:
            try:
                from metrics.collector import MetricsCollector
                self.collector = MetricsCollector()

                # Load existing metrics if output file exists
                if self.metrics_output and Path(self.metrics_output).exists():
                    with open(self.metrics_output, 'r') as f:
                        import json
                        self.collector.data = json.load(f)

                logger.info("Metrics collection enabled")
            except ImportError:
                logger.warning("Could not import MetricsCollector, metrics disabled")
                self.enable_metrics = False

    # NOTE: Auto-analysis feature
    # When metrics collection is enabled (via --enable-metrics or --metrics-output),
    # the plugin automatically analyzes test results after each pytest session.
    # This provides immediate feedback on pattern violations and effectiveness.
    # To disable auto-analysis while keeping metrics collection, set the
    # environment variable: FEEDBACK_LOOP_SKIP_AUTO_ANALYSIS=1

    @pytest.hookimpl(tryfirst=True, hookwrapper=True)
    def pytest_runtest_makereport(self, item, call):
        """Hook to capture test execution results.

        Args:
            item: Test item
            call: Call information
        """
        outcome = yield
        report = outcome.get_result()

        if not self.enable_metrics or not self.collector:
            return

        # Only process test call phase (not setup/teardown)
        if report.when != "call":
            return

        # Log test failures
        if report.failed:
            self._log_test_failure(item, report, call)

    def _log_test_failure(self, item, report, call):
        """Log a test failure to the metrics collector.

        Args:
            item: Test item
            report: Test report
            call: Call information
        """
        if not self.collector:
            return

        # Extract test information
        test_name = item.nodeid
        failure_reason = str(report.longrepr) if report.longrepr else "Unknown failure"

        # Try to detect pattern violated
        pattern_violated = self._detect_pattern_from_failure(failure_reason, report)

        # Extract code snippet if available
        code_snippet = self._extract_code_snippet(item, report)

        # Log the failure
        try:
            self.collector.log_test_failure(
                test_name=test_name,
                failure_reason=failure_reason[:500],  # Limit length
                pattern_violated=pattern_violated,
                code_snippet=code_snippet
            )
            logger.debug(f"Logged test failure: {test_name}")
        except Exception as e:
            logger.warning(f"Failed to log test failure: {e}")

    def _detect_pattern_from_failure(self, failure_reason: str, report) -> str:
        """Detect which pattern was violated from the failure.

        Args:
            failure_reason: Failure reason text
            report: Test report

        Returns:
            Pattern name or None
        """
        failure_lower = failure_reason.lower()

        # Pattern detection heuristics
        if "typeerror" in failure_lower and "json" in failure_lower:
            if "float64" in failure_lower or "int64" in failure_lower or "numpy" in failure_lower:
                return "numpy_json_serialization"

        if "indexerror" in failure_lower or "list index out of range" in failure_lower:
            return "bounds_checking"

        if "exception" in failure_lower:
            # Check if it's a bare except issue
            if "bare except" in failure_lower or "exception:" in failure_lower:
                return "specific_exceptions"

        if "print" in failure_lower and "logger" in failure_lower:
            return "logger_debug"

        if "file" in failure_lower and ("not closed" in failure_lower or "leak" in failure_lower):
            return "temp_file_handling"

        if "memory" in failure_lower or "memoryerror" in failure_lower:
            return "large_file_processing"

        # Try to extract pattern from test docstring
        if hasattr(report, 'location'):
            # Pattern might be in test name
            test_name = str(report.location[2]) if len(report.location) > 2 else ""
            for pattern in ["numpy_json", "bounds_checking", "specific_exceptions",
                           "logger_debug", "temp_file", "large_file"]:
                if pattern in test_name.lower():
                    return pattern.replace("_", "_")

        return None

    def _extract_code_snippet(self, item, report) -> str:
        """Extract code snippet related to the failure.

        Args:
            item: Test item
            report: Test report

        Returns:
            Code snippet or None
        """
        try:
            # Try to extract from traceback
            if hasattr(report, 'longreprtext'):
                lines = report.longreprtext.split('\n')
                # Find lines with code (usually indented)
                code_lines = [line for line in lines if line.startswith('    ') or line.startswith('>   ')]
                if code_lines:
                    return '\n'.join(code_lines[:10])  # Limit to 10 lines
        except Exception:
            pass

        return None

    def pytest_sessionfinish(self, session, exitstatus):
        """Hook called after test session finishes.

        Args:
            session: Test session
            exitstatus: Exit status
        """
        if not self.enable_metrics or not self.collector:
            return

        # Save metrics to file
        if self.metrics_output:
            try:
                import json
                with open(self.metrics_output, 'w') as f:
                    f.write(self.collector.export_json())

                summary = self.collector.get_summary()
                logger.info(f"Metrics saved to {self.metrics_output}")
                logger.info(f"Test failures logged: {summary['test_failures']}")

                # Automatic Analysis (can be skipped via environment variable)
                if os.getenv("FEEDBACK_LOOP_SKIP_AUTO_ANALYSIS"):
                    logger.info("Auto-analysis skipped (FEEDBACK_LOOP_SKIP_AUTO_ANALYSIS set)")
                    if not self._is_quiet():
                        print("\n✓ Metrics saved. Auto-analysis skipped.")
                    return

                # Check if auto-analysis should run based on config
                failure_count = summary.get('test_failures', 0)
                should_analyze = True
                is_quiet = False
                
                try:
                    from metrics.config_manager import ConfigManager
                    config_manager = ConfigManager.get_instance()
                    should_analyze = config_manager.should_auto_analyze(failure_count)
                    is_quiet = config_manager.is_quiet()
                except ImportError:
                    # Config manager not available, use default behavior
                    pass

                if not should_analyze:
                    if not is_quiet:
                        print(f"\n✓ Metrics saved ({failure_count} failures, below threshold)")
                    return

                try:
                    from metrics.integrate import MetricsIntegration
                    if not is_quiet:
                        print("\n🔄 Feedback Loop: Analyzing results...")
                    integration = MetricsIntegration(
                        metrics_file=self.metrics_output,
                        patterns_file="patterns.json"
                    )
                    integration.analyze_metrics(update_patterns=True)
                    
                    # Show dashboard if configured
                    try:
                        from metrics.config_manager import ConfigManager
                        config_manager = ConfigManager.get_instance()
                        if config_manager.should_show_dashboard():
                            from bin.fl_dashboard import main as dashboard_main
                            dashboard_main()
                    except (ImportError, Exception):
                        pass
                except Exception as e:
                    logger.error(f"Analysis failed: {e}")
                    if not is_quiet:
                        print(f"\n❌ Analysis failed: {e}")
    
    def _is_quiet(self) -> bool:
        """Check if output should be quiet."""
        try:
            from metrics.config_manager import ConfigManager
            config_manager = ConfigManager.get_instance()
            return config_manager.is_quiet()
        except ImportError:
            return False
            except Exception as e:
                logger.error(f"Failed to save metrics: {e}")
