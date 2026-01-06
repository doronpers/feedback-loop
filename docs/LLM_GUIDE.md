# LLM Integration Guide

## Overview

feedback-loop now supports multiple LLM providers for smarter, more engaging code generation and review. Choose from **Claude**, **GPT-4**, or **Gemini** - or use them all with automatic fallback!

## Quick Start

### 1. Set Up an LLM Provider

Choose one (or more) providers:

**Option A: Anthropic Claude (Recommended)**
```bash
export ANTHROPIC_API_KEY='your-key-here'
# Get your key at: https://console.anthropic.com/
```

**Option B: OpenAI GPT-4**
```bash
export OPENAI_API_KEY='your-key-here'
# Get your key at: https://platform.openai.com/api-keys
```

**Option C: Google Gemini**
```bash
export GOOGLE_API_KEY='your-key-here'
# Get your key at: https://makersuite.google.com/app/apikey
```

### 2. Try the Interactive Chat Assistant

The easiest way to learn patterns and get help:

```bash
./bin/fl-chat
```

Or:

```bash
python bin/fl-chat
```

**Features:**
- Ask questions about patterns in natural language
- Get pattern explanations with examples
- Generate code interactively
- Conversational, context-aware assistance

**Example conversation:**
```
You: How do I handle NumPy arrays in JSON?
Assistant: You should use the numpy_json_serialization pattern! Here's how...
```

## Benefits

### Simpler Onboarding

- **Interactive setup**: Wizard guides you through configuration
- **Chat assistant**: Ask questions instead of reading docs
- **Natural language**: No need to memorize commands

### More Engaging

- **Conversational**: Talk to your development tools
- **Real-time help**: Get instant answers
- **Context-aware**: Suggestions based on your code and patterns

### Better Code Quality

- **Pattern awareness**: LLM knows your project's patterns
- **Automatic review**: Get feedback instantly
- **Consistent style**: Generates code following your standards

### Flexible

- **Multiple providers**: Use Claude, GPT-4, or Gemini
- **Automatic fallback**: Works even if one provider is down
- **Template mode**: Degrades gracefully without API keys

## Configuration

### Environment Variables

```bash
# LLM Provider (required for AI features - choose at least one)
export ANTHROPIC_API_KEY='your-key'      # For Claude
export OPENAI_API_KEY='your-key'         # For GPT-4  
export GOOGLE_API_KEY='your-key'         # For Gemini

# Optional: Set preferred provider
export FL_LLM_PROVIDER='claude'          # claude|openai|gemini
```

### Check Configuration

```bash
# Using the dashboard
./bin/fl-dashboard

# Or check manually
python3 -c 'from metrics.llm_providers import get_llm_manager; m = get_llm_manager(); print(m.list_available_providers())'
```

## Advanced Usage

### Custom Code Generation

```python
from metrics.code_generator import PatternAwareGenerator
from metrics.pattern_manager import PatternManager

pm = PatternManager()
generator = PatternAwareGenerator(
    pm.get_all_patterns(),
    use_llm=True,
    llm_provider="claude"  # Specify provider
)

# Generate with metrics context
result = generator.generate(
    prompt="create async file processor",
    metrics_context={
        "high_frequency_patterns": ["large_file_processing"],
        "critical_patterns": ["specific_exceptions"]
    },
    min_confidence=0.85
)

print(f"Code:\n{result.code}")
print(f"\nReport:\n{result.report}")
```

### Pattern-Aware Review

```python
from metrics.code_reviewer import CodeReviewer

reviewer = CodeReviewer(llm_provider="openai")

code = 