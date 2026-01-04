# AI Development Patterns & Feedback Loop

This document describes reusable patterns for AI-assisted development and demonstrates a feedback loop for continuous improvement.

## 🎯 Workflow Philosophy

**Core principle:** AI as a collaborative partner, not just a code generator.

```
┌─────────────────────────────────────────────────────────────────┐
│                    MY DEVELOPMENT LOOP                          │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│   1.  PLAN ──► 2. BUILD ──► 3. REVIEW ──► 4. ITERATE            │
│      ▲           │            │              │                  │
│      │           ▼            ▼              │                  │
│      │       [AI Agent]  [AI Review]         │                  │
│      │           │            │              │                  │
│      └───────────┴────────────┴──────────────┘                  │
│                                                                 │
│   Key:  Humans guide, AI assists, both verify                   │
└─────────────────────────────────────────────────────────────────┘
```

## 🔧 Tech Stack Context

- **Backend**: Python 3.x, FastAPI, numpy, audio processing
- **Frontend**: Vite, React/TypeScript
- **Infrastructure**: Docker, nginx, SSL/TLS
- **Deployment**: Render.com / cloud platforms

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

### 6. Proper Temp File Handling

AI often uses `None` for file descriptors or forgets proper cleanup. This pattern ensures safe temp file handling.

#### ❌ Bad Pattern
```python
import tempfile

def write_temp_file_bad(data):
    # BAD: Using deprecated mktemp (insecure)
    path = tempfile.mktemp()
    
    # BAD: No error handling, no cleanup on failure
    with open(path, 'wb') as f:
        f.write(data)
    
    # BAD: File is not cleaned up - left on disk
    return path
```

**Problems:**
- `mktemp` is deprecated and has security issues (race conditions)
- No error handling if write fails
- File is never cleaned up
- File descriptor not properly managed

#### ✅ Good Pattern
```python
import os
import tempfile
import logging

logger = logging.getLogger(__name__)

def write_temp_file_good(data: bytes) -> tuple[str, bool]:
    """Write data to a temporary file with proper cleanup."""
    fd = None
    path = None
    try:
        # GOOD: Use mkstemp which returns both fd and path
        fd, path = tempfile.mkstemp(suffix=".tmp")
        
        # GOOD: Use os.fdopen to convert fd to file object
        with os.fdopen(fd, 'wb') as f:
            f.write(data)
            fd = None  # fd is now managed by the file object
        
        logger.debug(f"Successfully wrote {len(data)} bytes to {path}")
        return path, True
        
    except (IOError, OSError) as e:
        logger.debug(f"Failed to write temp file: {e}")
        # GOOD: Clean up on error
        if fd is not None:
            try:
                os.close(fd)
            except OSError:
                pass
        if path is not None and os.path.exists(path):
            try:
                os.unlink(path)
            except OSError:
                pass
        return "", False

def cleanup_temp_file_good(path: str) -> bool:
    """Clean up a temporary file safely."""
    if not path:
        return True
    try:
        if os.path.exists(path):
            os.unlink(path)
        return True
    except OSError as e:
        logger.debug(f"Failed to cleanup temp file {path}: {e}")
        return False
```

**Benefits:**
- Secure temp file creation with `mkstemp`
- Proper file descriptor management
- Cleanup on both success and failure
- Safe cleanup function for later use
- Specific exception handling

---

### 7. Large File Processing (up to 800MB)

For audio processing workflows with large files, nginx defaults block uploads and memory can be exhausted.

#### ❌ Bad Pattern
```python
def process_large_file_bad(file_path):
    # BAD: Reading entire file into memory at once
    # This will crash for 800MB files
    with open(file_path, 'rb') as f:
        data = f.read()  # Could cause MemoryError
    
    # BAD: No file size validation
    return {"size": len(data)}
```

**Problems:**
- Memory exhaustion for large files
- No size validation before processing
- No chunked reading strategy
- Will crash servers with limited memory

#### ✅ Good Pattern
```python
import os
import logging
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)

def process_large_file_good(
    file_path: str,
    max_size_bytes: int = 800 * 1024 * 1024,  # 800MB default
    chunk_size: int = 1024 * 1024  # 1MB chunks
) -> Optional[Dict[str, Any]]:
    """Process large files with proper memory management."""
    try:
        # GOOD: Check file size before loading
        file_size = os.path.getsize(file_path)
        
        if file_size > max_size_bytes:
            logger.debug(f"File too large: {file_size} > {max_size_bytes}")
            return None
        
        # GOOD: Calculate chunks from file size (efficient)
        # For actual processing, read in chunks to avoid memory exhaustion
        chunks_needed = (file_size + chunk_size - 1) // chunk_size if file_size > 0 else 1
        
        return {
            "file_path": file_path,
            "size_bytes": int(file_size),  # Ensure Python int for JSON
            "size_mb": float(file_size / (1024 * 1024)),
            "chunks_needed": int(chunks_needed)
        }
        
    except FileNotFoundError:
        logger.debug(f"File not found: {file_path}")
        return None
    except (IOError, OSError) as e:
        logger.debug(f"Error processing file: {e}")
        return None
```

**Benefits:**
- Size validation before processing
- Efficient chunk calculation without reading entire file
- Proper error handling for missing files
- JSON-safe numeric types
- Configurable size limits and chunk sizes

**nginx Configuration (Required for Large Uploads):**
```nginx
# Set in nginx.conf or server block
client_max_body_size 800M;
```

**Docker SSL Note:**
```dockerfile
# AI often forgets ca-certificates for HTTPS
RUN apk add --no-cache ca-certificates
```

---

## Multi-Agent Review Pattern

Use multiple AI agents for better code quality:

```
┌──────────────────┐     ┌──────────────────┐
│   Agent 1        │     │   Agent 2        │
│   (Generator)    │────►│   (Reviewer)     │
│   Creates code   │     │   Critiques it   │
└──────────────────┘     └──────────────────┘
         │                        │
         ▼                        ▼
┌─────────────────────────────────────────────┐
│              Human Decision                  │
│   Accept / Modify / Request Alternative     │
└─────────────────────────────────────────────┘
```

### Review Prompt Template
```
Review this code for:
1. Security issues (especially input validation)
2. Error handling gaps
3. Performance concerns for large files (up to 800MB)
4. Testing blind spots

Code:
[paste code]
```

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
All seven patterns have comprehensive test coverage:
- ✅ NumPy type conversion: 5 tests
- ✅ Bounds checking: 4 tests
- ✅ Specific exceptions: 4 tests
- ✅ Logger usage: 3 tests
- ✅ Metadata categorization: 6 tests
- ✅ Temp file handling: 4 tests
- ✅ Large file processing: 4 tests
- ✅ Integration tests: 5 tests

**Total: 35 tests covering all critical paths**

### Good Results
✅ **Type Safety**: No runtime JSON serialization errors  
✅ **Robustness**: Graceful handling of empty lists  
✅ **Debuggability**: Specific exception messages aid troubleshooting  
✅ **Observability**: Structured logging enables monitoring  
✅ **Maintainability**: Metadata-based logic is easy to extend  
✅ **File Safety**: Proper temp file handling with cleanup  
✅ **Memory Safety**: Large files processed in chunks  

### Bad Results (Before Improvements)
❌ **Type Errors**: JSON serialization crashes with NumPy types  
❌ **Index Errors**: Empty list access crashes services  
❌ **Silent Failures**: Bare except hides real problems  
❌ **Poor Logging**: Print statements not captured in production  
❌ **Fragile Logic**: String matching causes false categorizations  
❌ **File Leaks**: Temp files left on disk without cleanup  
❌ **Memory Exhaustion**: Large files loaded entirely into memory  

---

## 📊 Workflow Metrics I Track

| Metric | What It Tells Me |
|--------|------------------|
| AI suggestions accepted as-is | Am I prompting effectively? |
| Bugs from AI code | What patterns to verify? |
| Time to working feature | Is the workflow efficient? |
| Rework after review | Where are the gaps? |

---

## 🧠 Lessons Learned

### Things AI Consistently Gets Wrong (for me)

1. **numpy → JSON serialization** - Always check
2. **Docker SSL certificates** - Always add ca-certificates
3. **File descriptor handling** - Always use proper fd patterns
4. **nginx defaults** - Always set client_max_body_size

### Things AI Does Well

1. **Boilerplate generation** - FastAPI endpoints, Pydantic models
2. **Test case generation** - Given good examples
3. **Documentation** - Docstrings, README sections
4. **Refactoring** - When given clear patterns to follow

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
| Temp file handling | Working with temporary files | In-memory processing sufficient |
| Large file processing | Files > 10MB or memory constrained | Small files in memory OK |

---

## Prompt Engineering Tips

### Design & Planning Prompt Pattern

Use this pattern for AI-assisted design:

```
I'm building [specific feature].

Context:
- Tech: FastAPI, Docker, nginx
- Constraint: [specific constraint]
- Existing pattern: [reference to codebase]

Help me design the approach. Consider:
1. Edge cases
2. Error handling
3. Testing strategy
```

### AI Output Review Checklist

- [ ] Does it align with my existing patterns?
- [ ] Are the dependencies appropriate?
- [ ] Did it miss any constraints I mentioned?

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

### When AI Gets It Wrong

**Pattern: Clarify and Constrain**
```
That solution doesn't handle [specific case].

Additional context:
- We're using [specific library/pattern]
- The constraint is [specific constraint]
- Here's an example that does work: [code snippet]

Please revise.
```

### When AI Gets It Right

**Document for future sessions:**
```
This pattern works well for [use case]:
[code snippet with comments]

Key insight: [what made this work]
```

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
