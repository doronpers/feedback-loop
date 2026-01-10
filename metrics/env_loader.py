"""
Environment variable loader utility.

Provides centralized .env file loading for all feedback-loop entry points.
"""

import logging
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)


def load_env_file(project_root: Optional[Path] = None) -> None:
    """Load .env file from project root if it exists.

    This function safely loads environment variables from a .env file
    without overriding existing environment variables. It gracefully
    handles the case where python-dotenv is not installed.

    Args:
        project_root: Path to project root (defaults to parent of metrics/ directory)
    """
    if project_root is None:
        # Default to parent of metrics/ directory
        project_root = Path(__file__).parent.parent

    try:
        from dotenv import load_dotenv

        env_file = project_root / ".env"
        if env_file.exists():
            # load_dotenv doesn't override existing env vars by default
            load_dotenv(env_file, override=False)
            logger.debug(f"Loaded environment variables from {env_file}")
    except ImportError:
        # python-dotenv not installed, skip silently
        pass
    except Exception as e:
        # Log but don't fail if .env loading has issues
        logger.debug(f"Could not load .env file: {e}")
