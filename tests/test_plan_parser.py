"""
Tests for Plan Parser Module
"""

import pytest
from pathlib import Path
from metrics.plan_parser import PlanParser


class TestPlanParser:
    """Tests for PlanParser class."""
    
    def test_parse_task_plan_extracts_goal(self, tmp_path):
        """Test that parse_task_plan extracts goal correctly."""
        plan_file = tmp_path / "task_plan.md"
        plan_file.write_text(
            """# Task Plan

## Goal
Fix JSON serialization bug in API endpoint

## Phases
- [ ] Phase 1: Research
- [x] Phase 2: Implementation (CURRENT)
"""
        )
        
        parser = PlanParser()
        result = parser.parse_task_plan(str(plan_file))
        
        assert result["goal"] == "Fix JSON serialization bug in API endpoint"
        assert len(result["phases"]) == 2
    
    def test_parse_task_plan_extracts_phases(self, tmp_path):
        """Test that parse_task_plan extracts phases with status."""
        plan_file = tmp_path / "task_plan.md"
        plan_file.write_text(
            """# Task Plan

## Phases
- [x] Phase 1: Research
- [ ] Phase 2: Implementation (CURRENT)
- [ ] Phase 3: Testing
"""
        )
        
        parser = PlanParser()
        result = parser.parse_task_plan(str(plan_file))
        
        phases = result["phases"]
        assert len(phases) == 3
        assert phases[0]["status"] == "completed"
        assert phases[1]["status"] == "pending"
        assert phases[1]["is_current"] is True
        assert phases[2]["status"] == "pending"
    
    def test_parse_task_plan_extracts_patterns(self, tmp_path):
        """Test that parse_task_plan extracts pattern references."""
        plan_file = tmp_path / "task_plan.md"
        plan_file.write_text(
            """# Task Plan

## Patterns to Apply
- [ ] numpy_json_serialization (from feedback-loop)
- [x] bounds_checking (from feedback-loop)
- [ ] specific_exceptions
"""
        )
        
        parser = PlanParser()
        result = parser.parse_task_plan(str(plan_file))
        
        patterns = result["patterns"]
        assert "numpy_json_serialization" in patterns
        assert "bounds_checking" in patterns
        assert "specific_exceptions" in patterns
        assert len(patterns) == 3
    
    def test_extract_task_context(self, tmp_path):
        """Test that extract_task_context returns correct context."""
        plan_file = tmp_path / "task_plan.md"
        plan_file.write_text(
            """# Task Plan

## Goal
Process NumPy arrays safely

## Phases
- [x] Phase 1: Research
- [ ] Phase 2: Implementation (CURRENT)
"""
        )
        
        parser = PlanParser()
        context = parser.extract_task_context(str(plan_file))
        
        assert context["goal"] == "Process NumPy arrays safely"
        assert context["current_phase"] == "Phase 2: Implementation (CURRENT)"
        assert context["phase_status"] == "pending"
    
    def test_extract_pattern_references(self):
        """Test that extract_pattern_references finds patterns in content."""
        content = """
## Patterns to Apply
- [ ] numpy_json_serialization (from feedback-loop)
- [x] bounds_checking
- [ ] specific_exceptions (confidence: 0.65)
"""
        
        parser = PlanParser()
        patterns = parser.extract_pattern_references(content)
        
        assert "numpy_json_serialization" in patterns
        assert "bounds_checking" in patterns
        assert "specific_exceptions" in patterns
    
    def test_parse_task_plan_file_not_found(self):
        """Test that parse_task_plan raises FileNotFoundError for missing file."""
        parser = PlanParser()
        
        with pytest.raises(FileNotFoundError):
            parser.parse_task_plan("nonexistent_plan.md")
    
    def test_extract_pattern_references_handles_no_section(self):
        """Test that extract_pattern_references returns empty list if no section."""
        content = """
# Task Plan

## Goal
Some goal

## Notes
Some notes
"""
        
        parser = PlanParser()
        patterns = parser.extract_pattern_references(content)
        
        assert patterns == []
