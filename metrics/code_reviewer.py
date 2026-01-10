"""
Interactive Code Review Module

Provides LLM-powered code review with pattern suggestions and best practices.
"""

import logging
import re
from typing import Any, Dict, Optional

from metrics.config_manager import ConfigManager
from metrics.llm_providers import get_llm_manager
from metrics.pattern_manager import PatternManager

logger = logging.getLogger(__name__)


class CodeReviewer:
    """Interactive code reviewer with LLM assistance."""

    def __init__(self, llm_provider: Optional[str] = None):
        """Initialize code reviewer.

        Args:
            llm_provider: Preferred LLM provider
        """
        self.config = ConfigManager()
        self.llm_manager = get_llm_manager()
        if llm_provider:
            self.llm_manager.preferred_provider = llm_provider

        self.pattern_manager = PatternManager()
        self.patterns = self.pattern_manager.get_all_patterns()

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
                "error": f"Code too large for review (max {max_code_size} bytes). Please review in smaller chunks.",
                "suggestions": [],
                "debrief": {
                    "strategies": [
                        "Break the code into smaller, logical chunks for review."
                    ],
                    "difficulty": 2,
                    "explanation": "Code exceeded size limit for review.",
                },
            }

        if not self.llm_manager.is_any_available():
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
            response = self.llm_manager.generate(
                prompt, max_tokens=max_tokens, fallback=True
            )

            # Generate debrief
            debrief = self.generate_debrief(code, response.text, context)

            # Parse response
            return {
                "review": response.text,
                "provider": response.provider,
                "model": response.model,
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
        if not self.llm_manager.is_any_available():
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
            response = self.llm_manager.generate(
                prompt, max_tokens=max_tokens, fallback=True
            )
            return response.text
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
        if not self.llm_manager.is_any_available():
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
            response = self.llm_manager.generate(
                prompt, max_tokens=max_tokens, fallback=True
            )
            return response.text
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
        if not self.llm_manager.is_any_available():
            return {
                "strategies": [
                    "No LLM providers available. Set API keys to use this feature."
                ],
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
            response = self.llm_manager.generate(
                prompt, max_tokens=max_tokens, fallback=True
            )

            # Parse the response
            debrief_text = response.text
            strategies = []
            difficulty = 5
            explanation = ""

            # Extract strategies
            if "**Improvement Strategies:**" in debrief_text:
                strategies_section = debrief_text.split("**Improvement Strategies:**")[
                    1
                ]
                if "**Difficulty Rating:**" in strategies_section:
                    strategies_section = strategies_section.split(
                        "**Difficulty Rating:**"
                    )[0]

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
