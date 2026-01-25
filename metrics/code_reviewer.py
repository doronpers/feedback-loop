"""
Interactive Code Review Module

Provides LLM-powered code review with pattern suggestions and best practices.
"""

import logging
import re
from typing import Any, Dict, List, Optional

from metrics.config_manager import ConfigManager
from metrics.llm_providers import get_llm_manager
from metrics.pattern_manager import PatternManager

logger = logging.getLogger(__name__)


class CodeReviewer:
    """Interactive code reviewer with LLM assistance."""

    def __init__(self, llm_provider: Optional[str] = None, llm_client: Optional[object] = None, metrics_collector: Optional[object] = None):
        """Initialize code reviewer.

        Args:
            llm_provider: Preferred LLM provider
            llm_client: Optional `LLMClient` instance to use instead of the legacy
                provider manager. This allows tests to inject a `MockProvider`.
            metrics_collector: Optional `MetricsCollector` instance; if provided,
                its telemetry callback will be attached to the `LLMClient` created
                by this component so LLM call telemetry is recorded.
        """
        self.config = ConfigManager()
        self.llm_manager = get_llm_manager()
        if llm_provider:
            self.llm_manager.preferred_provider = llm_provider

        # Prefer an injected llm_client (new style). If a metrics_collector is
        # supplied and no client was injected, create a client with telemetry.
        self.llm_client = llm_client
        if self.llm_client is None and metrics_collector is not None:
            try:
                # Local import to avoid import cycles in tests
                from feedback_loop.llm import get_llm_client

                telemetry_cb = metrics_collector.get_telemetry_callback()
                self.llm_client = get_llm_client(telemetry_callback=telemetry_cb)
            except Exception:
                # Fall back to legacy manager if anything goes wrong
                logger.exception("Failed to initialize LLM client with telemetry; falling back to LLM manager")
                self.llm_client = None

        self.pattern_manager = PatternManager()
        self.patterns = self.pattern_manager.get_all_patterns()
    def _call_llm(self, prompt: str, max_tokens: int) -> Dict[str, Any]:
        """Unified call helper that supports both the legacy LLMManager and the
        new `LLMClient` interface. Returns a dict with at least the `text`
        key and optional `provider` and `model` keys.
        """
        # Prefer LLMClient if available
        if getattr(self, "llm_client", None) is not None:
            result = self.llm_client.call(prompt, max_tokens=max_tokens)
            if isinstance(result, dict):
                return {
                    "text": result.get("text"),
                    "provider": result.get("provider"),
                    "model": result.get("model"),
                }
            # Fallback to attribute access
            return {
                "text": getattr(result, "text", None),
                "provider": getattr(result, "provider", None),
                "model": getattr(result, "model", None),
            }

        # Legacy manager path
        response = self.llm_manager.generate(prompt, max_tokens=max_tokens, fallback=True)
        return {"text": response.text, "provider": response.provider, "model": response.model}
    def review_code(self, code: str, context: Optional[str] = None) -> Dict[str, Any]:
        """Review code with pattern awareness.

        Args:
            code: Code to review
            context: Optional context about the code

        Returns:
            Dictionary with review results including debrief
        """
        # Input validation
        if not code or not code.strip():
            return {
                "error": "No code provided for review.",
                "suggestions": [],
                "debrief": {
                    "strategies": ["Provide valid code for review."],
                    "difficulty": 1,
                    "explanation": "No code was provided for review.",
                },
            }

        max_code_size = self.config.get("code_review.max_code_size", 50000)
        if len(code) > max_code_size:
            return {
                "error": (
                    f"Code too large for review (max {max_code_size} bytes). "
                    "Please review in smaller chunks."
                ),
                "suggestions": [],
                "debrief": {
                    "strategies": ["Break the code into smaller, logical chunks for review."],
                    "difficulty": 2,
                    "explanation": "Code exceeded size limit for review.",
                },
            }

        if not (getattr(self, "llm_client", None) is not None or self.llm_manager.is_any_available()):
            return {
                "error": "No LLM providers available. Set API keys to use code review.",
                "suggestions": [],
                "debrief": {
                    "strategies": [
                        "Set up API keys for ANTHROPIC_API_KEY, OPENAI_API_KEY, or GEMINI_API_KEY."
                    ],
                    "difficulty": 2,
                    "explanation": "Cannot generate review or debrief without LLM access.",
                },
            }

        # Build review prompt
        prompt = self._build_review_prompt(code, context)

        try:
            # Get LLM review
            max_tokens = self.config.get("code_review.max_tokens", 2048)
            response = self._call_llm(prompt, max_tokens)

            # Generate debrief
            debrief = self.generate_debrief(code, response["text"], context)

            # Parse response
            return {
                "review": response["text"],
                "provider": response.get("provider"),
                "model": response.get("model"),
                "debrief": debrief,
            }

        except Exception as e:
            logger.error(f"Code review failed: {e}")
            return {
                "error": f"Code review failed: {e}",
                "suggestions": [],
                "debrief": {
                    "strategies": [
                        "Check if the LLM service is available and responding.",
                        "Verify API keys are valid and have sufficient quota.",
                        "Try again after a short wait if this is a temporary service issue.",
                    ],
                    "difficulty": 3,
                    "explanation": "Review failed due to an error during processing.",
                },
            }

    def _build_review_prompt(self, code: str, context: Optional[str] = None) -> str:
        """Build review prompt with pattern context.

        Args:
            code: Code to review
            context: Optional context

        Returns:
            Review prompt
        """
        prompt = """You are an expert code reviewer for the feedback-loop framework.

Review the following Python code and provide:
1. Pattern violations or missing patterns
2. Potential bugs or issues
3. Best practice improvements
4. Specific, actionable suggestions

Focus on these key patterns:
"""

        # Add key patterns
        for pattern in self.patterns[:5]:  # Top 5 patterns
            name = pattern.get("name", "")
            desc = pattern.get("description", "")
            prompt += f"- **{name}**: {desc}\n"

        prompt += "\n## Code to Review:\n\n```python\n"
        prompt += code
        prompt += "\n```\n"

        if context:
            prompt += f"\n## Context:\n{context}\n"

        prompt += """
## Review Guidelines:
- Be specific and actionable
- Reference patterns by name when applicable
- Prioritize critical issues
- Suggest concrete code improvements
- Keep feedback concise but thorough
"""

        return prompt

    def explain_issue(self, issue_description: str) -> str:
        """Get detailed explanation of a code issue.

        Args:
            issue_description: Description of the issue

        Returns:
            Detailed explanation
        """
        if not (getattr(self, "llm_client", None) is not None or self.llm_manager.is_any_available()):
            return "No LLM providers available. Set API keys to use this feature."

        prompt = f"""Explain this Python code issue in detail:

{issue_description}

Provide:
1. What the issue is
2. Why it's a problem
3. How to fix it
4. Example of correct code
5. Related best practices

Keep it practical and code-focused."""

        try:
            max_tokens = self.config.get("code_review.max_tokens_explain", 1500)
            response = self._call_llm(prompt, max_tokens)
            return response["text"]
        except Exception as e:
            logger.error(f"Explanation failed: {e}")
            return f"Could not generate explanation: {e}"

    def suggest_improvements(self, code: str, goal: str) -> str:
        """Suggest improvements to achieve a specific goal.

        Args:
            code: Current code
            goal: Improvement goal (e.g., "make it more efficient")

        Returns:
            Improvement suggestions
        """
        if not (getattr(self, "llm_client", None) is not None or self.llm_manager.is_any_available()):
            return "No LLM providers available. Set API keys to use this feature."

        prompt = f"""Given this Python code:

```python
{code}
```

Goal: {goal}

Suggest specific improvements with:
1. What to change and why
2. Updated code snippets
3. Expected benefits

Keep suggestions practical and pattern-aware."""

        try:
            max_tokens = self.config.get("code_review.max_tokens_suggest", 2048)
            response = self._call_llm(prompt, max_tokens)
            return response["text"]
        except Exception as e:
            logger.error(f"Suggestions failed: {e}")
            return f"Could not generate suggestions: {e}"

    def generate_debrief(
        self, code: str, review: str, context: Optional[str] = None
    ) -> Dict[str, Any]:
        """Generate a debrief with improvement strategies and difficulty rating.

        Args:
            code: The code that was reviewed
            review: The review feedback provided
            context: Optional context about the code

        Returns:
            Dictionary containing improvement strategies and difficulty rating
        """
        if not (getattr(self, "llm_client", None) is not None or self.llm_manager.is_any_available()):
            return {
                "strategies": ["No LLM providers available. Set API keys to use this feature."],
                "difficulty": 5,
                "explanation": "Cannot generate debrief without LLM access.",
            }

        prompt = """Based on the code review provided, generate a debrief that includes:

1. **Improvement Strategies**: 3-5 specific, actionable strategies the
   developer can use to improve their code quality and avoid similar issues in
   future submissions.
2. **Difficulty Rating**: Rate the difficulty of executing these improvements
   on a scale of 1-10, where:
   - 1-3: Easy (simple changes, no architectural impact)
   - 4-6: Moderate (requires refactoring or new patterns)
   - 7-9: Hard (significant architectural changes or deep understanding needed)
   - 10: Very Hard (requires extensive rewrite or advanced expertise)

## Code Reviewed:
```python
{code}
```

## Review Feedback:
{review}
"""

        if context:
            prompt += f"\n## Context:\n{context}\n"

        prompt += """
## Output Format:
Provide your response in the following format:

**Improvement Strategies:**
1. [Strategy 1]
2. [Strategy 2]
3. [Strategy 3]
...

**Difficulty Rating:** [1-10]

**Explanation:**
[Brief explanation of why this difficulty rating was assigned and what makes
these improvements more or less challenging]
"""

        try:
            max_tokens = self.config.get("code_review.max_tokens_debrief", 1500)
            response = self._call_llm(prompt, max_tokens)

            # Parse the response
            debrief_text = response["text"]
            strategies = []
            difficulty = 5
            explanation = ""

            # Extract strategies
            if "**Improvement Strategies:**" in debrief_text:
                strategies_section = debrief_text.split("**Improvement Strategies:**")[1]
                if "**Difficulty Rating:**" in strategies_section:
                    strategies_section = strategies_section.split("**Difficulty Rating:**")[0]

                # Parse numbered list using regex for better handling
                lines = strategies_section.strip().split("\n")
                for line in lines:
                    line = line.strip()
                    if line:
                        # Match numbered lists (1., 2., etc), bullet points (-, *), or simple text
                        # Pattern: optional number/bullet + optional space + content
                        match = re.match(r"^(?:\d+\.|\*|\-)?\s*(.+)$", line)
                        if match:
                            clean_line = match.group(1).strip()
                            if clean_line:
                                strategies.append(clean_line)

            # Extract difficulty rating
            if "**Difficulty Rating:**" in debrief_text:
                rating_section = debrief_text.split("**Difficulty Rating:**")[1]
                if "**Explanation:**" in rating_section:
                    rating_text = rating_section.split("**Explanation:**")[0].strip()
                else:
                    rating_text = rating_section.strip().split("\n")[0].strip()

                # Extract number from the beginning of rating text
                numbers = re.findall(r"^\s*(\d+)", rating_text)
                if numbers:
                    difficulty = min(10, max(1, int(numbers[0])))

            # Extract explanation
            if "**Explanation:**" in debrief_text:
                explanation = debrief_text.split("**Explanation:**")[1].strip()

            # Fallback if parsing failed
            if not strategies:
                strategies = [debrief_text]

            return {
                "strategies": strategies,
                "difficulty": difficulty,
                "explanation": explanation,
            }

        except Exception as e:
            logger.error(f"Debrief generation failed: {e}")
            return {
                "strategies": [f"Could not generate debrief: {e}"],
                "difficulty": 5,
                "explanation": "Error during debrief generation.",
            }


class CouncilCodeReviewer:
    """Multi-perspective code reviewer using Council AI with HTTP fallback."""

    def __init__(
        self,
        prefer_local: Optional[bool] = None,
        http_base_url: Optional[str] = None,
        timeout_seconds: Optional[float] = None,
        provider: Optional[str] = None,
    ):
        self.config = ConfigManager()
        self.pattern_manager = PatternManager()
        self.patterns = self.pattern_manager.get_all_patterns()

        self.prefer_local = (
            prefer_local
            if prefer_local is not None
            else self.config.get("council_review.prefer_local", True)
        )
        self.http_base_url = http_base_url or self.config.get(
            "council_review.http_base_url", "http://localhost:8000/api/consult"
        )
        self.timeout_seconds = timeout_seconds or self.config.get(
            "council_review.http_timeout_seconds", 60
        )
        self.domain = self.config.get("council_review.domain", "coding")
        self.mode = self.config.get("council_review.mode", "synthesis")
        self.temperature = self.config.get("council_review.temperature", 0.4)
        self.max_tokens = self.config.get("council_review.max_tokens", 1200)
        self.provider = provider or self.config.get("council_review.provider")

    def review_code(
        self, code: str, context: Optional[str] = None, api_key: Optional[str] = None
    ) -> Dict[str, Any]:
        """Review code with Council AI, falling back to HTTP API."""
        if not code or not code.strip():
            return {"error": "No code provided for review.", "responses": []}

        prompt = self._build_review_prompt(code, context)

        if self.prefer_local:
            local_result = self._review_local(prompt, api_key)
            if local_result:
                return local_result

        return self._review_http(prompt, api_key)

    def _build_review_prompt(self, code: str, context: Optional[str] = None) -> str:
        """Build review prompt with pattern context for council review."""
        prompt = """You are a multi-perspective code reviewer.

Provide:
1. Security concerns
2. Design clarity issues
3. Cognitive load and maintainability concerns
4. Risk and edge-case warnings
5. Actionable fixes

Focus on these key patterns:
"""
        for pattern in self.patterns[:5]:
            name = pattern.get("name", "")
            desc = pattern.get("description", "")
            prompt += f"- **{name}**: {desc}\n"

        prompt += "\n## Code to Review:\n\n```python\n"
        prompt += code
        prompt += "\n```\n"

        if context:
            prompt += f"\n## Context:\n{context}\n"

        return prompt

    def _review_local(self, prompt: str, api_key: Optional[str]) -> Optional[Dict[str, Any]]:
        """Attempt local Council AI review."""
        try:
            from council_ai import Council
        except ImportError:
            return None

        try:
            council = self._build_local_council(Council, api_key)
            result = council.consult(prompt)
            responses = [self._serialize_response(r) for r in result.responses]
            return {
                "review": result.synthesis,
                "responses": responses,
                "mode": result.mode,
                "source": "council_local",
            }
        except Exception as e:
            logger.error(f"Council local review failed: {e}")
            return None

    def _review_http(self, prompt: str, api_key: Optional[str]) -> Dict[str, Any]:
        """Review code using Council AI HTTP consult endpoint."""
        try:
            import requests
        except ImportError as e:
            return {"error": f"requests library not available: {e}", "responses": []}

        payload = {
            "query": prompt,
            "context": None,
            "domain": self.domain,
            "mode": self.mode,
            "provider": self.provider,
            "api_key": api_key,
            "temperature": self.temperature,
            "max_tokens": self.max_tokens,
        }

        try:
            response = requests.post(self.http_base_url, json=payload, timeout=self.timeout_seconds)
            if not response.ok:
                return {
                    "error": f"HTTP review failed: {response.status_code} - {response.text}",
                    "responses": [],
                }

            data = response.json()
            return {
                "review": data.get("synthesis"),
                "responses": data.get("responses", []),
                "mode": data.get("mode"),
                "source": "council_http",
            }
        except requests.exceptions.Timeout:
            return {
                "error": f"HTTP review timeout after {self.timeout_seconds}s",
                "responses": [],
            }
        except requests.exceptions.ConnectionError as e:
            return {"error": f"HTTP connection error: {e}", "responses": []}
        except Exception as e:
            return {"error": f"HTTP review failed: {e}", "responses": []}

    def _build_local_council(self, council_cls: Any, api_key: Optional[str]) -> Any:
        """Construct Council instance with optional provider override."""
        if self.provider:
            try:
                return council_cls.for_domain(self.domain, api_key=api_key, provider=self.provider)
            except TypeError:
                return council_cls.for_domain(self.domain, api_key=api_key)
        return council_cls.for_domain(self.domain, api_key=api_key)

    def _serialize_response(self, response: Any) -> Dict[str, Any]:
        """Serialize a Council response for output."""
        persona = getattr(response, "persona", None)
        return {
            "persona": {
                "id": getattr(persona, "id", None),
                "name": getattr(persona, "name", None),
                "title": getattr(persona, "title", None),
            }
            if persona
            else None,
            "content": getattr(response, "content", None),
            "error": getattr(response, "error", None),
        }

    def review_with_visual_diff(self, code: str, context: Optional[str] = None) -> Dict[str, Any]:
        """Review code and generate visual diff showing pattern applications.

        Args:
            code: Code to review
            context: Optional context about the code

        Returns:
            Dictionary with review results and visual diff information
        """
        # First get the regular review
        review_result = self.review_code(code, context)

        if "error" in review_result:
            return review_result

        # Generate pattern connections
        pattern_connections = self.get_pattern_connections(code)

        # Generate visual diff
        visual_diff = self._generate_visual_diff(code, pattern_connections)

        # Add visual elements to result
        review_result.update(
            {
                "pattern_connections": pattern_connections,
                "visual_diff": visual_diff,
                "diff_summary": self._summarize_diff(pattern_connections),
            }
        )

        return review_result

    def get_pattern_connections(self, code: str) -> Dict[str, Any]:
        """Map code sections to relevant patterns.

        Args:
            code: Code to analyze

        Returns:
            Dictionary mapping code patterns to relevant feedback-loop patterns
        """
        connections: Dict[str, Any] = {
            "detected_patterns": [],
            "pattern_matches": {},
            "confidence_scores": {},
            "code_sections": [],
        }

        # Analyze code for pattern violations using regex
        pattern_checks = {
            "numpy_json_serialization": {
                "regex": r"json\.dumps\([^)]*np\.|json\.dumps\([^)]*numpy",
                "description": "NumPy types in JSON serialization",
                "severity": "high",
            },
            "bounds_checking": {
                "regex": r"\w+\[0\](?!\s+if\s+\w+)",
                "description": "List access without bounds checking",
                "severity": "medium",
            },
            "specific_exceptions": {
                "regex": r"except\s*:",
                "description": "Bare except clause",
                "severity": "medium",
            },
            "structured_logging": {
                "regex": r"\bprint\s*\(",
                "description": "Using print instead of logging",
                "severity": "low",
            },
            "temp_file_handling": {
                "regex": r"tempfile\.mktemp\(",
                "description": "Using deprecated mktemp function",
                "severity": "high",
            },
        }

        lines = code.split("\n")
        for line_num, line in enumerate(lines, 1):
            for pattern_name, pattern_info in pattern_checks.items():
                if re.search(pattern_info["regex"], line):
                    connections["detected_patterns"].append(
                        {
                            "pattern": pattern_name,
                            "line": line_num,
                            "code": line.strip(),
                            "description": pattern_info["description"],
                            "severity": pattern_info["severity"],
                            "confidence": 0.8,  # Default confidence
                        }
                    )

                    if pattern_name not in connections["pattern_matches"]:
                        connections["pattern_matches"][pattern_name] = []

                    connections["pattern_matches"][pattern_name].append(
                        {"line": line_num, "code": line.strip()}
                    )

        # Calculate confidence scores
        for pattern_name in connections["pattern_matches"]:
            match_count = len(connections["pattern_matches"][pattern_name])
            connections["confidence_scores"][pattern_name] = min(0.9, 0.6 + (match_count * 0.1))

        return connections

    def generate_quick_fixes(self, review_result: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate actionable quick fixes with explanations.

        Args:
            review_result: Result from code review

        Returns:
            List of quick fix suggestions
        """
        fixes: List[Dict[str, Any]] = []

        if "pattern_connections" not in review_result:
            return fixes

        pattern_connections = review_result["pattern_connections"]

        # Generate fixes for each detected pattern
        fix_templates = {
            "numpy_json_serialization": {
                "title": "Convert NumPy types for JSON serialization",
                "fix": "Use float() and .tolist() for NumPy types",
                "example": "result = {'mean': float(np.mean(data)), 'values': data.tolist()}",
            },
            "bounds_checking": {
                "title": "Add bounds checking for list access",
                "fix": "Check list length before accessing elements",
                "example": "first = items[0] if items else None",
            },
            "specific_exceptions": {
                "title": "Use specific exception handling",
                "fix": "Catch specific exceptions instead of bare except",
                "example": "except json.JSONDecodeError as e:",
            },
            "structured_logging": {
                "title": "Replace print with proper logging",
                "fix": "Use logger instead of proper logging",
                "example": 'logger.debug(f"Processing {filename}")',
            },
            "temp_file_handling": {
                "title": "Use secure temporary file handling",
                "fix": "Replace mktemp with NamedTemporaryFile",
                "example": "with tempfile.NamedTemporaryFile() as tmp:",
            },
        }

        for detection in pattern_connections.get("detected_patterns", []):
            pattern_name = detection["pattern"]

            if pattern_name in fix_templates:
                template = fix_templates[pattern_name]
                fixes.append(
                    {
                        "pattern": pattern_name,
                        "title": template["title"],
                        "line": detection["line"],
                        "severity": detection["severity"],
                        "fix_description": template["fix"],
                        "example": template["example"],
                        "confidence": detection["confidence"],
                        "impact": "Improves code reliability and prevents runtime errors",
                    }
                )

        return fixes

    def _generate_visual_diff(
        self, code: str, pattern_connections: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generate visual diff information for pattern applications.

        Args:
            code: Original code
            pattern_connections: Pattern connection analysis

        Returns:
            Visual diff information
        """
        lines = code.split("\n")
        diff_info: Dict[str, List[Dict[str, Any]]] = {
            "original_lines": [],
            "suggested_changes": [],
            "pattern_highlights": [],
        }

        for detection in pattern_connections.get("detected_patterns", []):
            line_num = detection["line"]
            if 1 <= line_num <= len(lines):
                original_line = lines[line_num - 1]

                diff_info["original_lines"].append(
                    {
                        "line": line_num,
                        "content": original_line,
                        "pattern": detection["pattern"],
                        "severity": detection["severity"],
                    }
                )

                # Generate suggested fix
                suggested_fix = self._generate_line_fix(original_line, detection["pattern"])
                if suggested_fix:
                    diff_info["suggested_changes"].append(
                        {
                            "line": line_num,
                            "original": original_line,
                            "suggested": suggested_fix,
                            "pattern": detection["pattern"],
                        }
                    )

        return diff_info

    def _generate_line_fix(self, line: str, pattern: str) -> Optional[str]:
        """Generate a suggested fix for a single line.

        Args:
            line: Original code line
            pattern: Pattern name

        Returns:
            Suggested fixed line or None
        """
        if pattern == "numpy_json_serialization":
            # Replace np.mean(data) with float(np.mean(data))
            line = re.sub(r"(\w+)\s*=\s*np\.(\w+)\(([^)]+)\)", r"\1 = float(np.\2(\3))", line)
            # Replace data with data.tolist() in JSON contexts
            line = re.sub(
                r"json\.dumps\([^)]*(\w+)[^)]*\)", r"json.dumps(..., \1.tolist(), ...)", line
            )

        elif pattern == "bounds_checking":
            # Add bounds check before [0] access
            if "[0]" in line and "if" not in line:
                # This is a simple heuristic - real implementation would be more sophisticated
                pass

        elif pattern == "specific_exceptions":
            if "except:" in line:
                line = line.replace("except:", "except Exception as e:")

        elif pattern == "structured_logging":
            if "print(" in line:
                line = re.sub(r"print\s*\(", "logger.info(", line)

        elif pattern == "temp_file_handling":
            if "tempfile.mktemp(" in line:
                line = line.replace(
                    "tempfile.mktemp(", "tempfile.NamedTemporaryFile(delete=False).name"
                )

        return line if line != line else None  # Return None if no change

    def _summarize_diff(self, pattern_connections: Dict[str, Any]) -> Dict[str, Any]:
        """Summarize the diff for display.

        Args:
            pattern_connections: Pattern connection analysis

        Returns:
            Summary information
        """
        detected = pattern_connections.get("detected_patterns", [])

        summary: Dict[str, Any] = {
            "total_issues": len(detected),
            "by_severity": {"high": 0, "medium": 0, "low": 0},
            "by_pattern": {},
            "confidence_range": {"min": 1.0, "max": 0.0, "avg": 0.0},
        }

        confidences = []

        for detection in detected:
            severity = detection["severity"]
            pattern = detection["pattern"]
            confidence = detection["confidence"]

            summary["by_severity"][severity] += 1
            summary["by_pattern"][pattern] = summary["by_pattern"].get(pattern, 0) + 1
            confidences.append(confidence)

        if confidences:
            summary["confidence_range"]["min"] = min(confidences)
            summary["confidence_range"]["max"] = max(confidences)
            summary["confidence_range"]["avg"] = sum(confidences) / len(confidences)

        return summary


def display_debrief(debrief: Dict[str, Any]) -> None:
    """Display the debrief section in a formatted way.

    Args:
        debrief: Debrief dictionary containing strategies, difficulty, and explanation
    """
    print("=" * 70)
    print("📋 REVIEW DEBRIEF")
    print("=" * 70)
    print()

    if "strategies" in debrief and debrief["strategies"]:
        print("💡 Improvement Strategies:")
        print()
        for i, strategy in enumerate(debrief["strategies"], 1):
            print(f"  {i}. {strategy}")
        print()

    if "difficulty" in debrief:
        difficulty = debrief["difficulty"]
        print(f"📊 Difficulty of Execution: {difficulty}/10")

        # Visual representation
        filled = "█" * difficulty
        empty = "░" * (10 - difficulty)
        print(f"   {filled}{empty}")

        # Difficulty level description
        if difficulty <= 3:
            level = "Easy"
            emoji = "🟢"
        elif difficulty <= 6:
            level = "Moderate"
            emoji = "🟡"
        elif difficulty <= 9:
            level = "Hard"
            emoji = "🔴"
        else:
            level = "Very Hard"
            emoji = "⚫"

        print(f"   {emoji} Level: {level}")
        print()

    if "explanation" in debrief and debrief["explanation"]:
        print("📝 Explanation:")
        explanation_lines = debrief["explanation"].split("\n")
        for line in explanation_lines:
            if line.strip():
                print(f"   {line}")
        print()

    print("=" * 70)


def interactive_review():
    """Run interactive code review session."""
    print("\n" + "=" * 70)
    print("🔍 Interactive Code Review")
    print("=" * 70)
    print()

    reviewer = CodeReviewer()

    if not reviewer.llm_manager.is_any_available():
        print("⚠️  No LLM providers available!")
        print()
        print("Set one of these API keys:")
        print("  • ANTHROPIC_API_KEY")
        print("  • OPENAI_API_KEY")
        print("  • GEMINI_API_KEY")
        print()
        return

    providers = reviewer.llm_manager.list_available_providers()
    print(f"✓ Using LLM: {', '.join(providers)}")
    print()
    print("Paste your code (end with a line containing only '---'):")
    print()

    # Collect code
    code_lines = []
    while True:
        try:
            line = input()
            if line.strip() == "---":
                break
            code_lines.append(line)
        except EOFError:
            break

    code = "\n".join(code_lines)

    if not code.strip():
        print("\nNo code provided.\n")
        return

    print("\n🔍 Reviewing code...\n")

    # Review code
    result = reviewer.review_code(code)

    if "error" in result:
        print(f"Error: {result['error']}\n")
    else:
        print(result["review"])
        print()

        # Display debrief if available
        if "debrief" in result:
            display_debrief(result["debrief"])

        print()
        print(f"Reviewed by: {result['provider']} ({result['model']})")
        print()


if __name__ == "__main__":
    interactive_review()
