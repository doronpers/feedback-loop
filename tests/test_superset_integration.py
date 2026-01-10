"""
Test suite for Superset integration functionality.

Tests the database export functionality and model integrity.
"""

import json
import os
import sys
import tempfile
from pathlib import Path

import pytest

# Add superset-dashboards to path
superset_dir = Path(__file__).parent.parent / 'superset-dashboards'
sys.path.insert(0, str(superset_dir / 'database'))

from models import (
    Base,
    MetricsBug,
    MetricsTestFailure,
    MetricsCodeReview,
    MetricsPerformance,
    MetricsDeployment,
    MetricsCodeGeneration,
    get_all_models
)


class TestSupersetModels:
    """Test SQLAlchemy models for Superset integration."""
    
    def test_all_models_defined(self):
        """Test that all expected models are defined."""
        models = get_all_models()
        assert len(models) >= 8, "Expected at least 8 models"
        
        model_names = [m.__name__ for m in models]
        expected_models = [
            'MetricsBug',
            'MetricsTestFailure',
            'MetricsCodeReview',
            'MetricsPerformance',
            'MetricsDeployment',
            'MetricsCodeGeneration'
        ]
        
        for expected in expected_models:
            assert expected in model_names, f"Model {expected} not found"
    
    def test_metrics_bug_model(self):
        """Test MetricsBug model structure."""
        bug = MetricsBug(
            pattern='test_pattern',
            error='Test error',
            code='test code',
            file_path='test.py',
            line=10,
            count=1
        )
        
        assert bug.pattern == 'test_pattern'
        assert bug.error == 'Test error'
        assert bug.code == 'test code'
        assert bug.file_path == 'test.py'
        assert bug.line == 10
        assert bug.count == 1
    
    def test_metrics_code_generation_model(self):
        """Test MetricsCodeGeneration model structure."""
        gen = MetricsCodeGeneration(
            prompt='Test prompt',
            patterns_applied=['pattern1', 'pattern2'],
            confidence=0.95,
            success=True,
            code_length=100
        )
        
        assert gen.prompt == 'Test prompt'
        assert gen.patterns_applied == ['pattern1', 'pattern2']
        assert gen.confidence == 0.95
        assert gen.success is True
        assert gen.code_length == 100


class TestDatabaseExport:
    """Test database export functionality."""
    
    def test_export_script_exists(self):
        """Test that export script exists and is executable."""
        export_script = Path(__file__).parent.parent / 'superset-dashboards' / 'scripts' / 'export_to_db.py'
        assert export_script.exists(), "Export script not found"
        # Check if file is executable (on Unix systems)
        if sys.platform != 'win32':
            assert os.access(export_script, os.X_OK), "Export script not executable"
    
    def test_sync_script_exists(self):
        """Test that sync script exists."""
        sync_script = Path(__file__).parent.parent / 'superset-dashboards' / 'scripts' / 'sync_metrics.py'
        assert sync_script.exists(), "Sync script not found"
    
    def test_dashboard_configs_exist(self):
        """Test that dashboard configuration files exist."""
        dashboards_dir = Path(__file__).parent.parent / 'superset-dashboards' / 'dashboards'
        
        expected_dashboards = [
            'code_quality_dashboard.json',
            'pattern_analysis_dashboard.json',
            'development_trends_dashboard.json'
        ]
        
        for dashboard_file in expected_dashboards:
            dashboard_path = dashboards_dir / dashboard_file
            assert dashboard_path.exists(), f"Dashboard {dashboard_file} not found"
            
            # Validate JSON structure
            with open(dashboard_path, 'r') as f:
                dashboard_data = json.load(f)
                assert 'dashboard_title' in dashboard_data
                assert 'slices' in dashboard_data
                assert len(dashboard_data['slices']) > 0


class TestIntegrationDocumentation:
    """Test integration documentation exists and is complete."""
    
    def test_superset_integration_doc_exists(self):
        """Test that Superset integration documentation exists."""
        doc_path = Path(__file__).parent.parent / 'Documentation' / 'SUPERSET_INTEGRATION.md'
        assert doc_path.exists(), "SUPERSET_INTEGRATION.md not found"
        
        # Check documentation contains key sections
        with open(doc_path, 'r') as f:
            content = f.read()
            
        assert '# Apache Superset Integration Guide' in content
        assert 'Setup Guide' in content or 'setup guide' in content.lower()
        assert 'Dashboard' in content
        assert 'PostgreSQL' in content
        assert 'SQLite' in content
    
    def test_readme_includes_superset(self):
        """Test that main README mentions Superset integration."""
        readme_path = Path(__file__).parent.parent / 'README.md'
        
        with open(readme_path, 'r') as f:
            content = f.read()
        
        assert 'Superset' in content, "README should mention Superset integration"
    
    def test_connection_examples_doc_exists(self):
        """Test that database connection examples exist."""
        examples_path = Path(__file__).parent.parent / 'superset-dashboards' / 'database' / 'connection_examples.md'
        assert examples_path.exists(), "Connection examples documentation not found"


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
