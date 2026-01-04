#!/usr/bin/env python3
"""
Demonstration script showing good patterns in action.
Run this to see the patterns working correctly.
"""

import json
import logging
import numpy as np
from examples.good_patterns import (
    convert_numpy_types,
    process_data_good,
    get_first_item_good,
    parse_config_good,
    debug_processing_good,
    categorize_by_metadata_good,
    DataProcessor
)

# Configure logging to show debug messages
logging.basicConfig(
    level=logging.DEBUG,
    format='%(levelname)s - %(name)s - %(message)s'
)


def demo_numpy_conversion():
    """Demonstrate NumPy type conversion."""
    print("\n" + "="*60)
    print("1. NumPy Type Conversion Demo")
    print("="*60)
    
    data = np.array([1.5, 2.5, 3.5, 4.5, 5.5])
    result = process_data_good(data)
    print(f"Input: NumPy array {data}")
    print(f"Output: {result}")
    print(f"✅ Successfully serialized to JSON!")
    

def demo_bounds_checking():
    """Demonstrate bounds checking."""
    print("\n" + "="*60)
    print("2. Bounds Checking Demo")
    print("="*60)
    
    # Non-empty list
    items = ["apple", "banana", "cherry"]
    first = get_first_item_good(items)
    print(f"Items: {items}")
    print(f"First item: {first}")
    
    # Empty list
    empty_items = []
    first_empty = get_first_item_good(empty_items)
    print(f"\nEmpty items: {empty_items}")
    print(f"First item: {first_empty}")
    print(f"✅ No crashes on empty list!")


def demo_specific_exceptions():
    """Demonstrate specific exception handling."""
    print("\n" + "="*60)
    print("3. Specific Exception Handling Demo")
    print("="*60)
    
    # Valid config
    valid_config = '{"database": {"host": "db.example.com"}}'
    result = parse_config_good(valid_config)
    print(f"Valid config: {valid_config}")
    print(f"Result: {result}")
    
    # Invalid JSON
    invalid_json = '{not valid json}'
    result = parse_config_good(invalid_json)
    print(f"\nInvalid JSON: {invalid_json}")
    print(f"Result: {result}")
    
    # Missing key
    missing_key = '{"other": "value"}'
    result = parse_config_good(missing_key)
    print(f"\nMissing key: {missing_key}")
    print(f"Result: {result}")
    print(f"✅ Specific exceptions handled gracefully!")


def demo_logging():
    """Demonstrate logger.debug() usage."""
    print("\n" + "="*60)
    print("4. Structured Logging Demo")
    print("="*60)
    
    print("Processing data with structured logging...")
    data = [10, 20, 30, 40, 50]
    result = debug_processing_good(data)
    print(f"Result: {result}")
    print(f"✅ Debug information logged (check logs above)!")


def demo_metadata_categorization():
    """Demonstrate metadata-based categorization."""
    print("\n" + "="*60)
    print("5. Metadata-Based Categorization Demo")
    print("="*60)
    
    items = [
        {"name": "Critical bug fix", "priority": 10},
        {"name": "Feature request", "priority": 6},
        {"name": "Documentation update", "priority": 2},
        {"name": "Maintenance task", "category": "maintenance"},
        {"name": "Unknown item"}
    ]
    
    for item in items:
        category = categorize_by_metadata_good(item)
        print(f"Item: {item['name']:<25} → Category: {category}")
    
    print(f"✅ Categorization based on metadata, not string matching!")


def demo_data_processor():
    """Demonstrate DataProcessor class with all patterns."""
    print("\n" + "="*60)
    print("6. Complete DataProcessor Demo")
    print("="*60)
    
    # Valid config
    config = {"host": "api.example.com", "port": 8080}
    processor = DataProcessor(config)
    print(f"Config: {config}")
    print(f"Processor initialized: host={processor.host}, port={processor.port}")
    
    # Process items
    items = ["task1", "task2", "task3"]
    result = processor.process(items)
    print(f"\nProcessing items: {items}")
    print(f"Result: {result}")
    
    # Process empty list
    result_empty = processor.process([])
    print(f"\nProcessing empty list")
    print(f"Result: {result_empty}")
    print(f"✅ All patterns working together!")


def main():
    """Run all demonstrations."""
    print("\n" + "="*60)
    print("AI Development Patterns - Live Demo")
    print("="*60)
    
    demo_numpy_conversion()
    demo_bounds_checking()
    demo_specific_exceptions()
    demo_logging()
    demo_metadata_categorization()
    demo_data_processor()
    
    print("\n" + "="*60)
    print("Demo Complete!")
    print("="*60)
    print("\nAll patterns demonstrated successfully! ✅")
    print("See AI_PATTERNS.md for detailed documentation.")


if __name__ == "__main__":
    main()
