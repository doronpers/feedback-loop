# Quick Start (5 minutes)

**Welcome to feedback-loop!** Transform your test failures into reusable patterns and write better code with AI assistance.

## Choose Your Path

Select your role to get personalized guidance:

- [ ] **👨‍💻 Developer** - Write code with pattern guidance
- [ ] **👥 Team Lead** - Manage team patterns and workflows
- [ ] **📊 Manager** - View analytics and team insights

## Step 1: Quick Start (30 seconds!)

**Simplest option:** Run this single command for everything!

```bash
# 🚀 One-click: setup + demo + dashboard + AI assistance
python3 bin/fl-start
```

**What happens:**

- 🔧 Auto-detects your environment and installs everything
- 🎭 Launches interactive demo showing real patterns in action
- 📊 Opens analytics dashboard in your browser
- 🚀 Gets you productive immediately with AI-assisted coding

**No choices needed** - just run and explore!

---

**Manual setup:** If you prefer step-by-step control:

```bash
# Auto-detects your OS, checks Python, installs dependencies
python3 bin/fl-bootstrap
```

**What it does:**

- ✅ Detects macOS/Windows/Linux automatically
- ✅ Validates Python compatibility
- ✅ Checks virtual environment status
- ✅ Installs all required dependencies
- ✅ Sets up project configuration

## Step 2: Try It (2 minutes)

Experience feedback-loop with the interactive demo:

```bash
python3 bin/fl-demo
```

**What you'll see:**

- 📊 Pattern before/after examples
- 🎯 Interactive pattern playground
- 📈 Sample metrics and analytics
- 🧪 Working code examples

## Step 3: Apply Patterns (2 minutes)

### For Developers 👨‍💻

Start exploring and applying patterns:

```bash
# Browse the pattern catalog
python3 bin/fl-explore

# Apply patterns to your code
python3 bin/fl-apply --scan .

# Review code with AI assistance
python3 bin/fl-review my_code.py

# Chat with the AI assistant
python3 bin/fl-chat
```

**Quick wins:**

- Run `pytest --enable-metrics` to collect test data
- Use `fl-apply` to automatically fix pattern violations
- Ask the AI assistant: "How do I handle NumPy serialization?"

### For Team Leads 👥

Set up team collaboration:

```bash
# Sync patterns with your team
feedback-loop login

# Analyze team-wide patterns
feedback-loop analyze

# Generate team reports
feedback-loop report --format markdown
```

**Team features:**

- Cloud sync for shared patterns
- Team analytics and insights
- Automated code reviews

### For Managers 📊

Monitor development effectiveness:

```bash
# Launch analytics dashboard
python3 bin/fl-dashboard

# View pattern adoption metrics
# Monitor bug reduction trends
# Export reports for stakeholders
```

**Key metrics:**

- Pattern adoption rates
- Bug reduction over time
- Code quality improvements
- Team productivity insights

## Next Steps

**Learn more:**

- [AI Patterns Guide](AI_PATTERNS_GUIDE.md) - Deep dive into pattern philosophy
- [Quick Reference](QUICK_REFERENCE.md) - Pattern cheat sheet
- [Cursor Integration](../CURSOR_INTEGRATION.md) - IDE integration

**Get help:**

- `python3 bin/fl-chat` - Interactive AI assistant
- [Documentation Index](INDEX.md) - Complete guides
- [GitHub Issues](https://github.com/doronpers/feedback-loop/issues) - Report problems

## Pro Tips

🚀 **Start small**: Begin with `fl-demo` to see patterns in action
🎯 **Set API keys**: Add `ANTHROPIC_API_KEY` for AI features
📊 **Enable metrics**: Use `--enable-metrics` with pytest for data collection
🔄 **Iterate**: Patterns improve as you use them more

---

**Questions?** The AI chat assistant (`fl-chat`) knows everything about feedback-loop!

*Time estimate: 5 minutes to first successful pattern application*
