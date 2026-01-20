import os

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Use SQLite by default for development if no DATABASE_URL is set
# In production, this should be set to a PostgreSQL URL
SQLALCHEMY_DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./feedback_loop.db")

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    # distinct connect_args for sqlite vs others
    connect_args={"check_same_thread": False}
    if "sqlite" in SQLALCHEMY_DATABASE_URL
    else {},
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
