"""
FastAPI Application - Cloud Backend API Gateway

Centralized API gateway for feedback-loop team collaboration platform.
Handles authentication, pattern sync, team management, and analytics.
"""

import logging
import os
import secrets
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from passlib.context import CryptContext
from pydantic import BaseModel, EmailStr

# Load .env file from project root
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))
from api.dashboard import router as dashboard_router  # noqa: E402
from api.insights import router as insights_router  # noqa: E402

from metrics.env_loader import load_env_file  # noqa: E402
from config import FeedbackLoopConfig, get_config  # noqa: E402
from persistence import get_backend, PersistenceBackend  # noqa: E402

load_env_file(project_root)

logger = logging.getLogger(__name__)

# Password hashing context - using bcrypt for better GPU-resistance than PBKDF2
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Global persistence backend (initialized on startup)
_persistence_backend: Optional[PersistenceBackend] = None


def get_persistence() -> PersistenceBackend:
    """Get the global persistence backend instance."""
    global _persistence_backend
    if _persistence_backend is None:
        raise RuntimeError(
            "Persistence backend not initialized. "
            "This should only happen if the startup event failed."
        )
    return _persistence_backend


app = FastAPI(
    title="Feedback Loop API",
    description="Cloud backend API for feedback-loop team collaboration",
    version="0.1.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
)


# CORS configuration for web dashboard.
# Use FEEDBACK_LOOP_ALLOWED_ORIGINS (comma-separated) to set allowed origins.
def parse_allowed_origins(raw_value: Optional[str]) -> List[str]:
    """Parse allowed origins from env configuration.

    Hardened: Defaults to localhost only for security.
    Raises warning if wildcard detected in production.
    """
    if not raw_value:
        # Strict default - localhost only
        return ["http://localhost:3000"]

    origins = [origin.strip() for origin in raw_value.split(",") if origin.strip()]

    # Security check: warn if wildcard detected in production
    if "*" in origins:
        env = os.getenv("ENVIRONMENT", "development").lower()
        if env in ("production", "prod"):
            logger.warning(
                "SECURITY WARNING: Wildcard CORS origin detected in production! "
                "This is a major security risk. Use specific origins instead."
            )
        else:
            logger.warning("Wildcard CORS origin detected. This should not be used in production.")

    return origins


allowed_origins = parse_allowed_origins(os.getenv("FEEDBACK_LOOP_ALLOWED_ORIGINS"))

# CORS middleware for web dashboard
app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

security = HTTPBearer()


# ============================================================================
# Startup & Shutdown Events
# ============================================================================


@app.on_event("startup")
async def startup_event():
    """Initialize database connection and run migrations on startup."""
    global _persistence_backend

    try:
        # Load configuration
        config = get_config()

        logger.info(f"Initializing persistence backend: {config.database.type.value}")
        logger.info(f"Database URI: {config.get_db_uri()}")

        # Create backend
        _persistence_backend = get_backend(config.get_db_uri())

        # Connect to database
        _persistence_backend.connect()

        # Run migrations if configured
        if config.database.auto_migrate:
            logger.info("Running database migrations...")
            _persistence_backend.migrate()
            logger.info("Database migrations completed")

        # Log health check
        health = _persistence_backend.health_check()
        logger.info(f"Persistence health: {health['status']}")

    except Exception as e:
        logger.error(f"Failed to initialize persistence backend: {e}")
        raise


@app.on_event("shutdown")
async def shutdown_event():
    """Close database connection on shutdown."""
    global _persistence_backend

    if _persistence_backend:
        try:
            _persistence_backend.disconnect()
            logger.info("Persistence backend disconnected")
        except Exception as e:
            logger.error(f"Error disconnecting from database: {e}")


# Include dashboard router
app.include_router(dashboard_router)
app.include_router(insights_router)


# ============================================================================
# Request/Response Models
# ============================================================================


class LoginRequest(BaseModel):
    """Login request model."""

    email: EmailStr
    password: str


class LoginResponse(BaseModel):
    """Login response model."""

    access_token: str
    token_type: str = "bearer"
    user_id: int
    organization_id: int
    username: str
    role: str


class UserCreate(BaseModel):
    """User creation request."""

    email: EmailStr
    username: str
    password: str
    full_name: Optional[str] = None
    organization_name: Optional[str] = None


class UserResponse(BaseModel):
    """User response model."""

    id: int
    username: str
    email: str
    full_name: Optional[str]
    role: str
    organization_id: int
    created_at: datetime


class PatternSync(BaseModel):
    """Pattern synchronization request."""

    patterns: List[dict]


class PatternSyncResponse(BaseModel):
    """Pattern synchronization response."""

    status: str
    synced_count: int
    conflicts: List[dict] = []
    timestamp: datetime


class ConfigResponse(BaseModel):
    """Configuration response model."""

    config: dict
    enforced_settings: List[str]
    team_id: Optional[int]
    organization_id: int


# ============================================================================
# In-Memory Storage (Replace with database in production)
# ============================================================================

# TODO: PRODUCTION - Replace with PostgreSQL database
# In-memory dictionaries lose data on restart and don't support concurrent access
# See Documentation/PRODUCTION_CHECKLIST.md for migration plan
USERS_DB: Dict[int, dict] = {}
SESSIONS_DB: Dict[str, dict] = {}
PATTERNS_DB: Dict[int, Dict[str, dict]] = {}
CONFIG_DB: Dict[int, dict] = {}


# ============================================================================
# Authentication & Authorization
# ============================================================================


def create_api_key(user_id: int) -> str:
    """Generate a secure API key."""
    random_str = secrets.token_urlsafe(32)
    return f"fl_{user_id}_{random_str}"


def hash_password(password: str) -> str:
    """Hash password using bcrypt for better GPU-resistance than PBKDF2.

    Optimized: Uses bcrypt via passlib CryptContext for standardized,
    production-ready password hashing.
    """
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify password against bcrypt hash.

    Optimized: Standardized on CryptContext; removed legacy SHA-256 fallback
    to prevent downgrade attacks.
    """
    return pwd_context.verify(plain_password, hashed_password)


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
) -> dict:
    """Verify API key and return current user."""
    api_key = credentials.credentials

    # Look up user by API key
    user = SESSIONS_DB.get(api_key)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired API key",
        )

    return user


async def require_admin(current_user: dict = Depends(get_current_user)) -> dict:
    """Require admin role for endpoint access."""
    if current_user.get("role") != "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin access required")
    return current_user


# ============================================================================
# API Endpoints
# ============================================================================


@app.get("/")
async def root():
    """Root endpoint - redirect to dashboard."""
    from fastapi.responses import RedirectResponse

    return RedirectResponse(url="/dashboard/")


@app.get("/api/v1/health")
async def health_check():
    """Health check endpoint with persistence backend diagnostics."""
    try:
        persistence = get_persistence()
        if persistence:
            db_health = persistence.health_check()
            return {
                "status": "healthy",
                "timestamp": datetime.utcnow().isoformat(),
                "version": "0.1.0",
                "database": db_health,
            }
        else:
            return {
                "status": "warning",
                "timestamp": datetime.utcnow().isoformat(),
                "version": "0.1.0",
                "message": "Persistence backend not initialized",
            }
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return {
            "status": "unhealthy",
            "timestamp": datetime.utcnow().isoformat(),
            "version": "0.1.0",
            "error": str(e),
        }


@app.post("/api/v1/auth/login", response_model=LoginResponse)
async def login(request: LoginRequest):
    """
    Authenticate user and return API key.

    This endpoint supports the 'feedback-loop login' command in the CLI.
    """
    # Find user by email
    user = None
    for _uid, u in USERS_DB.items():
        if u["email"] == request.email:
            user = u
            break

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email or password"
        )

    # Verify password
    if not verify_password(request.password, user["hashed_password"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email or password"
        )

    # Generate API key
    api_key = create_api_key(user["id"])

    # Store session
    SESSIONS_DB[api_key] = {
        "user_id": user["id"],
        "username": user["username"],
        "email": user["email"],
        "role": user["role"],
        "organization_id": user["organization_id"],
        "created_at": datetime.utcnow().isoformat(),
    }

    # Update last login
    user["last_login"] = datetime.utcnow().isoformat()

    return LoginResponse(
        access_token=api_key,
        user_id=user["id"],
        organization_id=user["organization_id"],
        username=user["username"],
        role=user["role"],
    )


@app.post("/api/v1/auth/register", response_model=UserResponse)
async def register(request: UserCreate):
    """Register a new user and organization."""
    # Check if email already exists
    for user in USERS_DB.values():
        if user["email"] == request.email:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered",
            )
        if user["username"] == request.username:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="Username already taken"
            )

    # Create organization if provided
    org_id = 1  # Default org
    if request.organization_name:
        org_id = len(USERS_DB) + 1  # Simple ID generation

    # Create user
    user_id = len(USERS_DB) + 1
    user = {
        "id": user_id,
        "email": request.email,
        "username": request.username,
        "full_name": request.full_name,
        "hashed_password": hash_password(request.password),
        "role": "admin" if not USERS_DB else "developer",  # First user is admin
        "organization_id": org_id,
        "is_active": True,
        "created_at": datetime.utcnow().isoformat(),
    }

    USERS_DB[user_id] = user

    return UserResponse(
        id=user["id"],
        username=user["username"],
        email=user["email"],
        full_name=user["full_name"],
        role=user["role"],
        organization_id=user["organization_id"],
        created_at=datetime.utcnow(),
    )


@app.get("/api/v1/auth/me", response_model=UserResponse)
async def get_current_user_info(current_user: dict = Depends(get_current_user)):
    """Get current authenticated user information."""
    user = USERS_DB.get(current_user["user_id"])
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    return UserResponse(
        id=user["id"],
        username=user["username"],
        email=user["email"],
        full_name=user.get("full_name"),
        role=user["role"],
        organization_id=user["organization_id"],
        created_at=datetime.fromisoformat(user["created_at"]),
    )


@app.post("/api/v1/patterns/sync", response_model=PatternSyncResponse)
async def sync_patterns(request: PatternSync, current_user: dict = Depends(get_current_user)):
    """
    Sync patterns to cloud storage.

    Implements bi-directional sync with conflict resolution.
    """
    org_id = current_user["organization_id"]
    user_id = current_user["user_id"]

    # Initialize organization patterns if not exists
    if org_id not in PATTERNS_DB:
        PATTERNS_DB[org_id] = {}

    conflicts = []
    synced_count = 0

    for pattern in request.patterns:
        pattern_name = pattern.get("name")
        if not pattern_name:
            continue

        # Check for conflicts
        existing = PATTERNS_DB[org_id].get(pattern_name)
        if existing:
            # Simple conflict detection - check last modified
            if existing.get("version", 0) != pattern.get("version", 0):
                conflicts.append(
                    {
                        "pattern": pattern_name,
                        "reason": "Version mismatch",
                        "server_version": existing.get("version"),
                        "client_version": pattern.get("version"),
                    }
                )
                continue

        # Store pattern with metadata
        pattern["last_modified_by"] = user_id
        pattern["last_modified_at"] = datetime.utcnow().isoformat()
        pattern["version"] = pattern.get("version", 1) + 1

        PATTERNS_DB[org_id][pattern_name] = pattern
        synced_count += 1

    return PatternSyncResponse(
        status="success",
        synced_count=synced_count,
        conflicts=conflicts,
        timestamp=datetime.utcnow(),
    )


@app.get("/api/v1/patterns/pull")
async def pull_patterns(current_user: dict = Depends(get_current_user)):
    """
    Pull patterns from cloud storage.

    Returns all patterns for the user's organization.
    """
    org_id = current_user["organization_id"]

    patterns = list(PATTERNS_DB.get(org_id, {}).values())

    return {
        "patterns": patterns,
        "count": len(patterns),
        "organization_id": org_id,
        "timestamp": datetime.utcnow().isoformat(),
    }


@app.get("/api/v1/config", response_model=ConfigResponse)
async def get_config(current_user: dict = Depends(get_current_user)):
    """
    Get team configuration.

    Returns enforced settings and team-specific configuration.
    """
    org_id = current_user["organization_id"]

    # Get organization config
    config = CONFIG_DB.get(
        org_id,
        {
            "min_confidence_threshold": 0.8,
            "security_checks_required": True,
            "auto_sync_enabled": True,
        },
    )

    # List enforced settings (cannot be overridden by users)
    enforced_settings = ["security_checks_required", "min_confidence_threshold"]

    return ConfigResponse(
        config=config,
        enforced_settings=enforced_settings,
        team_id=None,  # TODO: Implement team selection
        organization_id=org_id,
    )


@app.post("/api/v1/config")
async def update_config(config: dict, current_user: dict = Depends(require_admin)):
    """
    Update team configuration (admin only).

    Allows team leads to enforce specific settings across all team members.
    """
    org_id = current_user["organization_id"]

    CONFIG_DB[org_id] = config

    return {
        "status": "success",
        "message": "Configuration updated",
        "organization_id": org_id,
        "timestamp": datetime.utcnow().isoformat(),
    }


@app.post("/api/v1/metrics")
async def submit_metrics(metrics: dict, current_user: dict = Depends(get_current_user)):
    """
    Submit metrics for analytics.

    Used for ROI calculations and team analytics dashboard.
    Metrics are persisted to the configured database backend (SQLite/PostgreSQL).
    """
    org_id = current_user["organization_id"]
    user_id = current_user["user_id"]

    try:
        # Add metadata to metrics
        metrics_with_meta = {
            "data": metrics,
            "user_id": user_id,
            "organization_id": org_id,
            "submitted_at": datetime.utcnow().isoformat(),
        }

        # Store in persistence backend
        persistence = get_persistence()
        if persistence:
            persistence.store_metric("user_metrics", metrics_with_meta)
            logger.info(f"Metrics stored for user {user_id} in org {org_id}")
        else:
            logger.warning("Persistence backend not available, metrics not stored")

        return {
            "status": "success",
            "message": "Metrics received and stored",
            "organization_id": org_id,
            "user_id": user_id,
            "timestamp": datetime.utcnow().isoformat(),
        }
    except Exception as e:
        logger.error(f"Failed to store metrics: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to store metrics"
        )


# ============================================================================
# Admin Endpoints
# ============================================================================


@app.get("/api/v1/admin/users")
async def list_users(current_user: dict = Depends(require_admin)):
    """List all users in organization (admin only)."""
    org_id = current_user["organization_id"]

    users = [
        {
            "id": u["id"],
            "username": u["username"],
            "email": u["email"],
            "role": u["role"],
            "is_active": u.get("is_active", True),
        }
        for u in USERS_DB.values()
        if u["organization_id"] == org_id
    ]

    return {"users": users, "count": len(users), "organization_id": org_id}


@app.delete("/api/v1/admin/patterns/{pattern_name}")
async def delete_pattern(pattern_name: str, current_user: dict = Depends(require_admin)):
    """Delete a pattern (admin only)."""
    org_id = current_user["organization_id"]

    if org_id not in PATTERNS_DB or pattern_name not in PATTERNS_DB[org_id]:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Pattern not found")

    del PATTERNS_DB[org_id][pattern_name]

    return {
        "status": "success",
        "message": f"Pattern '{pattern_name}' deleted",
        "timestamp": datetime.utcnow().isoformat(),
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
