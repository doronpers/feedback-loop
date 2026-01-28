import os
import sys
from datetime import datetime

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

# Ensure src is in path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
sys.path.insert(0, project_root)
sys.path.insert(0, os.path.join(project_root, "src"))

# Mock shared_ai_utils before importing main
from unittest.mock import MagicMock

sys.modules["shared_ai_utils"] = MagicMock()

# IMPORT MAGIC: access the 'persistence' module that main.py loaded
# forcing the override on THAT get_db
import persistence.database

from feedback_loop.api.main import app

get_db = persistence.database.get_db
from persistence.models import APIKey, Base, Metric, Organization, User


@pytest.fixture(scope="function")
def db():
    # Fresh engine per test
    SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"
    engine = create_engine(
        SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}, poolclass=StaticPool
    )
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    yield db
    db.close()
    try:
        engine.dispose()
    except:
        pass


@pytest.fixture(scope="function")
def client(db):
    def override_get_db():
        try:
            yield db
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    yield TestClient(app)
    del app.dependency_overrides[get_db]


def test_create_user_and_org(db, client):
    # Register user
    response = client.post(
        "/api/v1/auth/register",
        json={
            "email": "test@example.com",
            "username": "testuser",
            "password": "password123",
            "organization_name": "TestOrg",
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == "test@example.com"
    assert data["role"] == "admin"

    # Verify DB
    user = db.query(User).filter(User.email == "test@example.com").first()
    assert user is not None
    assert user.organization.name == "TestOrg"


def test_login_and_api_key(client):
    # Register
    client.post(
        "/api/v1/auth/register",
        json={
            "email": "user2@example.com",
            "username": "user2",
            "password": "password123",
            "organization_name": "Org2",
        },
    )

    # Login
    response = client.post(
        "/api/v1/auth/login", json={"email": "user2@example.com", "password": "password123"}
    )
    assert response.status_code == 200
    data = response.json()
    token = data["access_token"]
    assert token.startswith("fl_")

    # Access protected route
    response = client.get("/api/v1/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    assert response.json()["username"] == "user2"


def test_metrics_persistence(client, db):
    # Register & Login
    client.post(
        "/api/v1/auth/register", json={"email": "m@ex.com", "username": "m", "password": "p"}
    )
    login_res = client.post("/api/v1/auth/login", json={"email": "m@ex.com", "password": "p"})
    token = login_res.json()["access_token"]

    # Submit metrics
    metrics_data = {"bugs": [{"pattern": "TestPattern", "count": 5}]}
    response = client.post(
        "/api/v1/metrics", json=metrics_data, headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200

    # Verify in DB
    metric = db.query(Metric).first()
    assert metric is not None
    assert metric.data["bugs"][0]["pattern"] == "TestPattern"


def test_dashboard_summary(client, db):
    # Register & Login & Submit Metrics
    client.post(
        "/api/v1/auth/register", json={"email": "d@ex.com", "username": "d", "password": "p"}
    )
    login_res = client.post("/api/v1/auth/login", json={"email": "d@ex.com", "password": "p"})
    token = login_res.json()["access_token"]

    metrics_data = {
        "bugs": [{"pattern": "P1", "count": 2}],
        "test_failures": [{"pattern_violated": "P1", "count": 3}],
    }
    client.post("/api/v1/metrics", json=metrics_data, headers={"Authorization": f"Bearer {token}"})

    response = client.get("/dashboard/summary")
    assert response.status_code == 200
    data = response.json()
    assert data["total_bugs"] == 1
    assert data["total_test_failures"] == 1
