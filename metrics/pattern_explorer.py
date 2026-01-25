"""
Pattern Explorer Module

Provides interactive exploration of the pattern library with search, filtering,
and detailed pattern information.
"""

import json
import re
from pathlib import Path
from typing import Any, Dict, List, Optional

from rich.columns import Columns
from rich.console import Console
from rich.layout import Layout
from rich.panel import Panel
from rich.prompt import Confirm, Prompt
from rich.table import Table
from rich.text import Text
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
        "good": "green",
        "bad": "red",
    }
)

console = Console(theme=custom_theme)


class PatternExplorer:
    """Interactive pattern library explorer."""

    def __init__(self, patterns_file: str = "data/patterns.json"):
        """Initialize pattern explorer.

        Args:
            patterns_file: Path to patterns JSON file
        """
        self.patterns_file = Path(patterns_file)
        self.patterns: List[Dict[str, Any]] = []
        self.filtered_patterns: List[Dict[str, Any]] = []
        self.current_filter = ""
        self.load_patterns()

    def load_patterns(self) -> bool:
        """Load patterns from JSON file.

        Returns:
            True if patterns loaded successfully, False otherwise
        """
        try:
            if self.patterns_file.exists():
                with open(self.patterns_file, "r") as f:
                    data = json.load(f)
                    self.patterns = data.get("patterns", [])
                    self.filtered_patterns = self.patterns.copy()
                return True
            else:
                console.print(f"⚠️  Patterns file not found: {self.patterns_file}", style="warning")
                console.print(
                    "   Run 'feedback-loop analyze' to generate patterns first.", style="info"
                )
                return False
        except Exception as e:
            console.print(f"❌ Error loading patterns: {e}", style="error")
            return False

    def search_patterns(self, query: str) -> List[Dict[str, Any]]:
        """Search patterns by name, description, or category.

        Args:
            query: Search query string

        Returns:
            List of matching patterns
        """
        if not query.strip():
            return self.patterns.copy()

        query_lower = query.lower()
        results = []

        for pattern in self.patterns:
            # Search in name, description, category, and problem/solution
            searchable_fields = [
                pattern.get("name", ""),
                pattern.get("description", ""),
                pattern.get("category", ""),
                pattern.get("problem", ""),
                pattern.get("solution", ""),
            ]

            if any(query_lower in field.lower() for field in searchable_fields if field):
                results.append(pattern)

        return results

    def filter_by_category(self, category: str) -> List[Dict[str, Any]]:
        """Filter patterns by category.

        Args:
            category: Category to filter by

        Returns:
            List of patterns in the specified category
        """
        if not category or category.lower() == "all":
            return self.patterns.copy()

        return [p for p in self.patterns if p.get("category", "").lower() == category.lower()]

    def filter_by_severity(self, severity: str) -> List[Dict[str, Any]]:
        """Filter patterns by severity level.

        Args:
            severity: Severity level (high, medium, low)

        Returns:
            List of patterns with the specified severity
        """
        if not severity or severity.lower() == "all":
            return self.patterns.copy()

        return [p for p in self.patterns if p.get("severity", "").lower() == severity.lower()]

    def sort_patterns(
        self, patterns: List[Dict[str, Any]], sort_by: str = "name"
    ) -> List[Dict[str, Any]]:
        """Sort patterns by specified criteria.

        Args:
            patterns: List of patterns to sort
            sort_by: Sort criteria (name, frequency, severity, success_rate)

        Returns:
            Sorted list of patterns
        """
        if sort_by == "frequency":
            return sorted(patterns, key=lambda p: p.get("frequency", 0), reverse=True)
        elif sort_by == "severity":
            severity_order = {"high": 3, "medium": 2, "low": 1}
            return sorted(
                patterns,
                key=lambda p: severity_order.get(p.get("severity", "low"), 0),
                reverse=True,
            )
        elif sort_by == "success_rate":
            return sorted(patterns, key=lambda p: p.get("success_rate", 0), reverse=True)
        else:  # name
            return sorted(patterns, key=lambda p: p.get("name", ""))

    def get_pattern_categories(self) -> List[str]:
        """Get list of all pattern categories.

        Returns:
            List of unique category names
        """
        categories = set()
        for pattern in self.patterns:
            category = pattern.get("category", "")
            if category:
                categories.add(category)

        return sorted(list(categories))

    def get_pattern_details(self, pattern_name: str) -> Optional[Dict[str, Any]]:
        """Get detailed information about a specific pattern.

        Args:
            pattern_name: Name of the pattern

        Returns:
            Pattern details dictionary or None if not found
        """
        for pattern in self.patterns:
            if pattern.get("name") == pattern_name:
                return pattern
        return None

    def show_pattern_catalog(
        self, patterns: Optional[List[Dict[str, Any]]] = None, show_details: bool = False
    ):
        """Display pattern catalog in a table format.

        Args:
            patterns: List of patterns to display (uses filtered_patterns if None)
            show_details: Whether to show detailed information
        """
        if patterns is None:
            patterns = self.filtered_patterns

        if not patterns:
            console.print("❌ No patterns found matching your criteria.", style="warning")
            return

        if show_details:
            self._show_detailed_catalog(patterns)
        else:
            self._show_compact_catalog(patterns)

    def _show_compact_catalog(self, patterns: List[Dict[str, Any]]):
        """Show compact pattern catalog table."""
        table = Table(
            title=f"Pattern Catalog ({len(patterns)} patterns)",
            show_header=True,
            header_style="bold blue",
        )
        table.add_column("Name", style="cyan", no_wrap=True)
        table.add_column("Category", style="green")
        table.add_column("Severity", style="yellow", justify="center")
        table.add_column("Frequency", style="magenta", justify="right")
        table.add_column("Success Rate", style="blue", justify="right")

        for pattern in patterns:
            name = pattern.get("name", "unknown")
            category = pattern.get("category", "general")
            severity = pattern.get("severity", "medium")
            frequency = pattern.get("frequency", 0)
            success_rate = pattern.get("success_rate", 0)

            # Color code severity
            severity_color = {"high": "red", "medium": "yellow", "low": "green"}.get(
                severity, "white"
            )

            table.add_row(
                name,
                category,
                f"[{severity_color}]{severity}[/{severity_color}]",
                str(frequency),
                f"{success_rate:.0%}" if success_rate else "N/A",
            )

        console.print(table)

    def _show_detailed_catalog(self, patterns: List[Dict[str, Any]]):
        """Show detailed pattern catalog with descriptions."""
        for i, pattern in enumerate(patterns, 1):
            name = pattern.get("name", "unknown")
            description = pattern.get("description", "")
            category = pattern.get("category", "general")
            severity = pattern.get("severity", "medium")
            frequency = pattern.get("frequency", 0)

            # Header
            header_text = f"{i}. {name}"
            if frequency > 0:
                header_text += f" ({frequency} occurrences)"

            console.print(f"\n[bold blue]{header_text}[/bold blue]")
            console.print(
                f"[green]Category:[/green] {category} | [yellow]Severity:[/yellow] {severity}"
            )

            # Description
            if description:
                console.print(f"[cyan]Description:[/cyan] {description}")

            # Problem/Solution if available
            problem = pattern.get("problem", "")
            solution = pattern.get("solution", "")

            if problem:
                console.print(
                    f"[red]Problem:[/red] {problem[:100]}{'...' if len(problem) > 100 else ''}"
                )

            if solution:
                console.print(
                    f"[green]Solution:[/green] {solution[:100]}{'...' if len(solution) > 100 else ''}"
                )

    def show_pattern_detail(self, pattern: Dict[str, Any]):
        """Show detailed information about a single pattern.

        Args:
            pattern: Pattern dictionary
        """
        name = pattern.get("name", "unknown")
        description = pattern.get("description", "")
        category = pattern.get("category", "general")
        severity = pattern.get("severity", "medium")
        problem = pattern.get("problem", "")
        solution = pattern.get("solution", "")
        frequency = pattern.get("frequency", 0)
        success_rate = pattern.get("success_rate", 0)

        # Header
        header_panel = Panel.fit(
            f"[bold blue]{name}[/bold blue]\n"
            f"[green]Category:[/green] {category} | "
            f"[yellow]Severity:[/yellow] {severity} | "
            f"[magenta]Frequency:[/magenta] {frequency}",
            border_style="blue",
        )
        console.print(header_panel)

        # Description
        if description:
            desc_panel = Panel.fit(
                f"[cyan]{description}[/cyan]", title="Description", border_style="cyan"
            )
            console.print(desc_panel)

        # Problem and Solution
        if problem or solution:
            prob_sol_layout = Layout()

            if problem:
                prob_panel = Panel.fit(problem, title="[red]❌ Problem[/red]", border_style="red")
                prob_sol_layout.split_row(
                    Layout(prob_panel, name="problem", size=50), Layout(name="solution", size=50)
                )
            else:
                prob_sol_layout.add_split(Layout(name="solution"))

            if solution:
                sol_panel = Panel.fit(
                    solution, title="[green]✅ Solution[/green]", border_style="green"
                )
                if "problem" in prob_sol_layout:
                    prob_sol_layout["solution"].update(sol_panel)
                else:
                    prob_sol_layout.update(sol_panel)

            console.print(prob_sol_layout)

        # Code Examples
        bad_example = pattern.get("bad_example", "")
        good_example = pattern.get("good_example", "")

        if bad_example or good_example:
            console.print("\n[bold]Code Examples:[/bold]")

            examples_layout = Layout()

            if bad_example:
                bad_panel = Panel.fit(
                    bad_example.strip(), title="[red]❌ Bad Example[/red]", border_style="red"
                )
                examples_layout.split_row(
                    Layout(bad_panel, name="bad", size=40), Layout(name="good", size=40)
                )
            else:
                examples_layout.add_split(Layout(name="good"))

            if good_example:
                good_panel = Panel.fit(
                    good_example.strip(),
                    title="[green]✅ Good Example[/green]",
                    border_style="green",
                )
                if "bad" in examples_layout:
                    examples_layout["good"].update(good_panel)
                else:
                    examples_layout.update(good_panel)

            console.print(examples_layout)

        # Statistics
        if frequency > 0 or success_rate > 0:
            stats_text = ""
            if frequency > 0:
                stats_text += f"Frequency: {frequency} occurrences\n"
            if success_rate > 0:
                stats_text += f"Success Rate: {success_rate:.0%}"

            if stats_text:
                stats_panel = Panel.fit(
                    stats_text.strip(), title="[blue]📊 Statistics[/blue]", border_style="blue"
                )
                console.print(f"\n{stats_panel}")

    def interactive_search(self):
        """Run interactive search and filter interface."""
        console.print("\n[bold blue]🔍 Pattern Explorer[/bold blue]")
        console.print("Search and explore the pattern library interactively.\n")

        while True:
            # Show current filter status
            if self.current_filter:
                console.print(
                    f"[cyan]Current filter: '{self.current_filter}' ({len(self.filtered_patterns)} results)[/cyan]"
                )
            else:
                console.print(
                    f"[cyan]Showing all patterns ({len(self.filtered_patterns)} total)[/cyan]"
                )

            # Main menu
            console.print("\n[bold]Options:[/bold]")
            console.print("  1. 🔍 Search patterns")
            console.print("  2. 🏷️  Filter by category")
            console.print("  3. ⚠️  Filter by severity")
            console.print("  4. 📋 Show catalog")
            console.print("  5. 📖 View pattern details")
            console.print("  6. 🎮 Try pattern playground")
            console.print("  7. 🔄 Clear filters")
            console.print("  8. 🚪 Exit")

            choice = Prompt.ask(
                "\nChoose an option", choices=["1", "2", "3", "4", "5", "6", "7", "8"], default="4"
            )

            if choice == "1":
                query = Prompt.ask("Enter search query")
                self.filtered_patterns = self.search_patterns(query)
                self.current_filter = f"search: {query}"

            elif choice == "2":
                categories = ["all"] + self.get_pattern_categories()
                category = Prompt.ask("Choose category", choices=categories, default="all")
                self.filtered_patterns = self.filter_by_category(category)
                self.current_filter = f"category: {category}"

            elif choice == "3":
                severity = Prompt.ask(
                    "Choose severity", choices=["all", "high", "medium", "low"], default="all"
                )
                self.filtered_patterns = self.filter_by_severity(severity)
                self.current_filter = f"severity: {severity}"

            elif choice == "4":
                show_detailed = Confirm.ask("Show detailed view?", default=False)
                self.show_pattern_catalog(show_details=show_detailed)

            elif choice == "5":
                if not self.filtered_patterns:
                    console.print(
                        "❌ No patterns to show. Try clearing filters or searching.", style="warning"
                    )
                    continue

                # Show pattern list for selection
                console.print("\nAvailable patterns:")
                for i, pattern in enumerate(self.filtered_patterns, 1):
                    name = pattern.get("name", "unknown")
                    console.print(f"  {i}. {name}")

                try:
                    pattern_choice = int(Prompt.ask("Choose pattern number"))
                    if 1 <= pattern_choice <= len(self.filtered_patterns):
                        selected_pattern = self.filtered_patterns[pattern_choice - 1]
                        self.show_pattern_detail(selected_pattern)
                    else:
                        console.print("❌ Invalid pattern number.", style="error")
                except ValueError:
                    console.print("❌ Please enter a valid number.", style="error")

            elif choice == "6":
                # Import here to avoid circular imports
                from metrics.pattern_playground import PatternPlayground

                playground = PatternPlayground()
                playground.run(self.filtered_patterns)

            elif choice == "7":
                self.filtered_patterns = self.patterns.copy()
                self.current_filter = ""
                console.print("✅ Filters cleared.", style="success")

            elif choice == "8":
                console.print("\n👋 Happy exploring!", style="success")
                break

            # Pause before showing menu again
            if choice in ["1", "2", "3", "7"]:
                input("\nPress Enter to continue...")

    def export_patterns(self, output_file: str, patterns: Optional[List[Dict[str, Any]]] = None):
        """Export patterns to a file.

        Args:
            output_file: Output file path
            patterns: Patterns to export (uses filtered_patterns if None)
        """
        if patterns is None:
            patterns = self.filtered_patterns

        try:
            with open(output_file, "w") as f:
                json.dump(
                    {"patterns": patterns, "exported_at": str(Path(output_file).absolute())},
                    f,
                    indent=2,
                )
            console.print(f"✅ Patterns exported to {output_file}", style="success")
        except Exception as e:
            console.print(f"❌ Export failed: {e}", style="error")
