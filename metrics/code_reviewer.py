"""
Interactive Code Review Module

Provides LLM-powered code review with pattern suggestions and best practices.
"""

import logging
from typing import Dict, List, Optional

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
        self.llm_manager = get_llm_manager()
        if llm_provider:
            self.llm_manager.preferred_provider = llm_provider
        
        self.pattern_manager = PatternManager()
        self.patterns = self.pattern_manager.get_all_patterns()

    def review_code(self, code: str, context: Optional[str] = None) -> Dict[str, any]:
        """Review code with pattern awareness.
        
        Args:
            code: Code to review
            context: Optional context about the code
            
        Returns:
            Dictionary with review results
        """
        if not self.llm_manager.is_any_available():
            return {
                "error": "No LLM providers available. Set API keys to use code review.",
                "suggestions": []
            }

        # Build review prompt
        prompt = self._build_review_prompt(code, context)
        
        try:
            # Get LLM review
            response = self.llm_manager.generate(
                prompt,
                max_tokens=2048,
                fallback=True
            )
            
            # Parse response
            return {
                "review": response.text,
                "provider": response.provider,
                "model": response.model
            }
            
        except Exception as e:
            logger.error(f"Code review failed: {e}")
            return {
                "error": f"Code review failed: {e}",
                "suggestions": []
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
            response = self.llm_manager.generate(
                prompt,
                max_tokens=1500,
                fallback=True
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
            response = self.llm_manager.generate(
                prompt,
                max_tokens=2048,
                fallback=True
            )
            return response.text
        except Exception as e:
            logger.error(f"Suggestions failed: {e}")
            return f"Could not generate suggestions: {e}"


def interactive_review():
    """Run interactive code review session."""
    print("\n" + "="*70)
    print("🔍 Interactive Code Review")
    print("="*70)
    print()
    
    reviewer = CodeReviewer()
    
    if not reviewer.llm_manager.is_any_available():
        print("⚠️  No LLM providers available!")
        print()
        print("Set one of these API keys:")
        print("  • ANTHROPIC_API_KEY")
        print("  • OPENAI_API_KEY")
        print("  • GOOGLE_API_KEY")
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
        print(f"Reviewed by: {result['provider']} ({result['model']})")
        print()


if __name__ == "__main__":
    interactive_review()
