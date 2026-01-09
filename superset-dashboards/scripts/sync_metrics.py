#!/usr/bin/env python
"""
Automated sync script for feedback-loop metrics to database.

This script can be run periodically (e.g., via cron) to automatically
export metrics to the database for Superset visualization.

Usage:
    python sync_metrics.py --config sync_config.json
    
    Or with environment variables:
    export METRICS_DB_URI="postgresql://user:pass@localhost/db"
    python sync_metrics.py
"""

import argparse
import json
import logging
import os
import sys
from datetime import datetime
from pathlib import Path

# Add database directory to path
database_dir = Path(__file__).parent.parent / 'database'
sys.path.insert(0, str(database_dir))

from models import Base

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s: %(message)s'
)
logger = logging.getLogger(__name__)


class MetricsSync:
    """Automated metrics synchronization."""
    
    def __init__(self, config: dict):
        """Initialize sync with configuration.
        
        Args:
            config: Configuration dictionary with db_uri, metrics_path, etc.
        """
        self.config = config
        self.db_uri = config.get('db_uri') or os.getenv('METRICS_DB_URI')
        self.metrics_path = Path(config.get('metrics_path', 'metrics_data.json'))
        self.log_path = Path(config.get('log_path', 'sync_log.json'))
        
        if not self.db_uri:
            raise ValueError("Database URI not provided (set via config or METRICS_DB_URI env var)")
    
    def check_for_updates(self) -> bool:
        """Check if metrics file has been updated since last sync.
        
        Returns:
            True if metrics file has new data
        """
        if not self.metrics_path.exists():
            logger.warning(f"Metrics file not found: {self.metrics_path}")
            return False
        
        # Get last sync time
        last_sync = self._get_last_sync_time()
        
        # Get metrics file modification time
        metrics_mtime = datetime.fromtimestamp(self.metrics_path.stat().st_mtime)
        
        if last_sync is None or metrics_mtime > last_sync:
            logger.info(f"Metrics file updated: {metrics_mtime}")
            return True
        
        logger.info("No new metrics to sync")
        return False
    
    def sync(self) -> bool:
        """Perform sync operation.
        
        Returns:
            True if sync was successful
        """
        try:
            # Check for updates
            if not self.check_for_updates():
                return True
            
            # Import export module
            export_script = Path(__file__).parent / 'export_to_db.py'
            
            # Run export
            logger.info("Starting metrics export...")
            import subprocess
            
            result = subprocess.run(
                [
                    sys.executable,
                    str(export_script),
                    '--input', str(self.metrics_path),
                    '--db-uri', self.db_uri
                ],
                capture_output=True,
                text=True
            )
            
            if result.returncode != 0:
                logger.error(f"Export failed: {result.stderr}")
                return False
            
            logger.info("Export completed successfully")
            logger.info(result.stdout)
            
            # Update last sync time
            self._update_last_sync_time()
            
            return True
            
        except Exception as e:
            logger.error(f"Sync failed: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def _get_last_sync_time(self) -> datetime:
        """Get timestamp of last successful sync.
        
        Returns:
            Datetime of last sync or None
        """
        if not self.log_path.exists():
            return None
        
        try:
            with open(self.log_path, 'r') as f:
                log_data = json.load(f)
                last_sync_str = log_data.get('last_sync')
                if last_sync_str:
                    return datetime.fromisoformat(last_sync_str)
        except (json.JSONDecodeError, KeyError, ValueError):
            pass
        
        return None
    
    def _update_last_sync_time(self):
        """Update last sync timestamp in log file."""
        # Mask sensitive database credentials before logging
        if '@' in self.db_uri:
            # Extract only the host/database portion for logging
            uri_parts = self.db_uri.split('@')
            masked_uri = '@'.join(['***', uri_parts[-1]])
        else:
            masked_uri = self.db_uri
        
        log_data = {
            'last_sync': datetime.now().isoformat(),
            'metrics_path': str(self.metrics_path),
            'db_uri': masked_uri
        }
        
        with open(self.log_path, 'w') as f:
            json.dump(log_data, f, indent=2)


def load_config(config_path: str) -> dict:
    """Load configuration from JSON file.
    
    Args:
        config_path: Path to configuration file
        
    Returns:
        Configuration dictionary
    """
    if not Path(config_path).exists():
        logger.warning(f"Config file not found: {config_path}")
        return {}
    
    with open(config_path, 'r') as f:
        return json.load(f)


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description='Automated sync of feedback-loop metrics to database'
    )
    parser.add_argument(
        '--config',
        default='sync_config.json',
        help='Configuration file path (default: sync_config.json)'
    )
    parser.add_argument(
        '--force',
        action='store_true',
        help='Force sync even if no updates detected'
    )
    
    args = parser.parse_args()
    
    try:
        # Load configuration
        config = load_config(args.config)
        
        # Override with environment variables if present
        if os.getenv('METRICS_DB_URI'):
            config['db_uri'] = os.getenv('METRICS_DB_URI')
        if os.getenv('METRICS_PATH'):
            config['metrics_path'] = os.getenv('METRICS_PATH')
        
        # Initialize sync
        sync = MetricsSync(config)
        
        # Perform sync
        if args.force:
            logger.info("Force sync requested")
            # Temporarily remove last sync time to force update
            if sync.log_path.exists():
                sync.log_path.unlink()
        
        success = sync.sync()
        
        if success:
            logger.info("✓ Sync completed successfully")
            return 0
        else:
            logger.error("✗ Sync failed")
            return 1
            
    except Exception as e:
        logger.error(f"Sync error: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == '__main__':
    sys.exit(main())
