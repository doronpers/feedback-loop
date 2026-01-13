"""
Sync Client Module

Provides abstraction for pattern and metrics synchronization.
Supports both local file system (default) and cloud sync (when authenticated).
"""

import json
import logging
from abc import ABC, abstractmethod
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

import httpx

logger = logging.getLogger(__name__)


class SyncClient(ABC):
    """Abstract base class for synchronization clients."""

    @abstractmethod
    def sync_patterns(self, patterns: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Sync patterns to storage.

        Args:
            patterns: List of pattern dictionaries to sync

        Returns:
            Sync result with status and metadata
        """
        pass

    @abstractmethod
    def pull_patterns(self) -> List[Dict[str, Any]]:
        """Pull patterns from storage.

        Returns:
            List of pattern dictionaries
        """
        pass

    @abstractmethod
    def sync_metrics(self, metrics: Dict[str, Any]) -> Dict[str, Any]:
        """Sync metrics to storage.

        Args:
            metrics: Metrics data to sync

        Returns:
            Sync result with status and metadata
        """
        pass

    @abstractmethod
    def pull_config(self) -> Dict[str, Any]:
        """Pull configuration from storage.

        Returns:
            Configuration dictionary
        """
        pass

    @abstractmethod
    def is_authenticated(self) -> bool:
        """Check if client is authenticated.

        Returns:
            True if authenticated, False otherwise
        """
        pass


class LocalSyncClient(SyncClient):
    """Local file system sync client (default implementation)."""

    def __init__(
        self,
        patterns_file: str = "patterns.json",
        metrics_file: str = "metrics_data.json",
        config_file: str = ".feedback-loop/config.json",
    ):
        """Initialize local sync client.

        Args:
            patterns_file: Path to local patterns file
            metrics_file: Path to local metrics file
            config_file: Path to local config file
        """
        self.patterns_file = Path(patterns_file)
        self.metrics_file = Path(metrics_file)
        self.config_file = Path(config_file)
        logger.debug("Initialized LocalSyncClient")

    def sync_patterns(self, patterns: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Sync patterns to local file system.

        Args:
            patterns: List of pattern dictionaries to sync

        Returns:
            Sync result with status and metadata
        """
        try:
            # Ensure parent directory exists
            self.patterns_file.parent.mkdir(parents=True, exist_ok=True)

            # Write patterns to file
            with open(self.patterns_file, "w") as f:
                json.dump(patterns, f, indent=2)

            logger.debug(f"Synced {len(patterns)} patterns to {self.patterns_file}")

            return {
                "status": "success",
                "synced_count": len(patterns),
                "timestamp": datetime.now().isoformat(),
                "storage": "local",
            }
        except Exception as e:
            logger.error(f"Failed to sync patterns: {e}")
            return {
                "status": "error",
                "error": str(e),
                "timestamp": datetime.now().isoformat(),
            }

    def pull_patterns(self) -> List[Dict[str, Any]]:
        """Pull patterns from local file system.

        Returns:
            List of pattern dictionaries
        """
        try:
            if not self.patterns_file.exists():
                logger.debug(f"Patterns file not found: {self.patterns_file}")
                return []

            with open(self.patterns_file, "r") as f:
                patterns = json.load(f)

            logger.debug(f"Pulled {len(patterns)} patterns from {self.patterns_file}")
            return patterns
        except Exception as e:
            logger.error(f"Failed to pull patterns: {e}")
            return []

    def sync_metrics(self, metrics: Dict[str, Any]) -> Dict[str, Any]:
        """Sync metrics to local file system.

        Args:
            metrics: Metrics data to sync

        Returns:
            Sync result with status and metadata
        """
        try:
            # Ensure parent directory exists
            self.metrics_file.parent.mkdir(parents=True, exist_ok=True)

            # Write metrics to file
            with open(self.metrics_file, "w") as f:
                json.dump(metrics, f, indent=2)

            logger.debug(f"Synced metrics to {self.metrics_file}")

            return {
                "status": "success",
                "timestamp": datetime.now().isoformat(),
                "storage": "local",
            }
        except Exception as e:
            logger.error(f"Failed to sync metrics: {e}")
            return {
                "status": "error",
                "error": str(e),
                "timestamp": datetime.now().isoformat(),
            }

    def pull_config(self) -> Dict[str, Any]:
        """Pull configuration from local file system.

        Returns:
            Configuration dictionary
        """
        try:
            if not self.config_file.exists():
                logger.debug(f"Config file not found: {self.config_file}")
                return {}

            with open(self.config_file, "r") as f:
                config = json.load(f)

            logger.debug(f"Pulled config from {self.config_file}")
            return config
        except Exception as e:
            logger.error(f"Failed to pull config: {e}")
            return {}

    def is_authenticated(self) -> bool:
        """Check if client is authenticated.

        Returns:
            Always False for local client (no authentication needed)
        """
        return False


class CloudSyncClient(SyncClient):
    """Cloud sync client for team collaboration (requires authentication).

    This client is activated when a user logs in via the private repo API.
    It provides bi-directional sync with the cloud backend.
    """

    def __init__(
        self,
        api_url: str,
        api_key: str,
        organization_id: Optional[str] = None,
        team_id: Optional[str] = None,
        timeout: float = 30.0,
    ):
        """Initialize cloud sync client.

        Args:
            api_url: Base URL of the cloud API
            api_key: API key for authentication
            organization_id: Optional organization ID
            team_id: Optional team ID
            timeout: Request timeout in seconds (default: 30.0)
        """
        self.api_url = api_url.rstrip("/")
        self.api_key = api_key
        self.organization_id = organization_id
        self.team_id = team_id
        self.timeout = timeout
        self._authenticated = bool(api_key)
        
        # Initialize httpx client with proper error handling
        self._client = httpx.AsyncClient(
            base_url=self.api_url,
            headers={"Authorization": f"Bearer {self.api_key}"},
            timeout=timeout,
        )
        logger.debug("Initialized CloudSyncClient")

    def sync_patterns(self, patterns: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Sync patterns to cloud storage.

        Args:
            patterns: List of pattern dictionaries to sync

        Returns:
            Sync result with status and metadata
        """
        if not self.is_authenticated():
            return {
                "status": "error",
                "error": "Not authenticated",
                "timestamp": datetime.now().isoformat(),
            }

        try:
            import asyncio
            
            # Use async httpx client for actual HTTP call
            async def _sync():
                response = await self._client.post(
                    "/api/v1/patterns/sync",
                    json={"patterns": patterns},
                )
                response.raise_for_status()
                return response.json()
            
            result = asyncio.run(_sync())
            
            logger.info(f"Synced {len(patterns)} patterns to cloud")
            return {
                "status": "success",
                "synced_count": result.get("synced_count", len(patterns)),
                "conflicts": result.get("conflicts", []),
                "timestamp": datetime.now().isoformat(),
                "storage": "cloud",
                "organization_id": self.organization_id,
                "team_id": self.team_id,
            }
        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error syncing patterns: {e.response.status_code} - {e.response.text}")
            return {
                "status": "error",
                "error": f"HTTP {e.response.status_code}: {e.response.text[:200]}",
                "timestamp": datetime.now().isoformat(),
            }
        except httpx.RequestError as e:
            logger.error(f"Network error syncing patterns to cloud: {e}")
            return {
                "status": "error",
                "error": f"Network error: {str(e)}",
                "timestamp": datetime.now().isoformat(),
            }
        except Exception as e:
            logger.error(f"Failed to sync patterns to cloud: {e}", exc_info=True)
            return {
                "status": "error",
                "error": str(e),
                "timestamp": datetime.now().isoformat(),
            }

    def pull_patterns(self) -> List[Dict[str, Any]]:
        """Pull patterns from cloud storage.

        Returns:
            List of pattern dictionaries
        """
        if not self.is_authenticated():
            logger.warning("Cannot pull patterns: not authenticated")
            return []

        try:
            import asyncio
            
            # Use async httpx client for actual HTTP call
            async def _pull():
                response = await self._client.get("/api/v1/patterns/pull")
                response.raise_for_status()
                data = response.json()
                return data.get("patterns", [])
            
            patterns = asyncio.run(_pull())
            logger.info(f"Pulled {len(patterns)} patterns from cloud")
            return patterns
        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error pulling patterns: {e.response.status_code} - {e.response.text}")
            return []
        except httpx.RequestError as e:
            logger.error(f"Network error pulling patterns from cloud: {e}")
            return []
        except Exception as e:
            logger.error(f"Failed to pull patterns from cloud: {e}", exc_info=True)
            return []

    def sync_metrics(self, metrics: Dict[str, Any]) -> Dict[str, Any]:
        """Sync metrics to cloud storage.

        Args:
            metrics: Metrics data to sync

        Returns:
            Sync result with status and metadata
        """
        if not self.is_authenticated():
            return {
                "status": "error",
                "error": "Not authenticated",
                "timestamp": datetime.now().isoformat(),
            }

        try:
            import asyncio
            
            # Use async httpx client for actual HTTP call
            async def _sync():
                response = await self._client.post(
                    "/api/v1/metrics",
                    json=metrics,
                )
                response.raise_for_status()
                return response.json()
            
            result = asyncio.run(_sync())
            logger.info("Synced metrics to cloud")
            
            return {
                "status": "success",
                "timestamp": datetime.now().isoformat(),
                "storage": "cloud",
                "organization_id": self.organization_id,
                "team_id": self.team_id,
            }
        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error syncing metrics: {e.response.status_code} - {e.response.text}")
            return {
                "status": "error",
                "error": f"HTTP {e.response.status_code}: {e.response.text[:200]}",
                "timestamp": datetime.now().isoformat(),
            }
        except httpx.RequestError as e:
            logger.error(f"Network error syncing metrics to cloud: {e}")
            return {
                "status": "error",
                "error": f"Network error: {str(e)}",
                "timestamp": datetime.now().isoformat(),
            }
        except Exception as e:
            logger.error(f"Failed to sync metrics to cloud: {e}", exc_info=True)
            return {
                "status": "error",
                "error": str(e),
                "timestamp": datetime.now().isoformat(),
            }

    def pull_config(self) -> Dict[str, Any]:
        """Pull configuration from cloud storage.

        Returns:
            Configuration dictionary (team-enforced settings)
        """
        if not self.is_authenticated():
            logger.warning("Cannot pull config: not authenticated")
            return {}

        try:
            import asyncio
            
            # Use async httpx client for actual HTTP call
            async def _pull():
                response = await self._client.get("/api/v1/config")
                response.raise_for_status()
                data = response.json()
                return data.get("config", {})
            
            config = asyncio.run(_pull())
            logger.info("Pulled config from cloud")
            return config
        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error pulling config: {e.response.status_code} - {e.response.text}")
            return {}
        except httpx.RequestError as e:
            logger.error(f"Network error pulling config from cloud: {e}")
            return {}
        except Exception as e:
            logger.error(f"Failed to pull config from cloud: {e}", exc_info=True)
            return {}

    def is_authenticated(self) -> bool:
        """Check if client is authenticated.

        Returns:
            True if authenticated, False otherwise
        """
        return self._authenticated
    
    async def close(self) -> None:
        """Close the httpx client and clean up resources."""
        await self._client.aclose()
    
    def __enter__(self):
        """Context manager entry."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit - closes httpx client."""
        import asyncio
        try:
            asyncio.run(self.close())
        except Exception:
            pass  # Ignore errors during cleanup


def create_sync_client(
    use_cloud: bool = False,
    api_url: Optional[str] = None,
    api_key: Optional[str] = None,
    **kwargs,
) -> SyncClient:
    """Factory function to create appropriate sync client.

    Args:
        use_cloud: Whether to use cloud sync (requires authentication)
        api_url: Cloud API URL (required if use_cloud=True)
        api_key: API key for authentication (required if use_cloud=True)
        **kwargs: Additional arguments for the sync client

    Returns:
        SyncClient instance (LocalSyncClient or CloudSyncClient)
    """
    if use_cloud:
        if not api_url or not api_key:
            logger.warning(
                "Cloud sync requested but credentials missing, falling back to local"
            )
            return LocalSyncClient(**kwargs)
        return CloudSyncClient(api_url=api_url, api_key=api_key, **kwargs)

    return LocalSyncClient(**kwargs)
