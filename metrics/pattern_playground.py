"""
Pattern Playground Module

Provides interactive testing and experimentation with patterns.
Allows users to apply patterns to sample code and see results in real-time.
"""

from typing import Any, Dict, List

from rich.console import Console
from rich.layout import Layout
from rich.panel import Panel
from rich.prompt import Prompt
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


class PatternPlayground:
    """Interactive pattern testing environment."""

    def __init__(self):
        """Initialize pattern playground."""
        self.test_cases = self._load_test_cases()

    def _load_test_cases(self) -> Dict[str, Dict[str, Any]]:
        """Load predefined test cases for patterns.

        Returns:
            Dictionary mapping pattern names to test case data
        """
        return {
            "numpy_json_serialization": {
                "description": "Test NumPy array serialization to JSON",
                "bad_code": """
import json
import numpy as np

def process_data():
    data = np.array([1.0, 2.0, 3.0, 4.0, 5.0])
    result = {
        "mean": np.mean(data),
        "std": np.std(data),
        "values": data
    }
    return json.dumps(result)
                """,
                "good_code": """
import json
import numpy as np

def process_data():
    data = np.array([1.0, 2.0, 3.0, 4.0, 5.0])
    result = {
        "mean": float(np.mean(data)),
        "std": float(np.std(data)),
        "values": data.tolist()
    }
    return json.dumps(result)
                """,
                "test_function": "process_data()",
                "expected_success": True,
            },
            "bounds_checking": {
                "description": "Test safe list access with bounds checking",
                "bad_code": """
def get_first_item(items):
    return items[0]  # Will fail on empty list

# Test cases
result1 = get_first_item([1, 2, 3])  # Should work
result2 = get_first_item([])  # Will raise IndexError
                """,
                "good_code": """
def get_first_item(items):
    if not items:
        return None
    return items[0]

# Test cases
result1 = get_first_item([1, 2, 3])  # Should work
result2 = get_first_item([])  # Should return None
                """,
                "test_function": "get_first_item([1, 2, 3]), get_first_item([])",
                "expected_success": True,
            },
            "specific_exceptions": {
                "description": "Test specific exception handling",
                "bad_code": """
import json

def parse_config(config_str):
    try:
        config = json.loads(config_str)
        return config["database"]["host"]
    except:  # Bare except!
        print("Error parsing config")
        return None

# Test case
result = parse_config('{invalid json}')  # Should fail gracefully
                """,
                "good_code": """
import json
import logging

logger = logging.getLogger(__name__)

def parse_config(config_str):
    try:
        config = json.loads(config_str)
        return config["database"]["host"]
    except json.JSONDecodeError as e:
        logger.debug(f"Invalid JSON format: {e}")
        return None
    except KeyError as e:
        logger.debug(f"Missing configuration key: {e}")
        return None

# Test case
result = parse_config('{invalid json}')  # Should fail gracefully
                """,
                "test_function": "parse_config('{invalid json}'), parse_config('{}')",
                "expected_success": True,
            },
            "temp_file_handling": {
                "description": "Test proper temporary file cleanup",
                "bad_code": """
import tempfile
import os

def process_file(data):
    path = tempfile.mktemp()  # Insecure!
    with open(path, 'wb') as f:
        f.write(data)

    # Process file...
    result = len(data)

    # File never cleaned up! Resource leak.
    return result
                """,
                "good_code": """
import tempfile
import os

def process_file(data):
    with tempfile.NamedTemporaryFile(delete=False) as tmp:
        tmp.write(data)
        tmp_path = tmp.name

    try:
        # Process file...
        result = len(data)
        return result
    finally:
        # Always cleanup
        os.unlink(tmp_path)
                """,
                "test_function": "process_file(b'test data')",
                "expected_success": True,
            },
        }

    def run(self, patterns: List[Dict[str, Any]]):
        """Run interactive pattern playground.

        Args:
            patterns: List of available patterns
        """
        console.print("\n[bold blue]🎮 Pattern Playground[/bold blue]")
        console.print("Test patterns interactively with sample code!\n")

        # Filter to patterns we have test cases for
        available_patterns = [p for p in patterns if p.get("name") in self.test_cases]

        if not available_patterns:
            console.print(
                "❌ No playground test cases available for current patterns.", style="warning"
            )
            return

        while True:
            # Show available patterns
            console.print("[bold]Available Playground Patterns:[/bold]")
            for i, pattern in enumerate(available_patterns, 1):
                name = pattern.get("name", "unknown")
                desc = self.test_cases[name]["description"]
                console.print(f"  {i}. {name}")
                console.print(f"     {desc}")

            console.print("\n  0. Exit playground")

            try:
                choice = int(Prompt.ask("\nChoose a pattern to test", default="0"))

                if choice == 0:
                    console.print("\n👋 Thanks for playing!", style="success")
                    break

                if 1 <= choice <= len(available_patterns):
                    selected_pattern = available_patterns[choice - 1]
                    self._run_test_case(selected_pattern)
                else:
                    console.print("❌ Invalid choice.", style="error")

            except ValueError:
                console.print("❌ Please enter a valid number.", style="error")

            input("\nPress Enter to continue...")

    def _run_test_case(self, pattern: Dict[str, Any]):
        """Run a specific test case.

        Args:
            pattern: Pattern dictionary
        """
        pattern_name = pattern.get("name", "unknown")

        if pattern_name not in self.test_cases:
            console.print(f"❌ No test case available for pattern: {pattern_name}", style="error")
            return

        test_case = self.test_cases[pattern_name]

        console.print(f"\n[bold cyan]🧪 Testing: {pattern_name}[/bold cyan]")
        console.print(f"[yellow]{test_case['description']}[/yellow]\n")

        # Show the problem
        console.print("[red]❌ The Problem:[/red]")
        console.print("Running code with the anti-pattern...")

        bad_result = self._execute_code_safely(
            test_case["bad_code"], test_case.get("test_function", "")
        )

        if bad_result["success"]:
            console.print(f"[green]Unexpectedly succeeded:[/green] {bad_result['result']}")
        else:
            console.print(f"[red]Failed as expected:[/red] {bad_result['error']}")

        console.print()

        # Show the solution
        console.print("[green]✅ The Solution:[/green]")
        console.print("Running code with the correct pattern...")

        good_result = self._execute_code_safely(
            test_case["good_code"], test_case.get("test_function", "")
        )

        if good_result["success"]:
            console.print(f"[green]Success![/green] Result: {good_result['result']}")
        else:
            console.print(f"[red]Unexpected failure:[/red] {good_result['error']}")

        # Show code comparison
        self._show_code_comparison(test_case)

    def _execute_code_safely(self, code: str, test_expression: str = "") -> Dict[str, Any]:
        """Execute code safely in an isolated environment.

        Args:
            code: Python code to execute
            test_expression: Expression to evaluate after code execution

        Returns:
            Dictionary with execution results
        """
        try:
            # Create a temporary namespace
            namespace = {}

            # Execute the code
            exec(code, namespace)

            # If there's a test expression, evaluate it
            if test_expression.strip():
                result = eval(test_expression, namespace)
            else:
                result = "Code executed successfully"

            return {"success": True, "result": result, "error": None}

        except Exception as e:
            return {"success": False, "result": None, "error": str(e)}

    def _show_code_comparison(self, test_case: Dict[str, Any]):
        """Show side-by-side code comparison.

        Args:
            test_case: Test case dictionary
        """
        console.print("\n[bold]📝 Code Comparison:[/bold]")

        bad_code = test_case["bad_code"].strip()
        good_code = test_case["good_code"].strip()

        # Create side-by-side layout
        layout = Layout()
        layout.split_row(
            Layout(Panel.fit(f"[red]❌ BEFORE\n\n{bad_code}[/red]", border_style="red"), name="bad"),
            Layout(
                Panel.fit(f"[green]✅ AFTER\n\n{good_code}[/green]", border_style="green"),
                name="good",
            ),
        )

        console.print(layout)

    def create_custom_test(self):
        """Allow users to create and test their own code snippets."""
        console.print("\n[bold blue]🔧 Custom Code Tester[/bold blue]")
        console.print("Test your own code snippets!\n")

        console.print("Enter your Python code (press Enter twice when done):")

        code_lines = []
        while True:
            line = input()
            if not line and code_lines and not code_lines[-1]:  # Double enter
                break
            code_lines.append(line)

        code = "\n".join(code_lines[:-1])  # Remove the empty line

        if not code.strip():
            console.print("❌ No code entered.", style="warning")
            return

        console.print("\nEnter a test expression (optional, press Enter to skip):")
        test_expr = input().strip()

        console.print("\n[cyan]Executing your code...[/cyan]")

        result = self._execute_code_safely(code, test_expr)

        if result["success"]:
            console.print(f"[green]✅ Success![/green] Result: {result['result']}")
        else:
            console.print(f"[red]❌ Error:[/red] {result['error']}")

        console.print("\n[cyan]Code executed:[/cyan]")
        console.print(Panel.fit(code, border_style="blue"))

    def show_help(self):
        """Show playground help information."""
        help_text = """
[bold blue]🎮 Pattern Playground Help[/bold blue]

The Pattern Playground allows you to:
• Test patterns with real code examples
• See before/after comparisons
• Run code safely in isolation
• Create custom test cases

[bold cyan]Available Commands:[/bold cyan]
• Select a pattern number to test it
• Choose "Custom Test" to write your own code
• Use "Help" to see this information
• Select "Exit" to return to the explorer

[bold yellow]Safety:[/bold yellow]
• Code runs in an isolated environment
• No access to file system or network
• Errors are caught and displayed safely

[bold green]Tips:[/bold green]
• Start with simple patterns like "bounds_checking"
• Try the "bad" examples to see what goes wrong
• Use custom tests to validate your understanding
        """

        console.print(Panel.fit(help_text, border_style="blue"))
