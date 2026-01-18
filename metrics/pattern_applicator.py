"""
Pattern Applicator Module

Applies patterns to code with impact preview and guided workflow.
"""

import ast
import difflib
import re
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from rich.console import Console
from rich.layout import Layout
from rich.panel import Panel
from rich.prompt import Confirm, Prompt
from rich.table import Table
from rich.theme import Theme

from metrics.pattern_scanner import PatternScanner

# Custom theme
custom_theme = Theme(
    {
        "info": "cyan",
        "warning": "yellow",
        "error": "red",
        "success": "green",
        "header": "bold blue",
        "accent": "magenta",
        "good": "green",
        "bad": "red",
    }
)

console = Console(theme=custom_theme)


class PatternApplicator:
    """Applies patterns to code with preview and confirmation."""

    def __init__(self):
        """Initialize pattern applicator."""
        self.scanner = PatternScanner()
        self.applied_fixes = []
        self.fix_templates = self._load_fix_templates()

    def _load_fix_templates(self) -> Dict[str, Dict[str, Any]]:
        """Load pattern fix templates.

        Returns:
            Dictionary of fix templates
        """
        return {
            "numpy_json_serialization": {
                "description": "Convert NumPy types for JSON serialization",
                "transforms": [
                    {
                        "pattern": r"(\w+)\s*=\s*np\.(\w+)\(([^)]+)\)",
                        "replacement": r"\1 = float(np.\2(\3))",
                        "description": "Convert NumPy scalar to Python float",
                    },
                    {
                        "pattern": r"json\.dumps\(([^)]*)\b(\w+)\b([^)]*)\)",
                        "replacement": r"json.dumps(\1\2.tolist()\3)",
                        "description": "Convert NumPy arrays to lists for JSON",
                        "condition": lambda code: "np." in code or "numpy" in code,
                    },
                ],
            },
            "bounds_checking": {
                "description": "Add bounds checking for list access",
                "transforms": [
                    {
                        "pattern": r"(\w+)\[0\]",
                        "replacement": r"\1[0] if \1 else None",
                        "description": "Add bounds check for list access",
                    }
                ],
            },
            "specific_exceptions": {
                "description": "Use specific exception handling",
                "transforms": [
                    {
                        "pattern": r"except\s*:",
                        "replacement": r"except Exception as e:",
                        "description": "Replace bare except with specific exception",
                    }
                ],
            },
            "structured_logging": {
                "description": "Replace print with proper logging",
                "transforms": [
                    {
                        "pattern": r"print\s*\(([^)]+)\)",
                        "replacement": r"logger.info(\1)",
                        "description": "Replace print with logger.info",
                    }
                ],
            },
            "temp_file_handling": {
                "description": "Use secure temporary file handling",
                "transforms": [
                    {
                        "pattern": r"tempfile\.mktemp\s*\(([^)]*)\)",
                        "replacement": r"tempfile.NamedTemporaryFile(delete=False\1).name",
                        "description": "Replace mktemp with NamedTemporaryFile",
                    }
                ],
            },
        }

    def analyze_codebase(self, directory: Path) -> Dict[str, Any]:
        """Analyze codebase for pattern violations.

        Args:
            directory: Directory to analyze

        Returns:
            Analysis results
        """
        console.print(f"🔍 Analyzing codebase: {directory}", style="info")
        return self.scanner.scan_directory(directory)

    def preview_fixes(
        self, scan_results: Dict[str, Any], selected_patterns: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """Preview fixes for pattern violations.

        Args:
            scan_results: Results from codebase scan
            selected_patterns: List of patterns to fix (all if None)

        Returns:
            Preview information with proposed changes
        """
        if selected_patterns is None:
            selected_patterns = list(self.fix_templates.keys())

        preview_info = {
            "total_files": 0,
            "files_to_change": 0,
            "total_fixes": 0,
            "fixes_by_pattern": {},
            "file_changes": {},
        }

        # Process each file with violations
        for file_path, file_result in scan_results.get("violations_by_file", {}).items():
            file_fixes = []
            file_path_obj = Path(file_path)

            try:
                with open(file_path_obj, "r", encoding="utf-8") as f:
                    original_content = f.read()
            except Exception:
                continue

            lines = original_content.split("\n")
            modified_lines = lines.copy()

            # Apply fixes to this file
            for violation in file_result.get("violations", []):
                pattern_name = violation["pattern"]

                if pattern_name not in selected_patterns:
                    continue

                if pattern_name not in self.fix_templates:
                    continue

                line_num = violation["line"] - 1  # Convert to 0-based indexing
                if 0 <= line_num < len(lines):
                    original_line = lines[line_num]
                    fixed_line = self._apply_fix_to_line(original_line, pattern_name)

                    if fixed_line != original_line:
                        modified_lines[line_num] = fixed_line
                        file_fixes.append(
                            {
                                "line": line_num + 1,
                                "pattern": pattern_name,
                                "original": original_line,
                                "fixed": fixed_line,
                                "description": violation["description"],
                            }
                        )

            if file_fixes:
                new_content = "\n".join(modified_lines)
                diff = self._generate_diff(original_content, new_content)

                preview_info["file_changes"][file_path] = {
                    "fixes": file_fixes,
                    "diff": diff,
                    "original_content": original_content,
                    "modified_content": new_content,
                }

                preview_info["files_to_change"] += 1
                preview_info["total_fixes"] += len(file_fixes)

                # Update pattern counts
                for fix in file_fixes:
                    pattern = fix["pattern"]
                    preview_info["fixes_by_pattern"][pattern] = (
                        preview_info["fixes_by_pattern"].get(pattern, 0) + 1
                    )

        preview_info["total_files"] = scan_results.get("files_scanned", 0)

        return preview_info

    def _apply_fix_to_line(self, line: str, pattern_name: str) -> str:
        """Apply pattern fix to a single line.

        Args:
            line: Original line of code
            pattern_name: Name of pattern to apply

        Returns:
            Fixed line of code
        """
        if pattern_name not in self.fix_templates:
            return line

        template = self.fix_templates[pattern_name]

        for transform in template["transforms"]:
            pattern = transform["pattern"]
            replacement = transform["replacement"]

            # Check condition if specified
            if "condition" in transform:
                if not transform["condition"](line):
                    continue

            # Apply regex replacement
            new_line = re.sub(pattern, replacement, line)
            if new_line != line:
                return new_line

        return line

    def _generate_diff(self, original: str, modified: str) -> str:
        """Generate unified diff between original and modified content.

        Args:
            original: Original content
            modified: Modified content

        Returns:
            Unified diff string
        """
        original_lines = original.splitlines(keepends=True)
        modified_lines = modified.splitlines(keepends=True)

        diff = list(
            difflib.unified_diff(
                original_lines, modified_lines, fromfile="original", tofile="modified", lineterm=""
            )
        )

        return "".join(diff)

    def apply_fixes(self, preview_info: Dict[str, Any], backup: bool = True) -> Dict[str, Any]:
        """Apply the previewed fixes to files.

        Args:
            preview_info: Preview information from preview_fixes
            backup: Whether to create backup files

        Returns:
            Application results
        """
        results = {
            "files_modified": 0,
            "total_fixes_applied": 0,
            "backups_created": [],
            "errors": [],
        }

        console.print("🔧 Applying pattern fixes...", style="info")

        for file_path, changes in preview_info.get("file_changes", {}).items():
            file_path_obj = Path(file_path)

            try:
                # Create backup if requested
                if backup:
                    backup_path = file_path_obj.with_suffix(file_path_obj.suffix + ".bak")
                    file_path_obj.replace(backup_path)
                    results["backups_created"].append(str(backup_path))

                    # Write modified content to original location
                    with open(file_path_obj, "w", encoding="utf-8") as f:
                        f.write(changes["modified_content"])
                else:
                    # Overwrite original file
                    with open(file_path_obj, "w", encoding="utf-8") as f:
                        f.write(changes["modified_content"])

                results["files_modified"] += 1
                results["total_fixes_applied"] += len(changes["fixes"])

                console.print(
                    f"✅ Applied {len(changes['fixes'])} fixes to {file_path}", style="success"
                )

            except Exception as e:
                error_msg = f"Failed to apply fixes to {file_path}: {e}"
                results["errors"].append(error_msg)
                console.print(f"❌ {error_msg}", style="error")

        return results

    def show_preview(self, preview_info: Dict[str, Any]) -> None:
        """Display preview of changes in a user-friendly format.

        Args:
            preview_info: Preview information from preview_fixes
        """
        console.print("\n🔍 Pattern Application Preview", style="header")
        console.print("=" * 50, style="header")

        # Summary
        total_files = preview_info["total_files"]
        files_to_change = preview_info["files_to_change"]
        total_fixes = preview_info["total_fixes"]

        console.print(f"Files scanned: {total_files}", style="info")
        console.print(f"Files to modify: {files_to_change}", style="warning")
        console.print(f"Total fixes: {total_fixes}", style="accent")
        console.print()

        # Fixes by pattern
        if preview_info["fixes_by_pattern"]:
            console.print("Fixes by Pattern:", style="header")
            table = Table(show_header=True, header_style="bold blue")
            table.add_column("Pattern", style="cyan")
            table.add_column("Fixes", style="green", justify="right")

            for pattern, count in sorted(
                preview_info["fixes_by_pattern"].items(), key=lambda x: x[1], reverse=True
            ):
                table.add_row(pattern, str(count))

            console.print(table)
            console.print()

        # File-by-file preview
        if preview_info["file_changes"]:
            console.print("File Changes Preview:", style="header")

            for file_path, changes in list(preview_info["file_changes"].items())[
                :3
            ]:  # Show first 3
                console.print(f"\n📄 {Path(file_path).name}", style="cyan")
                console.print(f"   {len(changes['fixes'])} fixes to apply")

                # Show first few fixes
                for fix in changes["fixes"][:2]:
                    console.print(f"   Line {fix['line']}: {fix['pattern']}", style="yellow")
                    console.print(
                        f"     - {fix['original'][:60]}{'...' if len(fix['original']) > 60 else ''}"
                    )
                    console.print(
                        f"     + {fix['fixed'][:60]}{'...' if len(fix['fixed']) > 60 else ''}"
                    )

            if len(preview_info["file_changes"]) > 3:
                console.print(f"\n... and {len(preview_info['file_changes']) - 3} more files")
            console.print()

    def interactive_workflow(self, directory: Path) -> None:
        """Run interactive pattern application workflow.

        Args:
            directory: Directory to analyze and fix
        """
        console.print("[bold blue]🎯 Interactive Pattern Application[/bold blue]")
        console.print("Analyze and fix pattern violations in your codebase.\n")

        # Step 1: Analyze codebase
        console.print("Step 1: Analyzing codebase...", style="header")
        scan_results = self.analyze_codebase(directory)

        if scan_results["total_violations"] == 0:
            console.print("✅ No pattern violations found! Your code looks good.", style="success")
            return

        console.print(
            f"Found {scan_results['total_violations']} violations in {scan_results['files_with_violations']} files.",
            style="warning",
        )
        console.print()

        # Step 2: Show scan results
        console.print("Step 2: Scan Results", style="header")
        report = self.scanner.generate_report(scan_results)
        console.print(Panel.fit(report, border_style="blue"))
        console.print()

        # Step 3: Select patterns to fix
        available_patterns = list(scan_results.get("violations_by_pattern", {}).keys())
        if not available_patterns:
            console.print("❌ No fixable patterns found.", style="warning")
            return

        console.print("Step 3: Select Patterns to Fix", style="header")
        console.print("Available patterns:")
        for i, pattern in enumerate(available_patterns, 1):
            count = scan_results["violations_by_pattern"][pattern]
            console.print(f"  {i}. {pattern} ({count} occurrences)")

        console.print("  0. All patterns")
        console.print()

        pattern_choice = Prompt.ask(
            "Choose patterns to fix (comma-separated numbers, or 0 for all)", default="0"
        )

        if pattern_choice.strip() == "0":
            selected_patterns = available_patterns
        else:
            try:
                indices = [int(x.strip()) - 1 for x in pattern_choice.split(",")]
                selected_patterns = [
                    available_patterns[i] for i in indices if 0 <= i < len(available_patterns)
                ]
            except (ValueError, IndexError):
                console.print("❌ Invalid selection.", style="error")
                return

        console.print(
            f"Selected {len(selected_patterns)} patterns: {', '.join(selected_patterns)}",
            style="info",
        )
        console.print()

        # Step 4: Preview fixes
        console.print("Step 4: Previewing Fixes", style="header")
        preview_info = self.preview_fixes(scan_results, selected_patterns)

        if preview_info["total_fixes"] == 0:
            console.print("⚠️  No fixes available for selected patterns.", style="warning")
            return

        self.show_preview(preview_info)

        # Step 5: Confirm and apply
        console.print("Step 5: Apply Fixes", style="header")
        if not Confirm.ask(
            f"Apply {preview_info['total_fixes']} fixes to {preview_info['files_to_change']} files?",
            default=False,
        ):
            console.print("❌ Operation cancelled.", style="warning")
            return

        # Ask about backups
        create_backups = Confirm.ask("Create backup files (.bak) before modifying?", default=True)

        # Apply fixes
        results = self.apply_fixes(preview_info, backup=create_backups)

        # Show results
        console.print("\n📊 Application Results", style="header")
        console.print(f"Files modified: {results['files_modified']}", style="success")
        console.print(f"Fixes applied: {results['total_fixes_applied']}", style="success")

        if results["backups_created"]:
            console.print(f"Backups created: {len(results['backups_created'])}", style="info")
            console.print("Backup files have .bak extension", style="info")

        if results["errors"]:
            console.print(f"Errors: {len(results['errors'])}", style="error")
            for error in results["errors"][:3]:  # Show first 3 errors
                console.print(f"  • {error}", style="error")

        console.print("\n✅ Pattern application complete!", style="success")
        console.print("Run your tests to verify the fixes work correctly.", style="info")
