from datetime import datetime
from typing import List, Optional

from sqlalchemy import JSON, Boolean, Column, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship

from .database import Base


class Organization(Base):
    __tablename__ = "organizations"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Config stored as JSON
    config = Column(JSON, default={})

    users = relationship("User", back_populates="organization")
    patterns = relationship("Pattern", back_populates="organization")


class APIKey(Base):
    __tablename__ = "api_keys"

    key = Column(String, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    name = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    last_used_at = Column(DateTime, nullable=True)
    is_active = Column(Boolean, default=True)

    user = relationship("User", back_populates="api_keys")


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    username = Column(String, unique=True, index=True)
    full_name = Column(String, nullable=True)
    hashed_password = Column(String)
    role = Column(String, default="developer")
    organization_id = Column(Integer, ForeignKey("organizations.id"))
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    last_login = Column(DateTime, nullable=True)

    organization = relationship("Organization", back_populates="users")
    api_keys = relationship("APIKey", back_populates="user")


class Pattern(Base):
    __tablename__ = "patterns"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    organization_id = Column(Integer, ForeignKey("organizations.id"))

    # Store the entire pattern object as JSON for flexibility,
    # but we could extract fields if needed for querying.
    data = Column(JSON)

    version = Column(Integer, default=1)
    last_modified_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    last_modified_at = Column(DateTime, default=datetime.utcnow)

    organization = relationship("Organization", back_populates="patterns")


class Metric(Base):
    __tablename__ = "metrics"

    id = Column(String, primary_key=True)  # ID provided by caller or generated
    type = Column(String, index=True)
    data = Column(JSON)
    organization_id = Column(Integer, ForeignKey("organizations.id"), nullable=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
