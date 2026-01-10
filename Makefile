# Feedback Loop - Makefile for common operations

.PHONY: help install test analyze dashboard doctor clean

help:  ## Show this help message
	@echo "Feedback Loop - Available commands:"
	@echo ""
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-20s\033[0m %s\n", $$1, $$2}'
	@echo ""

install:  ## Install feedback-loop package
	pip install -e .
	@echo ""
	@echo "✓ Installed! Try: make dashboard"

install-dev:  ## Install with development dependencies
	pip install -e ".[dev,full]"

setup-repo:  ## Setup feedback-loop for current repository
	@./quickstart.sh

test:  ## Run tests with metrics collection
	pytest --enable-metrics -v

test-fast:  ## Run tests without metrics
	pytest -v

analyze:  ## Analyze metrics and update patterns
	feedback-loop analyze

generate:  ## Generate code (usage: make generate PROMPT="your prompt")
	@if [ -z "$(PROMPT)" ]; then \
		echo "Usage: make generate PROMPT=\"Create a function...\""; \
	else \
		feedback-loop generate "$(PROMPT)"; \
	fi

sync:  ## Sync patterns to AI_PATTERNS.md
	feedback-loop sync-to-markdown

dashboard:  ## Show interactive dashboard
	@./bin/fl-dashboard

doctor:  ## Run system health check
	@./bin/fl-doctor

report:  ## Generate detailed report
	feedback-loop report --format text

report-md:  ## Generate markdown report
	feedback-loop report --format markdown --output report.md

clean:  ## Clean generated files
	rm -f data/metrics_data.json
	rm -f data/patterns.json
	rm -f generated*.py
	rm -f *.meta.json
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	@echo "✓ Cleaned"

clean-all: clean  ## Clean everything including test cache
	rm -rf .pytest_cache
	rm -rf htmlcov
	rm -f .coverage
	@echo "✓ Deep cleaned"

demo:  ## Run all demos
	@echo "=== Core Patterns Demo ==="
	python demo.py
	@echo ""
	@echo "=== FastAPI Patterns Demo ==="
	python demo_fastapi.py
	@echo ""
	@echo "=== Metrics Demo ==="
	python demo_metrics.py

ci:  ## Run CI checks (test + analyze + report)
	@echo "Running CI checks..."
	@pytest --enable-metrics -v --cov=.
	@feedback-loop analyze
	@feedback-loop report
	@echo "✓ CI checks complete"

quick-check:  ## Quick health check
	@echo "Quick system check:"
	@python -c "import metrics; print('✓ Package installed')"
	@test -f conftest.py && echo "✓ Pytest plugin present" || echo "✗ Missing conftest.py"
	@test -f .git/hooks/pre-commit && echo "✓ Git hook installed" || echo "✗ Missing git hook"
	@test -n "$$ANTHROPIC_API_KEY" && echo "✓ API key set" || echo "⚠  API key not set"
