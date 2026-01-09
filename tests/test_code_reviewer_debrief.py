"""
Tests for the code reviewer debrief feature.
"""

import pytest
from unittest.mock import Mock, patch

from metrics.code_reviewer import CodeReviewer
from metrics.llm_providers import LLMResponse


class TestCodeReviewerDebrief:
    """Tests for the debrief functionality in CodeReviewer."""
    
    @patch('metrics.code_reviewer.get_llm_manager')
    def test_generate_debrief_basic(self, mock_get_llm):
        """Test basic debrief generation."""
        # Setup mock LLM
        mock_llm = Mock()
        mock_llm.is_any_available.return_value = True
        mock_llm.generate.return_value = LLMResponse(
            text="""**Improvement Strategies:**
1. Add input validation to check for None values
2. Use type hints for better code clarity
3. Add error handling for edge cases

**Difficulty Rating:** 4

**Explanation:**
These improvements are moderate in difficulty, requiring some refactoring but no major architectural changes.""",
            model="test-model",
            provider="test-provider"
        )
        mock_get_llm.return_value = mock_llm
        
        reviewer = CodeReviewer()
        
        code = "def foo(x): return x * 2"
        review = "Missing input validation"
        
        debrief = reviewer.generate_debrief(code, review)
        
        assert "strategies" in debrief
        assert len(debrief["strategies"]) >= 3
        assert "difficulty" in debrief
        assert debrief["difficulty"] == 4
        assert "explanation" in debrief
        assert "moderate" in debrief["explanation"].lower()
    
    @patch('metrics.code_reviewer.get_llm_manager')
    def test_generate_debrief_difficulty_range(self, mock_get_llm):
        """Test that difficulty rating is within valid range."""
        mock_llm = Mock()
        mock_llm.is_any_available.return_value = True
        mock_llm.generate.return_value = LLMResponse(
            text="""**Improvement Strategies:**
1. Simple fix

**Difficulty Rating:** 15

**Explanation:**
Test explanation""",
            model="test-model",
            provider="test-provider"
        )
        mock_get_llm.return_value = mock_llm
        
        reviewer = CodeReviewer()
        debrief = reviewer.generate_debrief("code", "review")
        
        # Should cap at 10
        assert 1 <= debrief["difficulty"] <= 10
    
    @patch('metrics.code_reviewer.get_llm_manager')
    def test_generate_debrief_no_llm(self, mock_get_llm):
        """Test debrief generation when no LLM is available."""
        mock_llm = Mock()
        mock_llm.is_any_available.return_value = False
        mock_get_llm.return_value = mock_llm
        
        reviewer = CodeReviewer()
        debrief = reviewer.generate_debrief("code", "review")
        
        assert "strategies" in debrief
        assert "difficulty" in debrief
        assert debrief["difficulty"] == 5  # Default value
    
    @patch('metrics.code_reviewer.get_llm_manager')
    def test_review_code_includes_debrief(self, mock_get_llm):
        """Test that review_code includes debrief in the response."""
        mock_llm = Mock()
        mock_llm.is_any_available.return_value = True
        
        # Mock two generate calls - one for review, one for debrief
        mock_llm.generate.side_effect = [
            LLMResponse(
                text="Code review feedback",
                model="test-model",
                provider="test-provider"
            ),
            LLMResponse(
                text="""**Improvement Strategies:**
1. Strategy one

**Difficulty Rating:** 3

**Explanation:**
Easy to implement""",
                model="test-model",
                provider="test-provider"
            )
        ]
        mock_get_llm.return_value = mock_llm
        
        reviewer = CodeReviewer()
        result = reviewer.review_code("def foo(): pass")
        
        assert "review" in result
        assert "debrief" in result
        assert "strategies" in result["debrief"]
        assert "difficulty" in result["debrief"]
    
    @patch('metrics.code_reviewer.get_llm_manager')
    def test_debrief_parsing_various_formats(self, mock_get_llm):
        """Test debrief parsing with different response formats."""
        mock_llm = Mock()
        mock_llm.is_any_available.return_value = True
        
        # Test with bullet points instead of numbers
        mock_llm.generate.return_value = LLMResponse(
            text="""**Improvement Strategies:**
- Use better variable names
- Add documentation
* Implement error handling

**Difficulty Rating:** 2

**Explanation:**
Simple improvements""",
            model="test-model",
            provider="test-provider"
        )
        mock_get_llm.return_value = mock_llm
        
        reviewer = CodeReviewer()
        debrief = reviewer.generate_debrief("code", "review")
        
        assert len(debrief["strategies"]) >= 3
        assert debrief["difficulty"] == 2
    
    @patch('metrics.code_reviewer.get_llm_manager')
    def test_debrief_error_handling(self, mock_get_llm):
        """Test debrief error handling when LLM fails."""
        mock_llm = Mock()
        mock_llm.is_any_available.return_value = True
        mock_llm.generate.side_effect = Exception("LLM error")
        mock_get_llm.return_value = mock_llm
        
        reviewer = CodeReviewer()
        debrief = reviewer.generate_debrief("code", "review")
        
        # Should return fallback response
        assert "strategies" in debrief
        assert "difficulty" in debrief
        assert "error" in debrief["strategies"][0].lower() or "could not" in debrief["strategies"][0].lower()
    
    @patch('metrics.code_reviewer.get_llm_manager')
    def test_debrief_with_context(self, mock_get_llm):
        """Test debrief generation with additional context."""
        mock_llm = Mock()
        mock_llm.is_any_available.return_value = True
        mock_llm.generate.return_value = LLMResponse(
            text="""**Improvement Strategies:**
1. Use context-specific patterns

**Difficulty Rating:** 5

**Explanation:**
Moderate difficulty with given context""",
            model="test-model",
            provider="test-provider"
        )
        mock_get_llm.return_value = mock_llm
        
        reviewer = CodeReviewer()
        context = "This is a web API endpoint"
        debrief = reviewer.generate_debrief("code", "review", context)
        
        # Verify that generate was called
        assert mock_llm.generate.called
        # Check that context is included in the prompt
        call_args = mock_llm.generate.call_args
        assert context in call_args[0][0]
