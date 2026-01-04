# AI Development Patterns & Feedback Loop

This document describes reusable patterns for AI-assisted development and demonstrates a feedback loop for continuous improvement.

## The Feedback Loop Process

```
PLAN → BUILD → REVIEW → ITERATE
                  ↓
           Retrospective
                  ↓
        Update AI_PATTERNS.md
                  ↓
       Better prompts next time
```

## Core Best Practices

### 1. NumPy Types Converted Before JSON Serialization

#### ❌ Bad Pattern
```python
import json
import numpy as np

def process_data_bad(data_array):
    result = {
        "mean": np.mean(data_array),  # NumPy float64
        "std": np.std(data_array),    # NumPy float64
        "max": np.max(data_array)     # NumPy float64
    }
    # TypeError: Object of type float64 is not JSON serializable
    return json.dumps(result)
```

**Problems:**
- NumPy types (int64, float64, etc.) are not JSON serializable
- Runtime errors when trying to serialize
- Data loss or corruption in API responses

#### ✅ Good Pattern
```python
import json
import numpy as np

def convert_numpy_types(obj):
    """Convert NumPy types to Python native types."""
    if isinstance(obj, np.integer):
        return int(obj)
    elif isinstance(obj, np.floating):
        return float(obj)
    elif isinstance(obj, np.ndarray):
        return obj.tolist()
    return obj

def process_data_good(data_array):
    result = {
        "mean": float(np.mean(data_array)),  # Explicit conversion
        "std": float(np.std(data_array)),
        "max": float(np.max(data_array))
    }
    return json.dumps(result)  # Works correctly
```

**Benefits:**
- No runtime serialization errors
- Portable JSON that works across systems
- Clear data type handling

---

### 2. Bounds Checking Before List Access

#### ❌ Bad Pattern
```python
def get_first_item_bad(items):
    # No bounds checking - crashes on empty list
    return items[0]  # IndexError if items is empty
```

**Problems:**
- IndexError on empty lists
- No graceful error handling
- Service crashes instead of handling edge cases

#### ✅ Good Pattern
```python
import logging

logger = logging.getLogger(__name__)

def get_first_item_good(items):
    """Get first item with bounds checking."""
    if not items:
        logger.debug("List is empty, returning None")
        return None
    return items[0]
```

**Benefits:**
- No crashes on empty lists
- Graceful degradation
- Debugging information via logging
- Clear return value contracts

---

### 3. Specific Exceptions, Not Bare Except

#### ❌ Bad Pattern
```python
def parse_config_bad(config_str):
    try:
        config = json.loads(config_str)
        return config["database"]["host"]
    except:  # Catches EVERYTHING including KeyboardInterrupt
        print("Error parsing config")
        return None
```

**Problems:**
- Catches system exceptions (KeyboardInterrupt, SystemExit)
- Hides bugs and makes debugging harder
- Can't differentiate between error types
- Silent failures

#### ✅ Good Pattern
```python
import json
import logging

logger = logging.getLogger(__name__)

def parse_config_good(config_str):
    """Parse configuration with specific exception handling."""
    try:
        config = json.loads(config_str)
        return config["database"]["host"]
    except json.JSONDecodeError as e:
        logger.debug(f"Invalid JSON format: {e}")
        return None
    except KeyError as e:
        logger.debug(f"Missing configuration key: {e}")
        return None
    except TypeError as e:
        logger.debug(f"Type error in configuration: {e}")
        return None
```

**Benefits:**
- Only catches expected exceptions
- Allows system interrupts to work
- Better error messages for debugging
- Different handling per error type
- Proper logging context

---

### 4. Logger.debug() Instead of Print()

#### ❌ Bad Pattern
```python
def debug_processing_bad(data):
    print(f"Processing data: {data}")  # Goes to stdout
    print(f"Data type: {type(data)}")
    
    result = len(data) if hasattr(data, "__len__") else 0
    print(f"Result: {result}")
    return result
```

**Problems:**
- Output mixed with application output
- No log levels or filtering
- Can't disable in production
- Not captured by log aggregation systems
- No timestamps or context

#### ✅ Good Pattern
```python
import logging

logger = logging.getLogger(__name__)

def debug_processing_good(data):
    """Debug processing using proper logging."""
    logger.debug(f"Processing data: {data}")
    logger.debug(f"Data type: {type(data)}")
    
    result = len(data) if hasattr(data, "__len__") else 0
    logger.debug(f"Result: {result}")
    return result
```

**Benefits:**
- Configurable log levels (DEBUG, INFO, WARNING, ERROR)
- Can be disabled in production
- Captured by log aggregation (CloudWatch, Splunk, etc.)
- Includes timestamps and module context
- Searchable and filterable

---

### 5. Metadata-Based Categorization Over String Matching

#### ❌ Bad Pattern
```python
def categorize_by_name_bad(item_name):
    """Categorize by searching strings in name."""
    if "urgent" in item_name.lower():
        return "high_priority"
    elif "important" in item_name.lower():
        return "medium_priority"
    elif "low" in item_name.lower():
        return "low_priority"
    else:
        return "unknown"
```

**Problems:**
- Fragile string matching
- False positives ("I have low confidence" → "low_priority")
- Language-dependent
- Hard to maintain and extend
- No clear data contract

#### ✅ Good Pattern
```python
import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)

def categorize_by_metadata_good(item: Dict[str, Any]) -> str:
    """Categorize items by metadata instead of string matching."""
    priority = item.get("priority")
    if priority is not None:
        if priority >= 9:
            return "high_priority"
        elif priority >= 5:
            return "medium_priority"
        else:
            return "low_priority"
    
    # Fallback to category metadata
    return item.get("category", "unknown")
```

**Benefits:**
- Explicit metadata contracts
- No false positives from string matching
- Language-agnostic
- Easy to extend with new categories
- Clear business logic
- Type-safe with proper validation

---

## Iteration Loop Example

### PLAN Phase
1. Identify the pattern or problem
2. Research best practices
3. Define success criteria
4. Write test cases first (TDD)

### BUILD Phase
1. Implement the minimal solution
2. Focus on one pattern at a time
3. Add type hints for clarity
4. Write clear docstrings

### REVIEW Phase
1. Run automated tests
2. Check code coverage
3. Review against style guide
4. Look for edge cases
5. Verify logging and error handling

### ITERATE Phase
1. Address review feedback
2. Refine implementation
3. Add missing test cases
4. Improve documentation
5. Repeat BUILD → REVIEW until satisfied

### Retrospective Phase
1. What worked well?
2. What could be improved?
3. What patterns emerged?
4. What should be documented?
5. Update this document with learnings

---

## Results Documentation

### Test Coverage
All five patterns have comprehensive test coverage:
- ✅ NumPy type conversion: 5 tests
- ✅ Bounds checking: 4 tests
- ✅ Specific exceptions: 4 tests
- ✅ Logger usage: 3 tests
- ✅ Metadata categorization: 6 tests
- ✅ Integration tests: 5 tests

**Total: 27 tests covering all critical paths**

### Good Results
✅ **Type Safety**: No runtime JSON serialization errors  
✅ **Robustness**: Graceful handling of empty lists  
✅ **Debuggability**: Specific exception messages aid troubleshooting  
✅ **Observability**: Structured logging enables monitoring  
✅ **Maintainability**: Metadata-based logic is easy to extend  

### Bad Results (Before Improvements)
❌ **Type Errors**: JSON serialization crashes with NumPy types  
❌ **Index Errors**: Empty list access crashes services  
❌ **Silent Failures**: Bare except hides real problems  
❌ **Poor Logging**: Print statements not captured in production  
❌ **Fragile Logic**: String matching causes false categorizations  

---

## Quick Reference

### When to Use Each Pattern

| Pattern | Use When | Don't Use When |
|---------|----------|----------------|
| NumPy conversion | Using NumPy with JSON APIs | Pure Python types only |
| Bounds checking | Accessing list/array elements | Length already verified |
| Specific exceptions | Handling expected errors | Re-raising all exceptions |
| Logger.debug() | Adding debug information | User-facing messages |
| Metadata categorization | Complex business logic | Simple true/false checks |

---

## Prompt Engineering Tips

### For Better AI Assistance
1. **Be Specific**: "Convert NumPy float64 to Python float before JSON" vs "Fix JSON"
2. **Provide Context**: Include error messages and stack traces
3. **Show Examples**: Demonstrate input/output expectations
4. **Request Tests**: Ask for test cases alongside implementation
5. **Iterate**: Refine based on results, don't expect perfection first try

### Example Prompts

**Bad Prompt:**
> "Fix the JSON problem"

**Good Prompt:**
> "I'm getting 'TypeError: Object of type float64 is not JSON serializable' when serializing NumPy arrays. Please show how to convert NumPy types to Python native types before JSON serialization, with tests."

**Bad Prompt:**
> "Add error handling"

**Good Prompt:**
> "Replace bare `except:` clauses with specific exception handling for JSON parsing errors (JSONDecodeError), missing keys (KeyError), and type errors (TypeError). Use logger.debug() to log each case with context."

---

## Contributing to This Document

When you discover new patterns or improvements:

1. Follow the feedback loop: PLAN → BUILD → REVIEW → ITERATE
2. Document both bad and good examples
3. Explain the problems and benefits
4. Add test cases demonstrating the pattern
5. Update this document in the Retrospective phase
6. Include concrete before/after results

---

## License

This document and examples are part of the feedback-loop repository.
See LICENSE for details.
