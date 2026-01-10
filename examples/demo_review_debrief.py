#!/usr/bin/env python3
"""
Demo script for the review debrief feature.

This demonstrates the new debrief functionality that provides:
1. Improvement strategies for the reviewed code
2. Difficulty rating (1-10 scale) for implementing the improvements

Run with: python demo_review_debrief.py
Requires: ANTHROPIC_API_KEY, OPENAI_API_KEY, or GOOGLE_API_KEY environment variable
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from metrics.code_reviewer import CodeReviewer, display_debrief


def demo_simple_code():
    """Demo with simple problematic code."""
    print("\n" + "=" * 70)
    print("🔍 Demo 1: Simple Function Review")
    print("=" * 70)

    code = """def calculate(a, b):
    result = a / b
    return result"""

    print("\n📝 Code to Review:\n")
    print(code)
    print()

    reviewer = CodeReviewer()

    if not reviewer.llm_manager.is_any_available():
        print("⚠️  No LLM providers available!")
        print(
            "Set one of these API keys: ANTHROPIC_API_KEY, OPENAI_API_KEY, or GOOGLE_API_KEY"
        )
        return False

    print("🔍 Reviewing code...\n")
    result = reviewer.review_code(code, context="Mathematical calculation function")

    if "error" in result:
        print(f"❌ Error: {result['error']}")
        return False

    print("=" * 70)
    print("📋 REVIEW RESULTS")
    print("=" * 70)
    print()
    print(result["review"])
    print()

    if "debrief" in result:
        display_debrief(result["debrief"])

    print(f"\n✅ Reviewed by: {result['provider']} ({result['model']})\n")
    return True


def demo_complex_code():
    """Demo with more complex problematic code."""
    print("\n" + "=" * 70)
    print("🔍 Demo 2: Complex Function Review")
    print("=" * 70)

    code = """import json

def process_data(data):
    parsed = json.loads(data)
    results = []
    for item in parsed:
        results.append(item['value'] * 2)
    return results"""

    print("\n📝 Code to Review:\n")
    print(code)
    print()

    reviewer = CodeReviewer()

    print("🔍 Reviewing code...\n")
    result = reviewer.review_code(
        code, context="Data processing function that handles JSON input"
    )

    if "error" in result:
        print(f"❌ Error: {result['error']}")
        return False

    print("=" * 70)
    print("📋 REVIEW RESULTS")
    print("=" * 70)
    print()
    print(result["review"])
    print()

    if "debrief" in result:
        display_debrief(result["debrief"])

    print(f"\n✅ Reviewed by: {result['provider']} ({result['model']})\n")
    return True


def main():
    """Run the demo."""
    print("\n" + "=" * 70)
    print("🎯 FEEDBACK-LOOP REVIEW DEBRIEF DEMO")
    print("=" * 70)
    print()
    print("This demo showcases the new debrief feature that provides:")
    print("  • Actionable improvement strategies")
    print("  • Difficulty rating (1-10 scale)")
    print("  • Explanation of the difficulty assessment")
    print()

    # Check for API key
    from metrics.llm_providers import get_llm_manager

    llm_manager = get_llm_manager()

    if not llm_manager.is_any_available():
        print("⚠️  No LLM providers available!")
        print()
        print("Please set one of these environment variables:")
        print("  • ANTHROPIC_API_KEY")
        print("  • OPENAI_API_KEY")
        print("  • GOOGLE_API_KEY")
        print()
        return 1

    providers = llm_manager.list_available_providers()
    print(f"✅ Using LLM: {', '.join(providers)}")
    print()

    # Run demos
    success = True

    if not demo_simple_code():
        success = False

    if not demo_complex_code():
        success = False

    if success:
        print("\n" + "=" * 70)
        print("✅ All demos completed successfully!")
        print("=" * 70)
        print()
        return 0
    else:
        print("\n" + "=" * 70)
        print("❌ Some demos failed")
        print("=" * 70)
        print()
        return 1


if __name__ == "__main__":
    try:
        exit_code = main()
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\n\n👋 Demo interrupted by user")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback

        traceback.print_exc()
        sys.exit(1)
