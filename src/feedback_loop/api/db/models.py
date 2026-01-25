from datetime import datetime
from typing import Dict, List, Optional

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Text,
    JSON,
    Float,
)
from sqlalchemy.orm import relationship

from api.db.base_class import Base


class Organization(Base):
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    users = relationship("User", back_populates="organization")
    patterns = relationship("Pattern", back_populates="organization")
    config = relationship("Config", back_populates="organization", uselist=False)


class User(Base):
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    username = Column(String, unique=True, index=True, nullable=False)
    full_name = Column(String, nullable=True)
    hashed_password = Column(String, nullable=False)
    role = Column(String, default="developer")
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    last_login = Column(DateTime, nullable=True)

    organization_id = Column(Integer, ForeignKey("organization.id"))
    organization = relationship("Organization", back_populates="users")
    sessions = relationship("Session", back_populates="user")


class Session(Base):
    id = Column(Integer, primary_key=True, index=True)
    token = Column(String, unique=True, index=True, nullable=False)
    user_id = Column(Integer, ForeignKey("user.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    expires_at = Column(DateTime, nullable=True)

    user = relationship("User", back_populates="sessions")


class Pattern(Base):
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True, nullable=False)
    description = Column(Text, nullable=True)
    bad_example = Column(Text, nullable=True)
    good_example = Column(Text, nullable=True)
    severity = Column(String, default="medium")
    occurrence_frequency = Column(Integer, default=0)
    effectiveness_score = Column(Float, default=0.5)
    last_occurrence = Column(DateTime, nullable=True)

    version = Column(Integer, default=1)
    last_modified_at = Column(DateTime, default=datetime.utcnow)
    last_modified_by = Column(Integer, ForeignKey("user.id"), nullable=True)

    organization_id = Column(Integer, ForeignKey("organization.id"))
    organization = relationship("Organization", back_populates="patterns")


class Config(Base):
    id = Column(Integer, primary_key=True, index=True)
    settings = Column(JSON, default={})
    enforced_settings = Column(JSON, default=[])

    organization_id = Column(Integer, ForeignKey("organization.id"), unique=True)
    organization = relationship("Organization", back_populates="config")
