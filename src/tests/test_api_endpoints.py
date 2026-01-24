"""
Comprehensive tests for feedback-loop API endpoints.

Tests all API endpoints including authentication, patterns, config, dashboard, and insights.
"""

import json
import tempfile
from pathlib import Path
from unittest.mock import Mock, patch

import pytest
from fastapi.testclient import TestClient

pytest.importorskip("fastapi")

from feedback_loop.api.main import app, USERS_DB, SESSIONS_DB, PATTERNS_DB, CONFIG_DB


@pytest.fixture
def temp_db_path(tmp_path):
    """Create a temporary database for testing."""
    return str(tmp_path / "test_api.db")


@pytest.fixture
def client(temp_db_path, monkeypatch):
    """Create a test client with a temporary database."""
    # Clear in-memory databases
    USERS_DB.clear()
    SESSIONS_DB.clear()
    PATTERNS_DB.clear()
    CONFIG_DB.clear()

    # Set environment to use temporary database
    monkeypatch.setenv("FL_DB_TYPE", "sqlite")
    monkeypatch.setenv("FL_DB_PATH", temp_db_path)

    # Mock persistence backend to avoid startup issues
    with patch("feedback_loop.api.main.get_backend") as mock_backend:
        mock_persistence = Mock()
        mock_persistence.health_check.return_value = {
            "status": "healthy",
            "backend": "sqlite",
            "total_metrics": 0,
        }
        mock_persistence.connect.return_value = None
        mock_persistence.disconnect.return_value = None
        mock_persistence.migrate.return_value = None
        mock_backend.return_value = mock_persistence

        # Create test client
        test_client = TestClient(app)
        yield test_client


@pytest.fixture
def auth_token(client):
    """Create a test user and return auth token."""
    # Register user
    register_response = client.post(
        "/api/v1/auth/register",
        json={
            "email": "test@example.com",
            "username": "testuser",
            "password": "testpass123",
            "full_name": "Test User",
        },
    )
    assert register_response.status_code == 200

    # Login to get token
    login_response = client.post(
        "/api/v1/auth/login",
        json={
            "email": "test@example.com",
            "password": "testpass123",
        },
    )
    assert login_response.status_code == 200
    return login_response.json()["access_token"]


@pytest.fixture
def admin_token(client):
    """Create an admin user and return auth token."""
    # First user is admin
    register_response = client.post(
        "/api/v1/auth/register",
        json={
            "email": "admin@example.com",
            "username": "admin",
            "password": "adminpass123",
            "full_name": "Admin User",
        },
    )
    assert register_response.status_code == 200

    login_response = client.post(
        "/api/v1/auth/login",
        json={
            "email": "admin@example.com",
            "password": "adminpass123",
        },
    )
    assert login_response.status_code == 200
    return login_response.json()["access_token"]


# ============================================================================
# Health Endpoint Tests
# ============================================================================


class TestHealthEndpoint:
    """Test health check endpoint."""

    def test_health_endpoint_returns_ok(self, client):
        """Test that health endpoint returns OK status."""
        response = client.get("/api/v1/health")
        assert response.status_code == 200

        data = response.json()
        assert data["status"] in ["healthy", "warning", "unhealthy"]
        assert "version" in data
        assert "timestamp" in data

    def test_health_includes_database_info(self, client):
        """Test that health endpoint includes database diagnostics."""
        response = client.get("/api/v1/health")
        assert response.status_code == 200

        data = response.json()
        if "database" in data:
            assert "backend" in data["database"]


# ============================================================================
# Authentication Endpoint Tests
# ============================================================================


class TestAuthentication:
    """Test authentication endpoints."""

    def test_register_new_user(self, client):
        """Test user registration."""
        response = client.post(
            "/api/v1/auth/register",
            json={
                "email": "newuser@example.com",
                "username": "newuser",
                "password": "password123",
                "full_name": "New User",
            },
        )

        assert response.status_code == 200
        data = response.json()
        assert data["email"] == "newuser@example.com"
        assert data["username"] == "newuser"
        assert "id" in data
        assert "role" in data

    def test_register_duplicate_email(self, client):
        """Test registration with duplicate email."""
        # Register first user
        client.post(
            "/api/v1/auth/register",
            json={
                "email": "duplicate@example.com",
                "username": "user1",
                "password": "pass123",
            },
        )

        # Try to register with same email
        response = client.post(
            "/api/v1/auth/register",
            json={
                "email": "duplicate@example.com",
                "username": "user2",
                "password": "pass123",
            },
        )

        assert response.status_code == 400
        assert "already registered" in response.json()["detail"].lower()

    def test_register_duplicate_username(self, client):
        """Test registration with duplicate username."""
        # Register first user
        client.post(
            "/api/v1/auth/register",
            json={
                "email": "user1@example.com",
                "username": "duplicate",
                "password": "pass123",
            },
        )

        # Try to register with same username
        response = client.post(
            "/api/v1/auth/register",
            json={
                "email": "user2@example.com",
                "username": "duplicate",
                "password": "pass123",
            },
        )

        assert response.status_code == 400
        assert "username" in response.json()["detail"].lower()

    def test_login_success(self, client):
        """Test successful login."""
        # Register user
        client.post(
            "/api/v1/auth/register",
            json={
                "email": "login@example.com",
                "username": "loginuser",
                "password": "password123",
            },
        )

        # Login
        response = client.post(
            "/api/v1/auth/login",
            json={
                "email": "login@example.com",
                "password": "password123",
            },
        )

        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"
        assert "user_id" in data

    def test_login_invalid_email(self, client):
        """Test login with invalid email."""
        response = client.post(
            "/api/v1/auth/login",
            json={
                "email": "nonexistent@example.com",
                "password": "password123",
            },
        )

        assert response.status_code == 401
        assert "invalid" in response.json()["detail"].lower()

    def test_login_invalid_password(self, client):
        """Test login with invalid password."""
        # Register user
        client.post(
            "/api/v1/auth/register",
            json={
                "email": "wrongpass@example.com",
                "username": "wrongpass",
                "password": "correctpass",
            },
        )

        # Try to login with wrong password
        response = client.post(
            "/api/v1/auth/login",
            json={
                "email": "wrongpass@example.com",
                "password": "wrongpass",
            },
        )

        assert response.status_code == 401
        assert "invalid" in response.json()["detail"].lower()

    def test_get_current_user(self, client, auth_token):
        """Test getting current user info."""
        response = client.get(
            "/api/v1/auth/me",
            headers={"Authorization": f"Bearer {auth_token}"},
        )

        assert response.status_code == 200
        data = response.json()
        assert data["email"] == "test@example.com"
        assert data["username"] == "testuser"

    def test_get_current_user_unauthorized(self, client):
        """Test getting current user without auth."""
        response = client.get("/api/v1/auth/me")

        assert response.status_code == 403

    def test_get_current_user_invalid_token(self, client):
        """Test getting current user with invalid token."""
        response = client.get(
            "/api/v1/auth/me",
            headers={"Authorization": "Bearer invalid_token"},
        )

        assert response.status_code == 401


# ============================================================================
# Pattern Sync Endpoint Tests
# ============================================================================


class TestPatternSync:
    """Test pattern synchronization endpoints."""

    def test_sync_patterns(self, client, auth_token):
        """Test syncing patterns."""
        patterns = [
            {
                "name": "test_pattern",
                "description": "Test pattern",
                "version": "1.0.0",
                "content": "pattern content",
            }
        ]

        response = client.post(
            "/api/v1/patterns/sync",
            headers={"Authorization": f"Bearer {auth_token}"},
            json={"patterns": patterns},
        )

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert data["synced_count"] > 0

    def test_sync_patterns_unauthorized(self, client):
        """Test syncing patterns without auth."""
        response = client.post(
            "/api/v1/patterns/sync",
            json={"patterns": []},
        )

        assert response.status_code == 403

    def test_get_patterns(self, client, auth_token):
        """Test getting patterns."""
        # First sync a pattern
        patterns = [
            {
                "name": "get_pattern",
                "description": "Pattern to get",
                "version": "1.0.0",
                "content": "content",
            }
        ]
        client.post(
            "/api/v1/patterns/sync",
            headers={"Authorization": f"Bearer {auth_token}"},
            json={"patterns": patterns},
        )

        # Get patterns
        response = client.get(
            "/api/v1/patterns",
            headers={"Authorization": f"Bearer {auth_token}"},
        )

        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)


# ============================================================================
# Config Endpoint Tests
# ============================================================================


class TestConfig:
    """Test configuration endpoints."""

    def test_get_config(self, client, auth_token):
        """Test getting configuration."""
        response = client.get(
            "/api/v1/config",
            headers={"Authorization": f"Bearer {auth_token}"},
        )

        assert response.status_code == 200
        data = response.json()
        assert "config" in data
        assert "enforced_settings" in data

    def test_update_config(self, client, auth_token):
        """Test updating configuration."""
        config_data = {
            "setting1": "value1",
            "setting2": "value2",
        }

        response = client.put(
            "/api/v1/config",
            headers={"Authorization": f"Bearer {auth_token}"},
            json=config_data,
        )

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"


# ============================================================================
# Admin Endpoint Tests
# ============================================================================


class TestAdminEndpoints:
    """Test admin-only endpoints."""

    def test_list_users_admin(self, client, admin_token):
        """Test listing users as admin."""
        response = client.get(
            "/api/v1/admin/users",
            headers={"Authorization": f"Bearer {admin_token}"},
        )

        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)

    def test_list_users_non_admin(self, client, auth_token):
        """Test listing users as non-admin."""
        response = client.get(
            "/api/v1/admin/users",
            headers={"Authorization": f"Bearer {auth_token}"},
        )

        assert response.status_code == 403

    def test_delete_pattern_admin(self, client, admin_token):
        """Test deleting pattern as admin."""
        # First sync a pattern
        patterns = [
            {
                "name": "pattern_to_delete",
                "description": "Pattern to delete",
                "version": "1.0.0",
                "content": "content",
            }
        ]
        client.post(
            "/api/v1/patterns/sync",
            headers={"Authorization": f"Bearer {admin_token}"},
            json={"patterns": patterns},
        )

        # Delete pattern
        response = client.delete(
            "/api/v1/admin/patterns/pattern_to_delete",
            headers={"Authorization": f"Bearer {admin_token}"},
        )

        assert response.status_code == 200
        assert "deleted" in response.json()["status"].lower()


# ============================================================================
# Dashboard Endpoint Tests
# ============================================================================


class TestDashboardEndpoints:
    """Test dashboard API endpoints."""

    def test_dashboard_summary(self, client, auth_token):
        """Test dashboard summary endpoint."""
        response = client.get(
            "/api/v1/dashboard/summary",
            headers={"Authorization": f"Bearer {auth_token}"},
        )

        assert response.status_code == 200
        data = response.json()
        assert "total_bugs" in data or "pattern_effectiveness_score" in data

    def test_dashboard_chart_data(self, client, auth_token):
        """Test dashboard chart data endpoint."""
        response = client.get(
            "/api/v1/dashboard/charts/bugs",
            headers={"Authorization": f"Bearer {auth_token}"},
            params={"date_range": "30d"},
        )

        assert response.status_code == 200
        data = response.json()
        assert "labels" in data or "datasets" in data

    def test_dashboard_insights(self, client, auth_token):
        """Test dashboard insights endpoint."""
        response = client.get(
            "/api/v1/dashboard/insights",
            headers={"Authorization": f"Bearer {auth_token}"},
        )

        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, dict)


# ============================================================================
# Insights Endpoint Tests
# ============================================================================


class TestInsightsEndpoints:
    """Test insights API endpoints."""

    @patch("feedback_loop.api.insights.get_insights_engine")
    def test_get_insights(self, mock_engine, client, auth_token):
        """Test getting insights."""
        mock_insights = Mock()
        mock_insights.generate_insights.return_value = [
            {
                "title": "Test Insight",
                "description": "Test description",
                "type": "info",
                "impact": "medium",
            }
        ]
        mock_engine.return_value = mock_insights

        response = client.get(
            "/api/v1/insights/insights",
            headers={"Authorization": f"Bearer {auth_token}"},
        )

        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)

    @patch("feedback_loop.api.insights.get_insights_engine")
    def test_get_recommendations(self, mock_engine, client, auth_token):
        """Test getting recommendations."""
        mock_insights = Mock()
        mock_insights.get_recommendations.return_value = [
            {
                "action": "Test Action",
                "description": "Test description",
                "priority": "high",
                "effort": "low",
            }
        ]
        mock_engine.return_value = mock_insights

        response = client.get(
            "/api/v1/insights/recommendations",
            headers={"Authorization": f"Bearer {auth_token}"},
        )

        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)

    @patch("feedback_loop.api.insights.get_insights_engine")
    def test_get_trends(self, mock_engine, client, auth_token):
        """Test getting trends."""
        mock_insights = Mock()
        mock_insights.analyze_trends.return_value = [
            {
                "metric": "bugs",
                "trend": "decreasing",
                "change": "-10%",
                "period": "30d",
                "description": "Bugs decreasing",
            }
        ]
        mock_engine.return_value = mock_insights

        response = client.get(
            "/api/v1/insights/trends",
            headers={"Authorization": f"Bearer {auth_token}"},
        )

        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)


# ============================================================================
# Metrics Endpoint Tests
# ============================================================================


class TestMetricsEndpoints:
    """Test metrics endpoints."""

    def test_post_metrics(self, client, auth_token):
        """Test posting metrics."""
        metric_data = {
            "metric_type": "pattern_applied",
            "pattern_name": "test_pattern",
            "time_saved_seconds": 300,
        }

        response = client.post(
            "/api/v1/metrics",
            headers={"Authorization": f"Bearer {auth_token}"},
            json=metric_data,
        )

        assert response.status_code == 200
        data = response.json()
        assert "status" in data or "success" in str(data).lower()

    def test_post_metrics_unauthorized(self, client):
        """Test posting metrics without auth."""
        response = client.post(
            "/api/v1/metrics",
            json={"metric_type": "test"},
        )

        assert response.status_code == 403
