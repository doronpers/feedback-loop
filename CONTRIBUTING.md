# Contributing to feedback-loop

Thank you for your interest in improving this project!

## How to Contribute

### Adding New Patterns

When you discover a useful pattern:

1. **Document it** in `documentation/AI_PATTERNS_GUIDE.md`
   - Add to the appropriate section
   - Include bad and good examples
   - Explain why the pattern matters

2. **Add code examples**
   - Bad example in `examples/bad_patterns.py`
   - Good example in `examples/good_patterns.py`
   - Clear comments explaining the difference

3. **Write tests** in `tests/test_good_patterns.py`
   - Test the good pattern works
   - Test the bad pattern fails as expected
   - Cover edge cases

4. **Update documentation**
   - Add to [QUICK_REFERENCE.md](documentation/QUICK_REFERENCE.md)
   - Update pattern count in README badges
   - Run `python -m metrics.integrate sync-to-markdown`

### Improving Documentation

We follow Dieter Rams' design principles:

- **Understandable**: Use clear, simple language
- **Minimal**: Remove redundancy, keep it focused
- **Honest**: Accurate code examples that work
- **Thorough**: Cover edge cases and gotchas

**Before submitting:**

- Verify all code examples run correctly
- Check for broken links
- Ensure consistent formatting

### Fixing Bugs

1. **Add a test** that demonstrates the bug
2. **Fix the code**
3. **Verify** all tests still pass
4. **Document** the fix in CHANGELOG.md

### Code Style

- Follow existing patterns in the codebase
- Use type hints for public APIs
- Add docstrings to public functions
- Use logger.debug() not print()
- Handle exceptions specifically

## Testing Your Changes

```bash
# Run all tests
pytest tests/ -v

# Run with coverage
pytest tests/ --cov=. --cov-report=html

# Run specific test file
pytest tests/test_good_patterns.py -v
```

Coverage should remain at 90%+ for core code.

## Pull Request Process

1. **Create a branch** with a descriptive name
2. **Make focused changes** - one feature/fix per PR
3. **Update documentation** - keep docs in sync with code
4. **Add tests** - maintain or improve coverage
5. **Update CHANGELOG.md** - document your changes
6. **Submit PR** with clear description

### PR Description Template

```markdown
## What Changed
Brief description of your changes

## Why
Explain the problem this solves or feature this adds

## Testing
- [ ] Added/updated tests
- [ ] All tests pass
- [ ] Documentation updated

## Checklist
- [ ] Code follows existing style
- [ ] Added to CHANGELOG.md
- [ ] Updated relevant documentation
- [ ] No broken links or references
```

## Project Structure

```
feedback-loop/
├── documentation/      # All documentation lives here
├── examples/           # Code examples (good & bad patterns)
├── metrics/            # Metrics collection system
├── tests/              # Test suite
├── demo*.py            # Interactive demonstrations
├── README.md           # Project overview and navigation
├── CHANGELOG.md        # Version history
└── RESULTS.md          # Test results and verification
```

## Questions?

- Open an issue for discussion
- Check existing issues first
- Be specific and provide examples

## License

By contributing, you agree that your contributions will be licensed under the MIT License.
