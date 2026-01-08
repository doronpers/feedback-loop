"""
Tests for Sync Client

Tests the abstraction layer for pattern and metrics synchronization.
"""

import json
import pytest
from pathlib import Path
from metrics.sync_client import (
    SyncClient,
    LocalSyncClient,
    CloudSyncClient,
    create_sync_client
)


class TestLocalSyncClient:
    """Tests for LocalSyncClient."""
    
    def test_initialization(self, tmp_path):
        """Test LocalSyncClient initialization."""
        patterns_file = tmp_path / "patterns.json"
        metrics_file = tmp_path / "metrics.json"
        
        client = LocalSyncClient(
            patterns_file=str(patterns_file),
            metrics_file=str(metrics_file)
        )
        
        assert client.patterns_file == patterns_file
        assert client.metrics_file == metrics_file
        assert not client.is_authenticated()
    
    def test_sync_patterns(self, tmp_path):
        """Test syncing patterns to local file system."""
        patterns_file = tmp_path / "patterns.json"
        client = LocalSyncClient(patterns_file=str(patterns_file))
        
        patterns = [
            {"name": "pattern1", "description": "Test pattern 1"},
            {"name": "pattern2", "description": "Test pattern 2"}
        ]
        
        result = client.sync_patterns(patterns)
        
        assert result["status"] == "success"
        assert result["synced_count"] == 2
        assert result["storage"] == "local"
        
        # Verify patterns were written to file
        assert patterns_file.exists()
        with open(patterns_file, 'r') as f:
            saved_patterns = json.load(f)
        assert len(saved_patterns) == 2
        assert saved_patterns[0]["name"] == "pattern1"
    
    def test_pull_patterns(self, tmp_path):
        """Test pulling patterns from local file system."""
        patterns_file = tmp_path / "patterns.json"
        
        # Create patterns file
        patterns = [
            {"name": "pattern1", "description": "Test pattern 1"},
            {"name": "pattern2", "description": "Test pattern 2"}
        ]
        with open(patterns_file, 'w') as f:
            json.dump(patterns, f)
        
        client = LocalSyncClient(patterns_file=str(patterns_file))
        pulled_patterns = client.pull_patterns()
        
        assert len(pulled_patterns) == 2
        assert pulled_patterns[0]["name"] == "pattern1"
    
    def test_pull_patterns_no_file(self, tmp_path):
        """Test pulling patterns when file doesn't exist."""
        patterns_file = tmp_path / "nonexistent.json"
        client = LocalSyncClient(patterns_file=str(patterns_file))
        
        pulled_patterns = client.pull_patterns()
        
        assert pulled_patterns == []
    
    def test_sync_metrics(self, tmp_path):
        """Test syncing metrics to local file system."""
        metrics_file = tmp_path / "metrics.json"
        client = LocalSyncClient(metrics_file=str(metrics_file))
        
        metrics = {
            "bugs": [{"id": 1, "type": "bug"}],
            "test_failures": []
        }
        
        result = client.sync_metrics(metrics)
        
        assert result["status"] == "success"
        assert result["storage"] == "local"
        
        # Verify metrics were written to file
        assert metrics_file.exists()
        with open(metrics_file, 'r') as f:
            saved_metrics = json.load(f)
        assert "bugs" in saved_metrics
        assert len(saved_metrics["bugs"]) == 1
    
    def test_pull_config(self, tmp_path):
        """Test pulling configuration from local file system."""
        config_file = tmp_path / ".feedback-loop" / "config.json"
        config_file.parent.mkdir(parents=True)
        
        config = {"min_confidence": 0.8, "auto_sync": True}
        with open(config_file, 'w') as f:
            json.dump(config, f)
        
        client = LocalSyncClient(config_file=str(config_file))
        pulled_config = client.pull_config()
        
        assert pulled_config["min_confidence"] == 0.8
        assert pulled_config["auto_sync"] is True


class TestCloudSyncClient:
    """Tests for CloudSyncClient."""
    
    def test_initialization(self):
        """Test CloudSyncClient initialization."""
        client = CloudSyncClient(
            api_url="http://localhost:8000",
            api_key="test_key_123",
            organization_id="org1",
            team_id="team1"
        )
        
        assert client.api_url == "http://localhost:8000"
        assert client.api_key == "test_key_123"
        assert client.organization_id == "org1"
        assert client.team_id == "team1"
        assert client.is_authenticated()
    
    def test_not_authenticated(self):
        """Test CloudSyncClient without API key."""
        client = CloudSyncClient(
            api_url="http://localhost:8000",
            api_key="",
            organization_id="org1"
        )
        
        assert not client.is_authenticated()
    
    def test_sync_patterns_not_authenticated(self):
        """Test syncing patterns without authentication."""
        client = CloudSyncClient(
            api_url="http://localhost:8000",
            api_key=""
        )
        
        patterns = [{"name": "test", "description": "Test"}]
        result = client.sync_patterns(patterns)
        
        assert result["status"] == "error"
        assert "Not authenticated" in result["error"]
    
    def test_sync_patterns_placeholder(self):
        """Test syncing patterns (placeholder implementation)."""
        client = CloudSyncClient(
            api_url="http://localhost:8000",
            api_key="test_key_123"
        )
        
        patterns = [
            {"name": "pattern1", "description": "Test pattern 1"},
            {"name": "pattern2", "description": "Test pattern 2"}
        ]
        
        result = client.sync_patterns(patterns)
        
        # Placeholder implementation should return success
        assert result["status"] == "success"
        assert result["synced_count"] == 2
        assert result["storage"] == "cloud"
    
    def test_pull_patterns_not_authenticated(self):
        """Test pulling patterns without authentication."""
        client = CloudSyncClient(
            api_url="http://localhost:8000",
            api_key=""
        )
        
        patterns = client.pull_patterns()
        
        assert patterns == []
    
    def test_sync_metrics_not_authenticated(self):
        """Test syncing metrics without authentication."""
        client = CloudSyncClient(
            api_url="http://localhost:8000",
            api_key=""
        )
        
        metrics = {"bugs": []}
        result = client.sync_metrics(metrics)
        
        assert result["status"] == "error"
        assert "Not authenticated" in result["error"]
    
    def test_pull_config_not_authenticated(self):
        """Test pulling config without authentication."""
        client = CloudSyncClient(
            api_url="http://localhost:8000",
            api_key=""
        )
        
        config = client.pull_config()
        
        assert config == {}


class TestSyncClientFactory:
    """Tests for create_sync_client factory function."""
    
    def test_create_local_client(self):
        """Test creating local sync client."""
        client = create_sync_client(use_cloud=False)
        
        assert isinstance(client, LocalSyncClient)
        assert not client.is_authenticated()
    
    def test_create_cloud_client(self):
        """Test creating cloud sync client."""
        client = create_sync_client(
            use_cloud=True,
            api_url="http://localhost:8000",
            api_key="test_key_123"
        )
        
        assert isinstance(client, CloudSyncClient)
        assert client.is_authenticated()
    
    def test_create_cloud_client_fallback(self):
        """Test creating cloud client falls back to local when credentials missing."""
        client = create_sync_client(use_cloud=True)
        
        # Should fall back to LocalSyncClient
        assert isinstance(client, LocalSyncClient)
    
    def test_create_client_with_kwargs(self, tmp_path):
        """Test creating client with additional kwargs."""
        patterns_file = tmp_path / "patterns.json"
        
        client = create_sync_client(
            use_cloud=False,
            patterns_file=str(patterns_file)
        )
        
        assert isinstance(client, LocalSyncClient)
        assert client.patterns_file == patterns_file
