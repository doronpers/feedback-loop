"""
Tests for MemU memory service integration.

These tests use mocking to avoid requiring the actual MemU library
during test execution, ensuring backward compatibility.
"""

from datetime import datetime
from unittest.mock import AsyncMock, Mock, patch

import pytest


class TestFeedbackLoopMemory:
    """Tests for FeedbackLoopMemory class."""

    @pytest.fixture
    def mock_memu(self):
        """Mock the memu module."""
        with patch.dict("sys.modules", {"memu": Mock()}):
            yield

    def test_init_without_memu(self):
        """Test initialization when MemU is not installed."""
        from metrics.memory_service import FeedbackLoopMemory

        with patch.dict("sys.modules", {"memu": None}):
            memory = FeedbackLoopMemory()
            assert not memory._memu_available
            assert not memory._initialized

    def test_init_with_memu(self, mock_memu):
        """Test initialization when MemU is available."""
        from metrics.memory_service import FeedbackLoopMemory

        memory = FeedbackLoopMemory(storage_type="inmemory")
        assert memory.storage_type == "inmemory"
        assert not memory._initialized

    @pytest.mark.asyncio
    async def test_initialize_success(self, mock_memu):
        """Test successful initialization."""
        from metrics.memory_service import FeedbackLoopMemory

        mock_memory_instance = Mock()

        with patch("memu.Memory", return_value=mock_memory_instance):
            memory = FeedbackLoopMemory(storage_type="inmemory")
            result = await memory.initialize()

            assert result is True
            assert memory._initialized is True
            assert memory._memory is mock_memory_instance

    @pytest.mark.asyncio
    async def test_initialize_without_memu(self):
        """Test initialization fails gracefully without MemU."""
        from metrics.memory_service import FeedbackLoopMemory

        with patch.dict("sys.modules", {"memu": None}):
            memory = FeedbackLoopMemory()
            result = await memory.initialize()

            assert result is False
            assert not memory._initialized

    @pytest.mark.asyncio
    async def test_memorize_pattern(self, mock_memu):
        """Test pattern memorization."""
        from metrics.memory_service import FeedbackLoopMemory

        mock_memory_instance = Mock()
        mock_memory_instance.memorize = AsyncMock(return_value={"success": True})

        with patch("memu.Memory", return_value=mock_memory_instance):
            memory = FeedbackLoopMemory()
            await memory.initialize()

            pattern = {
                "name": "test_pattern",
                "description": "Test description",
                "good_example": "# Good code",
                "bad_example": "# Bad code",
            }

            result = await memory.memorize_pattern(pattern)

            assert result is not None
            assert result["success"] is True
            mock_memory_instance.memorize.assert_called_once()

    @pytest.mark.asyncio
    async def test_memorize_pattern_not_initialized(self):
        """Test pattern memorization without initialization."""
        from metrics.memory_service import FeedbackLoopMemory

        with patch.dict("sys.modules", {"memu": None}):
            memory = FeedbackLoopMemory()

            pattern = {"name": "test"}
            result = await memory.memorize_pattern(pattern)

            assert result is None

    @pytest.mark.asyncio
    async def test_memorize_development_session(self, mock_memu):
        """Test development session memorization."""
        from metrics.memory_service import FeedbackLoopMemory

        mock_memory_instance = Mock()
        mock_memory_instance.memorize = AsyncMock(return_value={"success": True})

        with patch("memu.Memory", return_value=mock_memory_instance):
            memory = FeedbackLoopMemory()
            await memory.initialize()

            session_data = {
                "session_id": "test-session-001",
                "timestamp": datetime.now().isoformat(),
                "patterns_applied": ["pattern1", "pattern2"],
                "bugs": [],
                "test_failures": [],
            }

            result = await memory.memorize_development_session(session_data)

            assert result is not None
            assert result["success"] is True
            mock_memory_instance.memorize.assert_called_once()

    @pytest.mark.asyncio
    async def test_memorize_code_review(self, mock_memu):
        """Test code review memorization."""
        from metrics.memory_service import FeedbackLoopMemory

        mock_memory_instance = Mock()
        mock_memory_instance.memorize = AsyncMock(return_value={"success": True})

        with patch("memu.Memory", return_value=mock_memory_instance):
            memory = FeedbackLoopMemory()
            await memory.initialize()

            review_data = {
                "issue_type": "Missing validation",
                "pattern": "input_validation",
                "severity": "high",
                "file_path": "test.py",
                "suggestion": "Add validation",
            }

            result = await memory.memorize_code_review(review_data)

            assert result is not None
            assert result["success"] is True
            mock_memory_instance.memorize.assert_called_once()

    @pytest.mark.asyncio
    async def test_retrieve_patterns_rag(self, mock_memu):
        """Test pattern retrieval using RAG method."""
        from metrics.memory_service import FeedbackLoopMemory

        mock_memory_instance = Mock()
        mock_memory_instance.retrieve_rag = AsyncMock(
            return_value={
                "results": [
                    {
                        "content": "Pattern content",
                        "metadata": {"pattern_name": "test_pattern"},
                        "score": 0.95,
                    }
                ]
            }
        )

        with patch("memu.Memory", return_value=mock_memory_instance):
            memory = FeedbackLoopMemory()
            await memory.initialize()

            result = await memory.retrieve_patterns("test query", method="rag", limit=5)

            assert result is not None
            assert "results" in result
            assert len(result["results"]) == 1
            assert result["results"][0]["metadata"]["pattern_name"] == "test_pattern"
            mock_memory_instance.retrieve_rag.assert_called_once()

    @pytest.mark.asyncio
    async def test_retrieve_patterns_llm(self, mock_memu):
        """Test pattern retrieval using LLM method."""
        from metrics.memory_service import FeedbackLoopMemory

        mock_memory_instance = Mock()
        mock_memory_instance.retrieve_llm = AsyncMock(return_value={"results": []})

        with patch("memu.Memory", return_value=mock_memory_instance):
            memory = FeedbackLoopMemory()
            await memory.initialize()

            result = await memory.retrieve_patterns("test query", method="llm", limit=3)

            assert result is not None
            assert "results" in result
            mock_memory_instance.retrieve_llm.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_pattern_recommendations(self, mock_memu):
        """Test getting pattern recommendations."""
        from metrics.memory_service import FeedbackLoopMemory

        mock_memory_instance = Mock()
        mock_memory_instance.retrieve_rag = AsyncMock(
            return_value={
                "results": [
                    {
                        "content": "Pattern 1 content",
                        "metadata": {"pattern_name": "pattern1"},
                        "score": 0.9,
                    },
                    {
                        "content": "Pattern 2 content",
                        "metadata": {"pattern_name": "pattern2"},
                        "score": 0.8,
                    },
                ]
            }
        )

        with patch("memu.Memory", return_value=mock_memory_instance):
            memory = FeedbackLoopMemory()
            await memory.initialize()

            recommendations = await memory.get_pattern_recommendations(
                "Building FastAPI endpoint", limit=3
            )

            assert len(recommendations) == 2
            assert recommendations[0]["pattern_name"] == "pattern1"
            assert recommendations[0]["score"] == 0.9

    @pytest.mark.asyncio
    async def test_get_memory_stats(self, mock_memu):
        """Test getting memory statistics."""
        from metrics.memory_service import FeedbackLoopMemory

        mock_memory_instance = Mock()
        mock_memory_instance.get_stats = AsyncMock(
            return_value={
                "total_count": 10,
                "type_counts": {
                    "pattern": 5,
                    "development_session": 3,
                    "code_review": 2,
                },
            }
        )

        with patch("memu.Memory", return_value=mock_memory_instance):
            memory = FeedbackLoopMemory(storage_type="inmemory")
            await memory.initialize()

            stats = await memory.get_memory_stats()

            assert stats is not None
            assert stats["total_memories"] == 10
            assert stats["patterns_count"] == 5
            assert stats["sessions_count"] == 3
            assert stats["reviews_count"] == 2
            assert stats["storage_type"] == "inmemory"

    def test_is_available_false(self):
        """Test is_available returns False when not initialized."""
        from metrics.memory_service import FeedbackLoopMemory

        with patch.dict("sys.modules", {"memu": None}):
            memory = FeedbackLoopMemory()
            assert not memory.is_available()

    @pytest.mark.asyncio
    async def test_is_available_true(self, mock_memu):
        """Test is_available returns True when initialized."""
        from metrics.memory_service import FeedbackLoopMemory

        mock_memory_instance = Mock()

        with patch("memu.Memory", return_value=mock_memory_instance):
            memory = FeedbackLoopMemory()
            await memory.initialize()
            assert memory.is_available()


class TestPatternManagerMemoryIntegration:
    """Tests for PatternManager with memory integration."""

    def test_init_without_memory(self):
        """Test PatternManager initialization without memory."""
        import tempfile

        from metrics.pattern_manager import PatternManager

        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            patterns_file = f.name
            f.write('{"patterns": [], "changelog": []}')

        try:
            manager = PatternManager(pattern_library_path=patterns_file, use_memory=False)
            assert manager.memory is None
            assert not manager.use_memory
        finally:
            import os

            os.unlink(patterns_file)

    def test_init_with_memory(self):
        """Test PatternManager initialization with memory."""
        import tempfile

        from metrics.pattern_manager import PatternManager

        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            patterns_file = f.name
            f.write('{"patterns": [], "changelog": []}')

        try:
            manager = PatternManager(
                pattern_library_path=patterns_file,
                use_memory=True,
                memory_config={"storage_type": "inmemory"},
            )
            assert manager.memory is not None
            assert manager.use_memory
        finally:
            import os

            os.unlink(patterns_file)

    @pytest.mark.asyncio
    async def test_store_pattern_to_memory(self):
        """Test storing pattern to memory."""
        import tempfile

        from metrics.pattern_manager import PatternManager

        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            patterns_file = f.name
            f.write('{"patterns": [], "changelog": []}')

        try:
            manager = PatternManager(pattern_library_path=patterns_file, use_memory=True)

            # Mock the memory service
            manager.memory = Mock()
            manager.memory.memorize_pattern = AsyncMock(return_value={"success": True})

            pattern = {"name": "test_pattern", "description": "Test"}
            result = await manager.store_pattern_to_memory(pattern)

            assert result is True
            manager.memory.memorize_pattern.assert_called_once_with(pattern)
        finally:
            import os

            os.unlink(patterns_file)

    @pytest.mark.asyncio
    async def test_retrieve_similar_patterns_fallback(self):
        """Test fallback to keyword search when memory not available."""
        import json
        import tempfile

        from metrics.pattern_manager import PatternManager

        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            patterns_file = f.name
            json.dump(
                {
                    "patterns": [
                        {
                            "name": "test_pattern",
                            "description": "A test pattern for testing",
                        },
                        {"name": "other_pattern", "description": "Something else"},
                    ],
                    "changelog": [],
                },
                f,
            )

        try:
            manager = PatternManager(pattern_library_path=patterns_file, use_memory=False)

            # Should use keyword search fallback
            results = await manager.retrieve_similar_patterns("test", limit=5)

            assert len(results) >= 1
            assert any("test" in p.get("name", "").lower() for p in results)
        finally:
            import os

            os.unlink(patterns_file)


class TestMetricsCollectorMemoryIntegration:
    """Tests for MetricsCollector with memory integration."""

    def test_init_without_memory(self):
        """Test MetricsCollector initialization without memory."""
        from metrics.collector import MetricsCollector

        collector = MetricsCollector()
        assert collector.memory_service is None

    def test_init_with_memory(self):
        """Test MetricsCollector initialization with memory."""
        from metrics.collector import MetricsCollector

        mock_memory = Mock()
        collector = MetricsCollector(memory_service=mock_memory)
        assert collector.memory_service is mock_memory

    @pytest.mark.asyncio
    async def test_store_session_to_memory(self):
        """Test storing session to memory."""
        from metrics.collector import MetricsCollector

        mock_memory = Mock()
        mock_memory.memorize_development_session = AsyncMock(return_value={"success": True})

        collector = MetricsCollector(memory_service=mock_memory)
        collector.log_code_generation(
            prompt="test prompt",
            patterns_applied=["pattern1", "pattern2"],
            confidence=0.9,
            success=True,
        )

        result = await collector.store_session_to_memory(session_id="test-001")

        assert result is True
        mock_memory.memorize_development_session.assert_called_once()

        # Check the call arguments
        call_args = mock_memory.memorize_development_session.call_args[0][0]
        assert call_args["session_id"] == "test-001"
        assert "pattern1" in call_args["patterns_applied"]

    @pytest.mark.asyncio
    async def test_store_session_without_memory(self):
        """Test storing session without memory service."""
        from metrics.collector import MetricsCollector

        collector = MetricsCollector()
        result = await collector.store_session_to_memory()

        assert result is False

    def test_extract_patterns_from_generation(self):
        """Test extracting patterns from generation events."""
        from metrics.collector import MetricsCollector

        collector = MetricsCollector()
        collector.log_code_generation(
            prompt="test 1",
            patterns_applied=["pattern1", "pattern2"],
            confidence=0.9,
            success=True,
        )
        collector.log_code_generation(
            prompt="test 2",
            patterns_applied=["pattern2", "pattern3"],
            confidence=0.8,
            success=True,
        )

        patterns = collector._extract_patterns_from_generation()

        # Should have unique patterns
        assert len(patterns) == 3
        assert set(patterns) == {"pattern1", "pattern2", "pattern3"}
