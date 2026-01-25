"""
Database Models

Defines the database schema for users, organizations, teams, and patterns.
Uses SQLAlchemy for ORM and supports both SQLite (local) and PostgreSQL (production).
"""

from datetime import datetime
from enum import Enum
from typing import Any, List, Optional

from sqlalchemy import JSON, Boolean, Column, DateTime
from sqlalchemy import Enum as SQLEnum
from sqlalchemy import ForeignKey, Integer, String, Table, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base: Any = declarative_base()


class UserRole(str, Enum):
    """User roles for RBAC (Role-Based Access Control)."""

    ADMIN = "admin"  # Can delete patterns, manage team, view analytics
    DEVELOPER = "developer"  # Can read/write patterns
    VIEWER = "viewer"  # Read-only access


class SubscriptionTier(str, Enum):
    """Subscription tiers for the platform."""

    FREE = "free"  # Single-user, local only
    TEAM = "team"  # $25/user/month - Team sync and basic analytics
    ENTERPRISE = "enterprise"  # $50+/user/month - SSO, compliance, self-hosted


# Association table for many-to-many relationship between users and teams
user_teams = Table(
    "user_teams",
    Base.metadata,
    Column("user_id", Integer, ForeignKey("users.id"), primary_key=True),
    Column("team_id", Integer, ForeignKey("teams.id"), primary_key=True),
    Column("role", SQLEnum(UserRole), default=UserRole.DEVELOPER),
    Column("joined_at", DateTime, default=datetime.utcnow),
)


class Organization(Base):
    """Organization model for multi-tenant architecture."""

    __tablename__ = "organizations"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False, index=True)
    slug = Column(String(100), unique=True, nullable=False, index=True)
    subscription_tier = Column(SQLEnum(SubscriptionTier), default=SubscriptionTier.FREE)

    # Settings
    settings = Column(JSON, default=dict)  # Org-wide settings

    # Audit fields
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    teams = relationship("Team", back_populates="organization", cascade="all, delete-orphan")
    users = relationship("User", back_populates="organization", cascade="all, delete-orphan")
    patterns = relationship("Pattern", back_populates="organization", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Organization(id={self.id}, name='{self.name}', tier='{self.subscription_tier}')>"


class Team(Base):
    """Team model for organizing users within an organization."""

    __tablename__ = "teams"

    id = Column(Integer, primary_key=True, index=True)
    organization_id = Column(Integer, ForeignKey("organizations.id"), nullable=False)
    name = Column(String(255), nullable=False, index=True)
    slug = Column(String(100), nullable=False, index=True)
    description = Column(Text, nullable=True)

    # Team-specific settings (can override org settings)
    settings = Column(JSON, default=dict)

    # Audit fields
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    organization = relationship("Organization", back_populates="teams")
    users = relationship("User", secondary=user_teams, back_populates="teams")
    patterns = relationship("Pattern", back_populates="team", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Team(id={self.id}, name='{self.name}', org_id={self.organization_id})>"


class User(Base):
    """User model with authentication and RBAC."""

    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    organization_id = Column(Integer, ForeignKey("organizations.id"), nullable=False)

    # Authentication
    email = Column(String(255), unique=True, nullable=False, index=True)
    username = Column(String(100), unique=True, nullable=False, index=True)
    hashed_password = Column(String(255), nullable=False)
    api_key = Column(String(255), unique=True, nullable=True, index=True)

    # Profile
    full_name = Column(String(255), nullable=True)
    avatar_url = Column(String(500), nullable=True)

    # Role and status
    role = Column(SQLEnum(UserRole), default=UserRole.DEVELOPER)
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)

    # SSO/SAML fields (for Enterprise tier)
    sso_provider = Column(String(50), nullable=True)  # okta, azure_ad, etc.
    sso_id = Column(String(255), nullable=True, index=True)

    # Audit fields
    last_login = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    organization = relationship("Organization", back_populates="users")
    teams = relationship("Team", secondary=user_teams, back_populates="users")
    patterns = relationship("Pattern", back_populates="author", foreign_keys="Pattern.author_id")
    audit_logs = relationship("AuditLog", back_populates="user", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<User(id={self.id}, username='{self.username}', role='{self.role}')>"


class Pattern(Base):
    """Pattern model for storing learned development patterns."""

    __tablename__ = "patterns"

    id = Column(Integer, primary_key=True, index=True)
    organization_id = Column(Integer, ForeignKey("organizations.id"), nullable=False)
    team_id = Column(Integer, ForeignKey("teams.id"), nullable=True)
    author_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    # Pattern metadata
    name = Column(String(255), nullable=False, index=True)
    description = Column(Text, nullable=False)
    category = Column(String(100), nullable=True, index=True)
    severity = Column(String(50), nullable=True)  # low, medium, high, critical

    # Pattern content
    pattern_data = Column(JSON, nullable=False)  # Full pattern details
    code_example = Column(Text, nullable=True)
    solution = Column(Text, nullable=True)

    # Metrics
    frequency = Column(Integer, default=0)
    effectiveness_score = Column(Integer, default=0)
    times_applied = Column(Integer, default=0)

    # Versioning
    version = Column(Integer, default=1)
    parent_id = Column(Integer, ForeignKey("patterns.id"), nullable=True)

    # Status
    is_active = Column(Boolean, default=True)
    is_archived = Column(Boolean, default=False)

    # Audit fields
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_applied = Column(DateTime, nullable=True)

    # Relationships
    organization = relationship("Organization", back_populates="patterns")
    team = relationship("Team", back_populates="patterns")
    author = relationship("User", back_populates="patterns", foreign_keys=[author_id])
    versions = relationship("Pattern", remote_side=[parent_id])

    def __repr__(self):
        return f"<Pattern(id={self.id}, name='{self.name}', version={self.version})>"


class AuditLog(Base):
    """Audit log for compliance and tracking changes."""

    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)

    # Event details
    action = Column(String(100), nullable=False, index=True)  # create, update, delete, login, etc.
    resource_type = Column(String(100), nullable=False)  # pattern, user, team, etc.
    resource_id = Column(Integer, nullable=True)

    # Change tracking
    old_values = Column(JSON, nullable=True)
    new_values = Column(JSON, nullable=True)

    # Context
    ip_address = Column(String(45), nullable=True)
    user_agent = Column(String(500), nullable=True)

    # Timestamp
    created_at = Column(DateTime, default=datetime.utcnow, index=True)

    # Relationships
    user = relationship("User", back_populates="audit_logs")

    def __repr__(self):
        return f"<AuditLog(id={self.id}, action='{self.action}', resource='{self.resource_type}')>"


class Config(Base):
    """Configuration storage for team-wide settings."""

    __tablename__ = "configs"

    id = Column(Integer, primary_key=True, index=True)
    organization_id = Column(Integer, ForeignKey("organizations.id"), nullable=False)
    team_id = Column(Integer, ForeignKey("teams.id"), nullable=True)

    # Config metadata
    key = Column(String(255), nullable=False, index=True)
    value = Column(JSON, nullable=False)
    description = Column(Text, nullable=True)

    # Settings enforcement
    is_enforced = Column(Boolean, default=False)  # If True, users cannot override

    # Audit fields
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f"<Config(id={self.id}, key='{self.key}', enforced={self.is_enforced})>"


class Metric(Base):
    """Metrics storage for analytics and ROI calculations."""

    __tablename__ = "metrics"

    id = Column(Integer, primary_key=True, index=True)
    organization_id = Column(Integer, ForeignKey("organizations.id"), nullable=False)
    team_id = Column(Integer, ForeignKey("teams.id"), nullable=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)

    # Metric data
    metric_type = Column(
        String(100), nullable=False, index=True
    )  # pattern_applied, bug_found, etc.
    metric_data = Column(JSON, nullable=False)

    # ROI calculation fields
    time_saved_seconds = Column(Integer, default=0)
    pattern_id = Column(Integer, ForeignKey("patterns.id"), nullable=True)

    # Timestamp
    created_at = Column(DateTime, default=datetime.utcnow, index=True)

    def __repr__(self):
        return f"<Metric(id={self.id}, type='{self.metric_type}', time_saved={self.time_saved_seconds}s)>"
