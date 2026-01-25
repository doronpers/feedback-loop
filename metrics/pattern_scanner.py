"""
Pattern Scanner Module

Scans codebase for pattern violations and provides detailed analysis.
"""

import ast
import re
from pathlib import Path
from typing import Any, Dict, List, Optional

from rich.console import Console
from rich.theme import Theme

# Custom theme
custom_theme = Theme(
    {
        "info": "cyan",
        "warning": "yellow",
        "error": "red",
        "success": "green",
        "header": "bold blue",
        "accent": "magenta",
    }
)

console = Console(theme=custom_theme)


class PatternScanner:
    """Scans codebase for pattern violations."""

    def __init__(self):
        """Initialize pattern scanner."""
        self.pattern_rules = self._load_pattern_rules()

    def _load_pattern_rules(self) -> Dict[str, Dict[str, Any]]:
        """Load pattern detection rules.

        Returns:
            Dictionary of pattern rules
        """
        return {
            "numpy_json_serialization": {
                "regex": r"json\.dumps\([^)]*np\.|json\.dumps\([^)]*numpy",
                "ast_patterns": [{"type": "call", "func": "json.dumps", "contains_numpy": True}],
                "description": "NumPy types in JSON serialization",
                "severity": "high",
                "category": "serialization",
            },
            "bounds_checking": {
                "regex": r"\w+\[0\](?!\s+if\s+\w+)",
                "ast_patterns": [{"type": "subscript", "index": 0, "no_bounds_check": True}],
                "description": "List access without bounds checking",
                "severity": "medium",
                "category": "defensive_programming",
            },
            "specific_exceptions": {
                "regex": r"except\s*:",
                "ast_patterns": [{"type": "except_handler", "bare_except": True}],
                "description": "Bare except clause",
                "severity": "medium",
                "category": "error_handling",
            },
            "structured_logging": {
                "regex": r"\bprint\s*\(",
                "ast_patterns": [{"type": "call", "func": "print"}],
                "description": "Using print instead of logging",
                "severity": "low",
                "category": "production_readiness",
            },
            "temp_file_handling": {
                "regex": r"tempfile\.mktemp\(",
                "ast_patterns": [{"type": "call", "func": "tempfile.mktemp"}],
                "description": "Using deprecated mktemp function",
                "severity": "high",
                "category": "resource_management",
            },
        }

    def scan_file(self, file_path: Path) -> Dict[str, Any]:
        """Scan a single file for pattern violations.

        Args:
            file_path: Path to file to scan

        Returns:
            Dictionary with scan results
        """
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()
        except Exception as e:
            return {"file": str(file_path), "error": f"Could not read file: {e}", "violations": []}

        violations = []

        # Regex-based scanning
        lines = content.split("\n")
        for line_num, line in enumerate(lines, 1):
            for pattern_name, rule in self.pattern_rules.items():
                if re.search(rule["regex"], line):
                    violations.append(
                        {
                            "pattern": pattern_name,
                            "line": line_num,
                            "code": line.strip(),
                            "description": rule["description"],
                            "severity": rule["severity"],
                            "category": rule["category"],
                            "confidence": 0.8,
                            "method": "regex",
                        }
                    )

        # AST-based scanning for more complex patterns
        try:
            tree = ast.parse(content)
            ast_violations = self._scan_ast(tree, file_path)
            violations.extend(ast_violations)
        except SyntaxError:
            # Skip AST analysis for files with syntax errors
            pass

        return {
            "file": str(file_path),
            "error": None,
            "violations": violations,
            "total_violations": len(violations),
        }

    def _scan_ast(self, tree: ast.AST, file_path: Path) -> List[Dict[str, Any]]:
        """Scan AST for pattern violations.

        Args:
            tree: AST tree to scan
            file_path: File path for context

        Returns:
            List of violations found via AST analysis
        """
        violations = []
        visitor = PatternASTVisitor(self.pattern_rules)
        visitor.visit(tree)

        for violation in visitor.violations:
            violations.append({**violation, "method": "ast"})

        return violations

    def scan_directory(
        self,
        directory: Path,
        include_patterns: Optional[List[str]] = None,
        exclude_patterns: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """Scan a directory for pattern violations.

        Args:
            directory: Directory to scan
            include_patterns: File patterns to include (e.g., ["*.py"])
            exclude_patterns: File patterns to exclude

        Returns:
            Dictionary with scan results
        """
        if include_patterns is None:
            include_patterns = ["*.py"]

        if exclude_patterns is None:
            exclude_patterns = ["__pycache__", "*.pyc", ".git", "venv", "env"]

        all_files = []
        violations_by_file = {}
        total_violations = 0

        # Collect all Python files
        for pattern in include_patterns:
            for file_path in directory.rglob(pattern):
                if file_path.is_file():
                    # Check exclude patterns
                    should_exclude = False
                    for exclude in exclude_patterns:
                        if exclude in str(file_path):
                            should_exclude = True
                            break

                    if not should_exclude:
                        all_files.append(file_path)

        console.print(f"🔍 Scanning {len(all_files)} files...", style="info")

        # Scan each file
        for file_path in all_files:
            result = self.scan_file(file_path)
            if result["violations"]:
                violations_by_file[str(file_path)] = result
                total_violations += result["total_violations"]

        # Aggregate results
        violations_by_pattern = {}
        violations_by_severity = {"high": 0, "medium": 0, "low": 0}
        violations_by_category = {}

        for file_result in violations_by_file.values():
            for violation in file_result["violations"]:
                pattern = violation["pattern"]
                severity = violation["severity"]
                category = violation["category"]

                violations_by_pattern[pattern] = violations_by_pattern.get(pattern, 0) + 1
                violations_by_severity[severity] += 1
                violations_by_category[category] = violations_by_category.get(category, 0) + 1

        return {
            "directory": str(directory),
            "files_scanned": len(all_files),
            "files_with_violations": len(violations_by_file),
            "total_violations": total_violations,
            "violations_by_file": violations_by_file,
            "violations_by_pattern": violations_by_pattern,
            "violations_by_severity": violations_by_severity,
            "violations_by_category": violations_by_category,
        }

    def generate_report(self, scan_results: Dict[str, Any]) -> str:
        """Generate a human-readable report from scan results.

        Args:
            scan_results: Results from scan_directory

        Returns:
            Formatted report string
        """
        report = []
        report.append("Pattern Violation Scan Report")
        report.append("=" * 50)
        report.append("")

        report.append(f"Directory: {scan_results['directory']}")
        report.append(f"Files scanned: {scan_results['files_scanned']}")
        report.append(f"Files with violations: {scan_results['files_with_violations']}")
        report.append(f"Total violations: {scan_results['total_violations']}")
        report.append("")

        if scan_results["violations_by_severity"]:
            report.append("Violations by Severity:")
            for severity, count in scan_results["violations_by_severity"].items():
                severity_icon = {"high": "🔴", "medium": "🟡", "low": "🟢"}.get(severity, "⚪")
                report.append(f"  {severity_icon} {severity.title()}: {count}")
            report.append("")

        if scan_results["violations_by_pattern"]:
            report.append("Top Patterns:")
            sorted_patterns = sorted(
                scan_results["violations_by_pattern"].items(), key=lambda x: x[1], reverse=True
            )
            for pattern, count in sorted_patterns[:10]:
                report.append(f"  • {pattern}: {count} occurrences")
            report.append("")

        if scan_results["violations_by_file"]:
            report.append("Files with Violations:")
            for file_path, file_result in list(scan_results["violations_by_file"].items())[:10]:
                report.append(
                    f"  • {Path(file_path).name}: {file_result['total_violations']} violations"
                )

        return "\n".join(report)


class PatternASTVisitor(ast.NodeVisitor):
    """AST visitor for detecting pattern violations."""

    def __init__(self, pattern_rules: Dict[str, Dict[str, Any]]):
        """Initialize AST visitor.

        Args:
            pattern_rules: Pattern detection rules
        """
        self.pattern_rules = pattern_rules
        self.violations = []
        self.current_line = 0

    def visit_Call(self, node: ast.Call) -> None:
        """Visit function call nodes."""
        self.current_line = getattr(node, "lineno", 0)

        # Get function name
        func_name = self._get_func_name(node.func)

        # Check for pattern violations
        for pattern_name, rule in self.pattern_rules.items():
            for ast_pattern in rule.get("ast_patterns", []):
                if ast_pattern.get("type") == "call" and ast_pattern.get("func") == func_name:
                    # Additional checks
                    if func_name == "json.dumps" and ast_pattern.get("contains_numpy"):
                        if self._contains_numpy_args(node):
                            self._add_violation(pattern_name, rule, node)
                    else:
                        self._add_violation(pattern_name, rule, node)

        self.generic_visit(node)

    def visit_Subscript(self, node: ast.Subscript) -> None:
        """Visit subscript (indexing) nodes."""
        self.current_line = getattr(node, "lineno", 0)

        # Check for bounds checking violations
        if isinstance(node.slice, ast.Index):
            if isinstance(node.slice.value, ast.Num) and node.slice.value.n == 0:
                # Check if there's a bounds check in the current context
                # This is a simplified check - real implementation would be more sophisticated
                self._add_violation("bounds_checking", self.pattern_rules["bounds_checking"], node)

        self.generic_visit(node)

    def visit_ExceptHandler(self, node: ast.ExceptHandler) -> None:
        """Visit exception handler nodes."""
        self.current_line = getattr(node, "lineno", 0)

        # Check for bare except
        if node.type is None:
            self._add_violation(
                "specific_exceptions", self.pattern_rules["specific_exceptions"], node
            )

        self.generic_visit(node)

    def _get_func_name(self, func_node: ast.expr) -> str:
        """Get function name from AST node.

        Args:
            func_node: Function AST node

        Returns:
            Function name string
        """
        if isinstance(func_node, ast.Name):
            return func_node.id
        elif isinstance(func_node, ast.Attribute):
            return func_node.attr
        return ""

    def _contains_numpy_args(self, call_node: ast.Call) -> bool:
        """Check if call arguments contain NumPy usage.

        Args:
            call_node: Function call AST node

        Returns:
            True if NumPy usage detected
        """
        # Simple heuristic - check for 'np.' or 'numpy' in the source
        # In a real implementation, this would use more sophisticated analysis
        return True  # Simplified for this example

    def _add_violation(self, pattern_name: str, rule: Dict[str, Any], node: ast.AST) -> None:
        """Add a pattern violation.

        Args:
            pattern_name: Name of the pattern
            rule: Pattern rule dictionary
            node: AST node where violation occurred
        """
        self.violations.append(
            {
                "pattern": pattern_name,
                "line": getattr(node, "lineno", 0),
                "code": f"<AST node: {type(node).__name__}>",  # Simplified
                "description": rule["description"],
                "severity": rule["severity"],
                "category": rule["category"],
                "confidence": 0.9,  # AST-based detection is more reliable
            }
        )
