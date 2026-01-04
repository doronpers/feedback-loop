"""
Bad Patterns Example - DO NOT USE
This module demonstrates antipatterns that should be avoided in production code.
"""

import json
import numpy as np


def process_data_bad(data_array):
    """Process data without proper NumPy type conversion."""
    # BAD: NumPy types are not JSON serializable
    result = {
        "mean": np.mean(data_array),
        "std": np.std(data_array),
        "max": np.max(data_array)
    }
    # This will fail with: TypeError: Object of type float64 is not JSON serializable
    return json.dumps(result)


def get_first_item_bad(items):
    """Get first item without bounds checking."""
    # BAD: No bounds checking - will raise IndexError if list is empty
    return items[0]


def parse_config_bad(config_str):
    """Parse configuration without specific exception handling."""
    try:
        # BAD: Bare except catches everything, including KeyboardInterrupt
        config = json.loads(config_str)
        return config["database"]["host"]
    except:
        print("Error parsing config")
        return None


def debug_processing_bad(data):
    """Debug processing using print statements."""
    # BAD: Using print() for debugging instead of proper logging
    print(f"Processing data: {data}")
    print(f"Data type: {type(data)}")
    
    result = len(data) if hasattr(data, "__len__") else 0
    print(f"Result: {result}")
    return result


def categorize_by_name_bad(item_name):
    """Categorize items by string matching."""
    # BAD: Using string matching instead of metadata-based categorization
    if "urgent" in item_name.lower():
        return "high_priority"
    elif "important" in item_name.lower():
        return "medium_priority"
    elif "low" in item_name.lower():
        return "low_priority"
    else:
        return "unknown"


class DataProcessor:
    """Example class with bad patterns."""
    
    def __init__(self, config):
        # BAD: Multiple antipatterns
        try:
            self.host = config["host"]
            self.port = config["port"]
        except:
            print("Config error")
            self.host = "localhost"
            self.port = 5432
    
    def process(self, items):
        # BAD: No bounds checking
        first = items[0]
        print(f"Processing first item: {first}")
        
        # BAD: NumPy type not converted
        metrics = {
            "count": np.int64(len(items)),
            "first_value": first
        }
        return json.dumps(metrics)
