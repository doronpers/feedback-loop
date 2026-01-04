"""
Tests for good patterns module.
Validates that all best practices work correctly.
"""

import json
import logging
import numpy as np
import pytest
from examples.good_patterns import (
    convert_numpy_types,
    process_data_good,
    get_first_item_good,
    parse_config_good,
    debug_processing_good,
    categorize_by_metadata_good,
    DataProcessor
)


class TestNumpyTypeConversion:
    """Test NumPy type conversion before JSON serialization."""
    
    def test_convert_numpy_int(self):
        """Test converting NumPy integer to Python int."""
        numpy_int = np.int64(42)
        result = convert_numpy_types(numpy_int)
        assert isinstance(result, int)
        assert result == 42
    
    def test_convert_numpy_float(self):
        """Test converting NumPy float to Python float."""
        numpy_float = np.float64(3.14)
        result = convert_numpy_types(numpy_float)
        assert isinstance(result, float)
        assert result == pytest.approx(3.14)
    
    def test_convert_numpy_array(self):
        """Test converting NumPy array to list."""
        numpy_array = np.array([1, 2, 3, 4, 5])
        result = convert_numpy_types(numpy_array)
        assert isinstance(result, list)
        assert result == [1, 2, 3, 4, 5]
    
    def test_convert_dict_with_numpy(self):
        """Test converting dict containing NumPy types."""
        data = {
            "count": np.int64(10),
            "average": np.float64(5.5),
            "values": np.array([1, 2, 3])
        }
        result = convert_numpy_types(data)
        assert isinstance(result["count"], int)
        assert isinstance(result["average"], float)
        assert isinstance(result["values"], list)
    
    def test_process_data_json_serializable(self):
        """Test that processed data is JSON serializable."""
        data_array = np.array([1.0, 2.0, 3.0, 4.0, 5.0])
        result = process_data_good(data_array)
        
        # Should not raise exception
        parsed = json.loads(result)
        assert "mean" in parsed
        assert "std" in parsed
        assert "max" in parsed
        assert parsed["mean"] == pytest.approx(3.0)


class TestBoundsChecking:
    """Test bounds checking before list access."""
    
    def test_get_first_item_with_items(self):
        """Test getting first item from non-empty list."""
        items = [1, 2, 3, 4, 5]
        result = get_first_item_good(items)
        assert result == 1
    
    def test_get_first_item_empty_list(self):
        """Test getting first item from empty list."""
        items = []
        result = get_first_item_good(items)
        assert result is None
    
    def test_get_first_item_none(self):
        """Test handling None input."""
        result = get_first_item_good(None)
        assert result is None
    
    def test_get_first_item_with_string(self):
        """Test getting first item from string list."""
        items = ["first", "second", "third"]
        result = get_first_item_good(items)
        assert result == "first"


class TestSpecificExceptions:
    """Test specific exception handling instead of bare except."""
    
    def test_parse_config_valid(self):
        """Test parsing valid configuration."""
        config_str = '{"database": {"host": "localhost"}}'
        result = parse_config_good(config_str)
        assert result == "localhost"
    
    def test_parse_config_invalid_json(self):
        """Test handling invalid JSON."""
        config_str = '{invalid json}'
        result = parse_config_good(config_str)
        assert result is None
    
    def test_parse_config_missing_key(self):
        """Test handling missing configuration key."""
        config_str = '{"other": "value"}'
        result = parse_config_good(config_str)
        assert result is None
    
    def test_parse_config_wrong_type(self):
        """Test handling wrong type in configuration."""
        config_str = '{"database": "not_a_dict"}'
        result = parse_config_good(config_str)
        assert result is None


class TestLoggerUsage:
    """Test logger.debug() usage instead of print()."""
    
    def test_debug_processing_with_list(self, caplog):
        """Test debug processing with list input."""
        with caplog.at_level(logging.DEBUG):
            result = debug_processing_good([1, 2, 3, 4, 5])
        
        assert result == 5
        # Verify logging was used (not print)
        assert len(caplog.records) > 0
        assert "Processing data" in caplog.text
    
    def test_debug_processing_with_string(self, caplog):
        """Test debug processing with string input."""
        with caplog.at_level(logging.DEBUG):
            result = debug_processing_good("hello")
        
        assert result == 5
        assert "Data type" in caplog.text
    
    def test_debug_processing_without_length(self, caplog):
        """Test debug processing with object without length."""
        with caplog.at_level(logging.DEBUG):
            result = debug_processing_good(42)
        
        assert result == 0
        assert "Result: 0" in caplog.text


class TestMetadataBasedCategorization:
    """Test metadata-based categorization over string matching."""
    
    def test_categorize_high_priority(self):
        """Test categorizing high priority item."""
        item = {"name": "Task 1", "priority": 10}
        result = categorize_by_metadata_good(item)
        assert result == "high_priority"
    
    def test_categorize_medium_priority(self):
        """Test categorizing medium priority item."""
        item = {"name": "Task 2", "priority": 5}
        result = categorize_by_metadata_good(item)
        assert result == "medium_priority"
    
    def test_categorize_low_priority(self):
        """Test categorizing low priority item."""
        item = {"name": "Task 3", "priority": 2}
        result = categorize_by_metadata_good(item)
        assert result == "low_priority"
    
    def test_categorize_by_category_fallback(self):
        """Test fallback to category metadata."""
        item = {"name": "Task 4", "category": "maintenance"}
        result = categorize_by_metadata_good(item)
        assert result == "maintenance"
    
    def test_categorize_unknown(self):
        """Test categorizing item without metadata."""
        item = {"name": "Task 5"}
        result = categorize_by_metadata_good(item)
        assert result == "unknown"
    
    def test_categorize_name_doesnt_affect_result(self):
        """Test that item name doesn't affect categorization."""
        # Even with "urgent" in name, priority metadata takes precedence
        item = {"name": "urgent task", "priority": 1}
        result = categorize_by_metadata_good(item)
        assert result == "low_priority"


class TestDataProcessor:
    """Test DataProcessor class with all patterns."""
    
    def test_init_with_valid_config(self):
        """Test initialization with valid configuration."""
        config = {"host": "example.com", "port": 8080}
        processor = DataProcessor(config)
        assert processor.host == "example.com"
        assert processor.port == 8080
    
    def test_init_with_missing_key(self, caplog):
        """Test initialization with missing configuration key."""
        with caplog.at_level(logging.DEBUG):
            config = {"host": "example.com"}
            processor = DataProcessor(config)
        
        assert processor.host == "example.com"
        assert processor.port == 5432  # Default value
        assert "Missing 'port' configuration key" in caplog.text
    
    def test_init_with_invalid_type(self, caplog):
        """Test initialization with invalid configuration type."""
        with caplog.at_level(logging.DEBUG):
            config = "not_a_dict"
            processor = DataProcessor(config)
        
        assert processor.host == "localhost"
        assert processor.port == 5432
        assert "Invalid configuration type" in caplog.text
    
    def test_process_with_items(self):
        """Test processing with items."""
        config = {"host": "localhost", "port": 5432}
        processor = DataProcessor(config)
        
        items = ["item1", "item2", "item3"]
        result = processor.process(items)
        
        assert result is not None
        parsed = json.loads(result)
        assert parsed["count"] == 3
        assert parsed["first_value"] == "item1"
    
    def test_process_with_empty_list(self, caplog):
        """Test processing with empty list."""
        config = {"host": "localhost", "port": 5432}
        processor = DataProcessor(config)
        
        with caplog.at_level(logging.DEBUG):
            result = processor.process([])
        
        assert result is None
        assert "Empty items list" in caplog.text
