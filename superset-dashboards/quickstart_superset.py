#!/usr/bin/env python3
"""
Quick start script for Apache Superset integration.

This script helps users quickly set up Superset dashboard integration
by checking prerequisites, creating sample data, and providing next steps.

Usage:
    python quickstart_superset.py
"""

import json
import os
import subprocess
import sys
from pathlib import Path


def print_header(text):
    """Print a section header."""
    print("\n" + "=" * 70)
    print(f"  {text}")
    print("=" * 70)


def check_prerequisites():
    """Check if prerequisites are installed."""
    print_header("Checking Prerequisites")
    
    checks_passed = True
    
    # Check Python version
    python_version = sys.version_info
    if python_version >= (3, 8):
        print(f"✓ Python {python_version.major}.{python_version.minor} detected")
    else:
        print(f"✗ Python 3.8+ required (found {python_version.major}.{python_version.minor})")
        checks_passed = False
    
    # Check SQLAlchemy
    try:
        import sqlalchemy
        print(f"✓ SQLAlchemy {sqlalchemy.__version__} installed")
    except ImportError:
        print("✗ SQLAlchemy not installed")
        print("  Install with: pip install sqlalchemy")
        checks_passed = False
    
    # Check feedback-loop
    try:
        from metrics.collector import MetricsCollector
        print("✓ feedback-loop installed")
    except ImportError:
        print("✗ feedback-loop not installed")
        print("  Install with: pip install -e /path/to/feedback-loop")
        print("  (Replace /path/to/feedback-loop with the actual path)")
        checks_passed = False
    
    return checks_passed


def create_sample_data():
    """Create sample metrics data for testing."""
    print_header("Creating Sample Data")
    
    try:
        from metrics.collector import MetricsCollector
        
        collector = MetricsCollector()
        
        # Add sample metrics
        collector.log_bug(
            pattern='numpy_json_serialization',
            error='TypeError: Object of type float64 is not JSON serializable',
            code='result = {"score": np.mean(data)}',
            file_path='api/endpoints.py',
            line=42
        )
        
        collector.log_code_generation(
            prompt='Create function to process data',
            patterns_applied=['numpy_json_serialization', 'bounds_checking'],
            confidence=0.92,
            success=True,
            code_length=150
        )
        
        # Save to file
        sample_file = 'sample_metrics_data.json'
        with open(sample_file, 'w') as f:
            json.dump(collector.data, f, indent=2)
        
        print(f"✓ Created {sample_file}")
        return sample_file
    except Exception as e:
        print(f"✗ Failed to create sample data: {e}")
        return None


def export_to_database(metrics_file):
    """Export metrics to SQLite database."""
    print_header("Exporting to Database")
    
    try:
        result = subprocess.run(
            [
                sys.executable,
                'superset-dashboards/scripts/export_to_db.py',
                '--input', metrics_file,
                '--format', 'sqlite',
                '--db-path', 'sample_metrics.db'
            ],
            capture_output=True,
            text=True
        )
        
        if result.returncode == 0:
            print("✓ Metrics exported to sample_metrics.db")
            return True
        else:
            print(f"✗ Export failed: {result.stderr}")
            return False
    except Exception as e:
        print(f"✗ Export failed: {e}")
        return False


def print_next_steps():
    """Print next steps for user."""
    print_header("Next Steps")
    
    print("\n1. Install Apache Superset (if not already installed):")
    print("   Using Docker:")
    print("     git clone https://github.com/apache/superset.git")
    print("     cd superset")
    print("     docker-compose -f docker-compose-non-dev.yml up -d")
    print("")
    print("   Or using pip:")
    print("     pip install apache-superset")
    print("     superset db upgrade")
    print("     superset init")
    
    print("\n2. Start Superset:")
    print("   Access at: http://localhost:8088")
    print("   Default credentials: admin/admin")
    
    print("\n3. Configure Database Connection in Superset:")
    print("   a. Go to Data → Databases → + Database")
    print("   b. Select SQLite")
    db_path = Path('sample_metrics.db').absolute()
    print(f"   c. SQLAlchemy URI: sqlite:///{db_path}")
    print("   d. Test connection and save")
    
    print("\n4. Add Datasets:")
    print("   a. Go to Data → Datasets → + Dataset")
    print("   b. Add tables: metrics_bugs, metrics_code_generation, etc.")
    
    print("\n5. Create Dashboards:")
    print("   a. Go to Dashboards → + Dashboard")
    print("   b. Or import pre-configured dashboards from:")
    print("      superset-dashboards/dashboards/")
    
    print("\n6. For production use:")
    print("   - Switch to PostgreSQL database")
    print("   - Set up automated sync with cron or CI/CD")
    print("   - See Documentation/SUPERSET_INTEGRATION.md for details")
    
    print("\n📚 Documentation:")
    print("   - Quick Start: superset-dashboards/README.md")
    print("   - Full Guide: Documentation/SUPERSET_INTEGRATION.md")
    print("   - Examples: superset-dashboards/examples/")
    
    print("\n✨ Sample files created:")
    print("   - sample_metrics_data.json (sample metrics)")
    print("   - sample_metrics.db (SQLite database)")
    print("\n   You can delete these after testing.")


def main():
    """Main entry point."""
    print("\n" + "🎬 " + "=" * 65)
    print("   APACHE SUPERSET INTEGRATION - QUICK START")
    print("=" * 70)
    
    # Check prerequisites
    if not check_prerequisites():
        print("\n❌ Prerequisites check failed")
        print("Please install missing dependencies and try again")
        return 1
    
    # Create sample data
    metrics_file = create_sample_data()
    if not metrics_file:
        print("\n❌ Failed to create sample data")
        return 1
    
    # Export to database
    if not export_to_database(metrics_file):
        print("\n❌ Failed to export to database")
        return 1
    
    # Print next steps
    print_next_steps()
    
    print("\n" + "=" * 70)
    print("✓ Quick start completed successfully!")
    print("=" * 70 + "\n")
    
    return 0


if __name__ == '__main__':
    sys.exit(main())
