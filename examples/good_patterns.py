"""
Good Patterns Example - USE THESE
This module demonstrates best practices for robust, maintainable code.
"""

import json
import logging
from typing import Any, Dict, List, Optional
import numpy as np

# Configure logging
logger = logging.getLogger(__name__)


def convert_numpy_types(obj: Any) -> Any:
    """Convert NumPy types to Python native types for JSON serialization.
    
    Args:
        obj: Object potentially containing NumPy types
        
    Returns:
        Object with NumPy types converted to native Python types
    """
    if isinstance(obj, np.integer):
        return int(obj)
    elif isinstance(obj, np.floating):
        return float(obj)
    elif isinstance(obj, np.ndarray):
        return obj.tolist()
    elif isinstance(obj, dict):
        return {key: convert_numpy_types(value) for key, value in obj.items()}
    elif isinstance(obj, list):
        return [convert_numpy_types(item) for item in obj]
    return obj


def process_data_good(data_array: np.ndarray) -> str:
    """Process data with proper NumPy type conversion.
    
    Args:
        data_array: NumPy array to process
        
    Returns:
        JSON string with converted types
    """
    # GOOD: Convert NumPy types before JSON serialization
    result = {
        "mean": float(np.mean(data_array)),
        "std": float(np.std(data_array)),
        "max": float(np.max(data_array))
    }
    return json.dumps(result)


def get_first_item_good(items: List[Any]) -> Optional[Any]:
    """Get first item with bounds checking.
    
    Args:
        items: List to get first item from
        
    Returns:
        First item or None if list is empty
    """
    # GOOD: Bounds checking before list access
    if not items:
        logger.debug("List is empty, returning None")
        return None
    return items[0]


def parse_config_good(config_str: str) -> Optional[str]:
    """Parse configuration with specific exception handling.
    
    Args:
        config_str: JSON configuration string
        
    Returns:
        Database host or None on error
    """
    try:
        config = json.loads(config_str)
        return config["database"]["host"]
    except json.JSONDecodeError as e:
        # GOOD: Specific exception for JSON parsing errors
        logger.debug(f"Invalid JSON format: {e}")
        return None
    except KeyError as e:
        # GOOD: Specific exception for missing keys
        logger.debug(f"Missing configuration key: {e}")
        return None
    except TypeError as e:
        # GOOD: Specific exception for type errors
        logger.debug(f"Type error in configuration: {e}")
        return None


def debug_processing_good(data: Any) -> int:
    """Debug processing using proper logging.
    
    Args:
        data: Data to process
        
    Returns:
        Length of data or 0 if not applicable
    """
    # GOOD: Using logger.debug() instead of print()
    logger.debug(f"Processing data: {data}")
    logger.debug(f"Data type: {type(data)}")
    
    result = len(data) if hasattr(data, "__len__") else 0
    logger.debug(f"Result: {result}")
    return result


def categorize_by_metadata_good(item: Dict[str, Any]) -> str:
    """Categorize items by metadata instead of string matching.
    
    Args:
        item: Item dictionary with metadata
        
    Returns:
        Category string
    """
    # GOOD: Using metadata-based categorization
    priority = item.get("priority")
    if priority is not None:
        if priority >= 9:
            return "high_priority"
        elif priority >= 5:
            return "medium_priority"
        else:
            return "low_priority"
    
    # Fallback to category metadata if priority not set
    return item.get("category", "unknown")


class DataProcessor:
    """Example class with good patterns."""
    
    def __init__(self, config: Dict[str, Any]):
        """Initialize processor with configuration.
        
        Args:
            config: Configuration dictionary
        """
        # GOOD: Specific exception handling with logging
        try:
            self.host = config.get("host", "localhost")
            self.port = config.get("port", 5432)
            
            # Validate that we got the expected keys if config is a dict
            if not isinstance(config, dict):
                raise TypeError("Configuration must be a dictionary")
                
            # Log if defaults were used
            if "host" not in config:
                logger.debug("Missing 'host' configuration key, using default: localhost")
            if "port" not in config:
                logger.debug("Missing 'port' configuration key, using default: 5432")
                
        except (AttributeError, TypeError) as e:
            logger.debug(f"Invalid configuration type: {e}")
            self.host = "localhost"
            self.port = 5432
    
    def process(self, items: List[Any]) -> Optional[str]:
        """Process items with proper validation.
        
        Args:
            items: List of items to process
            
        Returns:
            JSON string or None on error
        """
        # GOOD: Bounds checking before list access
        if not items:
            logger.debug("Empty items list provided")
            return None
        
        first = items[0]
        logger.debug(f"Processing first item: {first}")
        
        # GOOD: NumPy types converted before serialization
        metrics = {
            "count": int(np.int64(len(items))),
            "first_value": first
        }
        
        return json.dumps(metrics)
