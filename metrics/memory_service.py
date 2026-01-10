"""
Memory Service Module

Integrates MemU agentic memory framework to provide intelligent,
long-term memory for development patterns in feedback-loop.
"""

import logging
import os
from datetime import datetime
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


class FeedbackLoopMemory:
    """
    MemU integration for semantic pattern storage and retrieval.

    This class provides an intelligent memory layer that enables:
    - Semantic pattern retrieval (query by concept, not just name)
    - Self-evolving patterns (patterns improve based on usage)
    - Cross-project learning (share patterns across projects)
    - Multimodal memory (code, logs, tests, reviews)
    - Intelligent recommendations (context-aware suggestions)
    """

    def __init__(
        self,
        storage_type: str = "inmemory",
        openai_api_key: Optional[str] = None,
        db_url: Optional[str] = None,
    ):
        """Initialize MemU service.

        Args:
            storage_type: Storage backend ("inmemory" or "postgres")
            openai_api_key: OpenAI API key for embeddings (optional)
            db_url: PostgreSQL connection string (only for postgres storage)

        Raises:
            ImportError: If memu-py is not installed
        """
        self.storage_type = storage_type
        self.openai_api_key = openai_api_key or os.getenv("OPENAI_API_KEY")
        self.db_url = db_url
        self._memory = None
        self._initialized = False

        # Try to import MemU
        try:
            import memu

            self._memu_available = True
            logger.info("MemU library loaded successfully")
        except ImportError:
            self._memu_available = False
            logger.warning(
                "MemU library not available. Install with: pip install memu-py"
            )

    async def initialize(self) -> bool:
        """Initialize the MemU memory service.

        Returns:
            True if initialization successful, False otherwise
        """
        if self._initialized:
            return True

        if not self._memu_available:
            logger.warning("Cannot initialize: MemU not available")
            return False

        try:
            import memu

            # Configure storage based on type
            if self.storage_type == "inmemory":
                # Use in-memory storage (no DB required)
                self._memory = memu.Memory(
                    storage="inmemory", api_key=self.openai_api_key
                )
                logger.info("Initialized MemU with in-memory storage")
            elif self.storage_type == "postgres":
                if not self.db_url:
                    raise ValueError("db_url required for postgres storage")
                self._memory = memu.Memory(
                    storage="postgres",
                    connection_string=self.db_url,
                    api_key=self.openai_api_key,
                )
                logger.info("Initialized MemU with PostgreSQL storage")
            else:
                raise ValueError(f"Unsupported storage type: {self.storage_type}")

            self._initialized = True
            return True

        except Exception as e:
            logger.error(f"Failed to initialize MemU: {e}")
            return False

    def is_available(self) -> bool:
        """Check if MemU is available and initialized.

        Returns:
            True if MemU is available and ready to use
        """
        return self._memu_available and self._initialized

    async def memorize_pattern(
        self, pattern: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """Store a pattern in MemU memory.

        Args:
            pattern: Pattern dictionary with fields:
                - name: Pattern identifier
                - description: Pattern description
                - good_example: Good code example
                - bad_example: Bad code example (optional)
                - tags: Optional list of tags

        Returns:
            Response from MemU or None if failed
        """
        if not await self._ensure_initialized():
            return None

        try:
            # Prepare resource for MemU
            resource = {
                "type": "pattern",
                "content": self._format_pattern_content(pattern),
                "metadata": {
                    "pattern_name": pattern.get("name", "unknown"),
                    "pattern_id": pattern.get("pattern_id", ""),
                    "severity": pattern.get("severity", "medium"),
                    "occurrence_frequency": pattern.get("occurrence_frequency", 0),
                    "effectiveness_score": pattern.get("effectiveness_score", 0.5),
                    "timestamp": datetime.now().isoformat(),
                    "source": "feedback-loop",
                },
                "tags": self._extract_tags(pattern),
            }

            # Store in MemU
            response = await self._memory.memorize(resource)
            logger.debug(f"Stored pattern '{pattern.get('name')}' in MemU")
            return response

        except Exception as e:
            logger.error(f"Failed to memorize pattern: {e}")
            return None

    async def memorize_development_session(
        self, session_data: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """Store metrics from a development session.

        Args:
            session_data: Session data dictionary with:
                - session_id: Unique session identifier
                - timestamp: Session timestamp
                - patterns_applied: List of patterns used
                - bugs: List of bugs encountered
                - test_failures: List of test failures
                - metrics: Additional metrics

        Returns:
            Response from MemU or None if failed
        """
        if not await self._ensure_initialized():
            return None

        try:
            resource = {
                "type": "development_session",
                "content": self._format_session_content(session_data),
                "metadata": {
                    "session_id": session_data.get("session_id", ""),
                    "timestamp": session_data.get(
                        "timestamp", datetime.now().isoformat()
                    ),
                    "patterns_count": len(session_data.get("patterns_applied", [])),
                    "bugs_count": len(session_data.get("bugs", [])),
                    "test_failures_count": len(session_data.get("test_failures", [])),
                    "source": "feedback-loop",
                },
                "tags": ["session", "metrics"],
            }

            response = await self._memory.memorize(resource)
            logger.debug(f"Stored development session in MemU")
            return response

        except Exception as e:
            logger.error(f"Failed to memorize session: {e}")
            return None

    async def memorize_code_review(
        self, review_data: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """Store code review feedback.

        Args:
            review_data: Review data dictionary with:
                - issue_type: Type of issue
                - pattern: Related pattern
                - severity: Severity level
                - file_path: File location
                - suggestion: Fix suggestion

        Returns:
            Response from MemU or None if failed
        """
        if not await self._ensure_initialized():
            return None

        try:
            resource = {
                "type": "code_review",
                "content": self._format_review_content(review_data),
                "metadata": {
                    "issue_type": review_data.get("issue_type", ""),
                    "pattern": review_data.get("pattern", ""),
                    "severity": review_data.get("severity", "medium"),
                    "file_path": review_data.get("file_path", ""),
                    "timestamp": datetime.now().isoformat(),
                    "source": "feedback-loop",
                },
                "tags": ["code_review", review_data.get("pattern", "")],
            }

            response = await self._memory.memorize(resource)
            logger.debug(f"Stored code review in MemU")
            return response

        except Exception as e:
            logger.error(f"Failed to memorize code review: {e}")
            return None

    async def retrieve_patterns(
        self, query: str, method: str = "rag", limit: int = 5
    ) -> Optional[Dict[str, Any]]:
        """Retrieve patterns using semantic search.

        Args:
            query: Natural language query
            method: Retrieval method ("rag" for fast, "llm" for deep)
            limit: Maximum number of results

        Returns:
            Dictionary with retrieved patterns or None if failed
        """
        if not await self._ensure_initialized():
            return None

        try:
            # Query MemU with semantic search
            if method == "rag":
                response = await self._memory.retrieve_rag(
                    query=query, limit=limit, filters={"type": "pattern"}
                )
            elif method == "llm":
                response = await self._memory.retrieve_llm(
                    query=query, limit=limit, filters={"type": "pattern"}
                )
            else:
                raise ValueError(f"Unsupported retrieval method: {method}")

            logger.debug(
                f"Retrieved {len(response.get('results', []))} patterns for query: {query}"
            )
            return response

        except Exception as e:
            logger.error(f"Failed to retrieve patterns: {e}")
            return None

    async def get_pattern_recommendations(
        self, context: str, limit: int = 3
    ) -> List[Dict[str, Any]]:
        """Get pattern recommendations for current context.

        Args:
            context: Current development context (e.g., "Building FastAPI endpoint")
            limit: Maximum number of recommendations

        Returns:
            List of recommended patterns
        """
        if not await self._ensure_initialized():
            return []

        try:
            # Use RAG retrieval for recommendations
            response = await self.retrieve_patterns(
                query=f"What patterns should I use for: {context}",
                method="rag",
                limit=limit,
            )

            if not response or "results" not in response:
                return []

            # Extract and format recommendations
            recommendations = []
            for result in response["results"]:
                recommendations.append(
                    {
                        "pattern_name": result.get("metadata", {}).get(
                            "pattern_name", ""
                        ),
                        "content": result.get("content", ""),
                        "score": result.get("score", 0.0),
                        "metadata": result.get("metadata", {}),
                    }
                )

            logger.debug(f"Generated {len(recommendations)} recommendations")
            return recommendations

        except Exception as e:
            logger.error(f"Failed to get recommendations: {e}")
            return []

    async def get_memory_stats(self) -> Optional[Dict[str, Any]]:
        """Get statistics about stored memories.

        Returns:
            Dictionary with memory statistics or None if failed
        """
        if not await self._ensure_initialized():
            return None

        try:
            # Get stats from MemU
            stats = await self._memory.get_stats()

            return {
                "total_memories": stats.get("total_count", 0),
                "patterns_count": stats.get("type_counts", {}).get("pattern", 0),
                "sessions_count": stats.get("type_counts", {}).get(
                    "development_session", 0
                ),
                "reviews_count": stats.get("type_counts", {}).get("code_review", 0),
                "storage_type": self.storage_type,
                "initialized": self._initialized,
            }

        except Exception as e:
            logger.error(f"Failed to get memory stats: {e}")
            return None

    # Helper methods

    async def _ensure_initialized(self) -> bool:
        """Ensure MemU is initialized, initialize if not.

        Returns:
            True if initialized successfully
        """
        if not self._initialized:
            return await self.initialize()
        return True

    def _format_pattern_content(self, pattern: Dict[str, Any]) -> str:
        """Format pattern as text content for MemU.

        Args:
            pattern: Pattern dictionary

        Returns:
            Formatted content string
        """
        parts = [
            f"Pattern: {pattern.get('name', 'unknown')}",
            f"Description: {pattern.get('description', 'No description')}",
        ]

        if pattern.get("good_example"):
            parts.append(f"Good Example:\n{pattern['good_example']}")

        if pattern.get("bad_example"):
            parts.append(f"Bad Example:\n{pattern['bad_example']}")

        return "\n\n".join(parts)

    def _format_session_content(self, session_data: Dict[str, Any]) -> str:
        """Format session data as text content for MemU.

        Args:
            session_data: Session data dictionary

        Returns:
            Formatted content string
        """
        parts = [
            f"Development Session: {session_data.get('session_id', 'unknown')}",
            f"Timestamp: {session_data.get('timestamp', 'unknown')}",
            f"Patterns Applied: {', '.join(session_data.get('patterns_applied', []))}",
            f"Bugs: {len(session_data.get('bugs', []))}",
            f"Test Failures: {len(session_data.get('test_failures', []))}",
        ]

        return "\n".join(parts)

    def _format_review_content(self, review_data: Dict[str, Any]) -> str:
        """Format review data as text content for MemU.

        Args:
            review_data: Review data dictionary

        Returns:
            Formatted content string
        """
        parts = [
            f"Code Review Issue: {review_data.get('issue_type', 'unknown')}",
            f"Pattern: {review_data.get('pattern', 'unknown')}",
            f"Severity: {review_data.get('severity', 'unknown')}",
            f"File: {review_data.get('file_path', 'unknown')}",
        ]

        if review_data.get("suggestion"):
            parts.append(f"Suggestion: {review_data['suggestion']}")

        return "\n".join(parts)

    def _extract_tags(self, pattern: Dict[str, Any]) -> List[str]:
        """Extract tags from pattern.

        Args:
            pattern: Pattern dictionary

        Returns:
            List of tags
        """
        tags = ["pattern"]

        # Add pattern name as tag
        if pattern.get("name"):
            tags.append(pattern["name"])

        # Add severity as tag
        if pattern.get("severity"):
            tags.append(pattern["severity"])

        # Add any explicit tags
        if pattern.get("tags"):
            tags.extend(pattern["tags"])

        return list(set(tags))  # Remove duplicates
