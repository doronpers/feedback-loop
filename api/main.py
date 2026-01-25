"""
FastAPI Application - Cloud Backend API Gateway

Centralized API gateway for feedback-loop team collaboration platform.
Handles authentication, pattern sync, team management, and analytics.
"""

import logging
import os
import secrets
import sys
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional

# Load .env file from project root
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))
from metrics.env_loader import load_env_file

load_env_file(project_root)

from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from passlib.context import CryptContext
from pydantic import BaseModel, EmailStr

# Import dashboard router
from api.dashboard import router as dashboard_router
from api.insights import router as insights_router

logger = logging.getLogger(__name__)

# Password hashing context - using bcrypt for better GPU-resistance than PBKDF2
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


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
            logger.warning(
                "Wildcard CORS origin detected. This should not be used in production."
            )

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


def create_token_str(user_id: int) -> str:
    """Generate a secure API key/token."""
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
    db: DbSession = Depends(get_db),
) -> models.User:
    """Verify API key and return current user."""
    token = credentials.credentials

    # Look up session by token
    session = db.query(models.Session).filter(models.Session.token == token).first()
    if not session:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired API key",
        )

    # Check expiration if applicable (optional, not implemented in models yet fully/enforced)
    if session.expires_at and session.expires_at < datetime.utcnow():
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token expired",
        )

    return session.user


async def require_admin(
    current_user: models.User = Depends(get_current_user),
) -> models.User:
    """Require admin role for endpoint access."""
    if current_user.get("role") != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Admin access required"
        )
    return current_user


# ============================================================================
# API Endpoints
# ============================================================================


@app.get("/api/v1/health")
async def health_check(db: DbSession = Depends(get_db)):
    """Health check endpoint."""
    try:
        # Simple DB check
        db.execute("SELECT 1")
        db_status = "connected"
    except Exception:
        db_status = "disconnected"

    return {
        "status": "healthy",
        "database": db_status,
        "timestamp": datetime.utcnow().isoformat(),
        "version": "0.1.0",
    }


@app.post("/api/v1/auth/login", response_model=LoginResponse)
async def login(request: LoginRequest, db: DbSession = Depends(get_db)):
    """
    Authenticate user and return API key.

    This endpoint supports the 'feedback-loop login' command in the CLI.
    """
    # Find user by email
    user = db.query(models.User).filter(models.User.email == request.email).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email or password"
        )

    # Verify password
    if not verify_password(request.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email or password"
        )

    # Generate API key
    token_str = create_token_str(user.id)

    # Store session in DB
    session = models.Session(
        token=token_str,
        user_id=user.id,
        created_at=datetime.utcnow(),
        # Optional: set expires_at
    )
    db.add(session)

    # Update last login
    user.last_login = datetime.utcnow()
    db.commit()
    db.refresh(session)

    return LoginResponse(
        access_token=token_str,
        user_id=user.id,
        organization_id=user.organization_id,
        username=user.username,
        role=user.role,
    )


@app.post("/api/v1/auth/register", response_model=UserResponse)
async def register(request: UserCreate, db: DbSession = Depends(get_db)):
    """Register a new user and organization."""
    # Check if email or username already exists
    existing_user = (
        db.query(models.User)
        .filter(
            or_(
                models.User.email == request.email,
                models.User.username == request.username,
            )
        )
        .first()
    )

    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email or Username already registered",
        )

    # Create organization if provided or default
    # If explicit name provided, try to find or create
    org = None
    if request.organization_name:
        org = (
            db.query(models.Organization)
            .filter(models.Organization.name == request.organization_name)
            .first()
        )
        if not org:
            org = models.Organization(name=request.organization_name)
            db.add(org)
            db.commit()
            db.refresh(org)
    else:
        # Default org logic (e.g. "Default Org" or create one per user?)
        # For simple migration, let's look for "Default Organization" or create it
        org = (
            db.query(models.Organization)
            .filter(models.Organization.name == "Default Organization")
            .first()
        )
        if not org:
            org = models.Organization(name="Default Organization")
            db.add(org)
            db.commit()
            db.refresh(org)

    # Create user
    # Check if it's the first user ever?
    user_count = db.query(models.User).count()
    role = "admin" if user_count == 0 else "developer"

    user = models.User(
        email=request.email,
        username=request.username,
        full_name=request.full_name,
        hashed_password=hash_password(request.password),
        role=role,
        organization_id=org.id,
        is_active=True,
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    return UserResponse(
        id=user.id,
        username=user.username,
        email=user.email,
        full_name=user.full_name,
        role=user.role,
        organization_id=user.organization_id,
        created_at=user.created_at,
    )


@app.get("/api/v1/auth/me", response_model=UserResponse)
async def get_current_user_info(current_user: models.User = Depends(get_current_user)):
    """Get current authenticated user information."""
    user = USERS_DB.get(current_user["user_id"])
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )

    return UserResponse(
        id=current_user.id,
        username=current_user.username,
        email=current_user.email,
        full_name=current_user.full_name,
        role=current_user.role,
        organization_id=current_user.organization_id,
        created_at=current_user.created_at,
    )


@app.post("/api/v1/patterns/sync", response_model=PatternSyncResponse)
async def sync_patterns(
    request: PatternSync, current_user: dict = Depends(get_current_user)
):
    """
    Sync patterns to cloud storage.

    Implements bi-directional sync with conflict resolution.
    """
    org_id = current_user.organization_id
    user_id = current_user.id

    conflicts = []
    synced_count = 0

    for pattern_data in request.patterns:
        pattern_name = pattern_data.get("name")
        if not pattern_name:
            continue

        # Check for existing
        existing = (
            db.query(models.Pattern)
            .filter(
                models.Pattern.organization_id == org_id,
                models.Pattern.name == pattern_name,
            )
            .first()
        )

        if existing:
            # Simple conflict detection - check version
            if existing.version != pattern_data.get("version", 0):
                conflicts.append(
                    {
                        "pattern": pattern_name,
                        "reason": "Version mismatch",
                        "server_version": existing.version,
                        "client_version": pattern_data.get("version"),
                    }
                )
                continue

            # Update existing
            existing.description = pattern_data.get("description")
            existing.bad_example = pattern_data.get("bad_example")
            existing.good_example = pattern_data.get("good_example")
            existing.severity = pattern_data.get("severity", "medium")
            existing.occurrence_frequency = pattern_data.get("occurrence_frequency", 0)
            existing.effectiveness_score = pattern_data.get("effectiveness_score", 0.5)
            existing.version = pattern_data.get("version", 1) + 1
            existing.last_modified_by = user_id
            existing.last_modified_at = datetime.utcnow()

        else:
            # Create new
            new_pattern = models.Pattern(
                name=pattern_name,
                description=pattern_data.get("description"),
                bad_example=pattern_data.get("bad_example"),
                good_example=pattern_data.get("good_example"),
                severity=pattern_data.get("severity", "medium"),
                occurrence_frequency=pattern_data.get("occurrence_frequency", 0),
                effectiveness_score=pattern_data.get("effectiveness_score", 0.5),
                version=pattern_data.get("version", 1) + 1,
                last_modified_by=user_id,
                last_modified_at=datetime.utcnow(),
                organization_id=org_id,
            )
            db.add(new_pattern)

        synced_count += 1

    db.commit()

    return PatternSyncResponse(
        status="success",
        synced_count=synced_count,
        conflicts=conflicts,
        timestamp=datetime.utcnow(),
    )


@app.get("/api/v1/patterns/pull")
async def pull_patterns(
    current_user: models.User = Depends(get_current_user),
    db: DbSession = Depends(get_db),
):
    """
    Pull patterns from cloud storage.

    Returns all patterns for the user's organization.
    """
    patterns = (
        db.query(models.Pattern)
        .filter(models.Pattern.organization_id == current_user.organization_id)
        .all()
    )

    # Convert to dicts for simple response
    # (In a real app, use a proper Pydantic scheme Response model with orm_mode=True)
    # But for now matching the manual dict structure
    pattern_list = []
    for p in patterns:
        pattern_list.append(
            {
                "name": p.name,
                "description": p.description,
                "bad_example": p.bad_example,
                "good_example": p.good_example,
                "severity": p.severity,
                "occurrence_frequency": p.occurrence_frequency,
                "effectiveness_score": p.effectiveness_score,
                "version": p.version,
            }
        )

    return {
        "patterns": pattern_list,
        "count": len(pattern_list),
        "organization_id": current_user.organization_id,
        "timestamp": datetime.utcnow().isoformat(),
    }


@app.get("/api/v1/config", response_model=ConfigResponse)
async def get_config(
    current_user: models.User = Depends(get_current_user),
    db: DbSession = Depends(get_db),
):
    """
    Get team configuration.

    Returns enforced settings and team-specific configuration.
    """
    org_id = current_user.organization_id

    # Get organization config
    config_obj = (
        db.query(models.Config).filter(models.Config.organization_id == org_id).first()
    )

    config_data = (
        config_obj.settings
        if config_obj
        else {
            "min_confidence_threshold": 0.8,
            "security_checks_required": True,
            "auto_sync_enabled": True,
        }
    )

    enforced = (
        config_obj.enforced_settings
        if config_obj
        else ["security_checks_required", "min_confidence_threshold"]
    )

    return ConfigResponse(
        config=config_data,
        enforced_settings=enforced,
        team_id=None,
        organization_id=org_id,
    )


@app.post("/api/v1/config")
async def update_config(
    config: dict,
    current_user: models.User = Depends(require_admin),
    db: DbSession = Depends(get_db),
):
    """
    Update team configuration (admin only).
    """
    org_id = current_user.organization_id

    config_obj = (
        db.query(models.Config).filter(models.Config.organization_id == org_id).first()
    )
    if not config_obj:
        config_obj = models.Config(organization_id=org_id, settings=config)
        db.add(config_obj)
    else:
        config_obj.settings = config

    db.commit()

    return {
        "status": "success",
        "message": "Configuration updated",
        "organization_id": org_id,
        "timestamp": datetime.utcnow().isoformat(),
    }


@app.post("/api/v1/metrics")
async def submit_metrics(
    metrics: dict,
    current_user: models.User = Depends(get_current_user),
    db: DbSession = Depends(get_db),
):
    """
    Submit metrics for analytics.
    """
    # TODO: Store metrics in database for analytics (Phase 3)
    # For now, just acknowledge receipt

    return {
        "status": "success",
        "message": "Metrics received",
        "organization_id": current_user.organization_id,
        "user_id": current_user.id,
        "timestamp": datetime.utcnow().isoformat(),
    }


# ============================================================================
# Admin Endpoints
# ============================================================================


@app.get("/api/v1/admin/users")
async def list_users(
    current_user: models.User = Depends(require_admin), db: DbSession = Depends(get_db)
):
    """List all users in organization (admin only)."""
    users_list = (
        db.query(models.User)
        .filter(models.User.organization_id == current_user.organization_id)
        .all()
    )

    users = [
        {
            "id": u.id,
            "username": u.username,
            "email": u.email,
            "role": u.role,
            "is_active": u.is_active,
        }
        for u in users_list
    ]

    return {
        "users": users,
        "count": len(users),
        "organization_id": current_user.organization_id,
    }


@app.delete("/api/v1/admin/patterns/{pattern_name}")
async def delete_pattern(
    pattern_name: str, current_user: dict = Depends(require_admin)
):
    """Delete a pattern (admin only)."""
    org_id = current_user["organization_id"]

    if org_id not in PATTERNS_DB or pattern_name not in PATTERNS_DB[org_id]:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Pattern not found"
        )

    db.delete(pattern)
    db.commit()

    return {
        "status": "success",
        "message": f"Pattern '{pattern_name}' deleted",
        "timestamp": datetime.utcnow().isoformat(),
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
