# Quick Reference

**One-page reference for common patterns and commands.**

> 💡 **Learn differently?** This is organized linearly. For personalized paths based on YOUR motivations and style, see the [Flexible Learning Paths](FLEXIBLE_LEARNING_PATHS.md).

## The 9 Patterns

### 1. NumPy Type Conversion

```python
# ❌ BAD: Crashes on JSON serialization
result = {"mean": np.mean(data)}

# ✅ GOOD: Convert to Python types first
result = {"mean": float(np.mean(data))}
```

### 2. Bounds Checking

```python
# ❌ BAD: Crashes on empty list
first = items[0]

# ✅ GOOD: Check first
first = items[0] if items else None
```

### 3. Specific Exceptions

```python
# ❌ BAD: Catches everything including Ctrl+C
try:
    data = json.loads(text)
except:
    return None

# ✅ GOOD: Catch specific errors
try:
    data = json.loads(text)
except json.JSONDecodeError as e:
    logger.debug(f"Invalid JSON: {e}")
    return None
```

### 4. Structured Logging

```python
# ❌ BAD: Not captured in production
print(f"Processing {file}")

# ✅ GOOD: Use logger
logger.debug(f"Processing {file}")
```

### 5. Metadata-Based Logic

```python
# ❌ BAD: Fragile string matching
if "urgent" in name.lower():
    priority = "high"

# ✅ GOOD: Use metadata
priority = item.get("priority_level", "normal")
```

### 6. Temp File Handling

```python
# ❌ BAD: No cleanup
path = tempfile.mktemp()
with open(path, 'wb') as f:
    f.write(data)

# ✅ GOOD: Always cleanup
fd, path = tempfile.mkstemp()
try:
    with os.fdopen(fd, 'wb') as f:
        f.write(data)
finally:
    os.unlink(path)
```

### 7. Large File Processing

```python
# ❌ BAD: Loads entire file into memory
with open(path, 'rb') as f:
    data = f.read()  # OOM for large files

# ✅ GOOD: Process in chunks
with open(path, 'rb') as f:
    while chunk := f.read(1024 * 1024):
        process(chunk)
```

### 8. FastAPI Streaming

```python
# ❌ BAD: Loads entire upload into memory
content = await file.read()

# ✅ GOOD: Stream to disk
while chunk := await file.read(1024 * 1024):
    tmp_file.write(chunk)
```

### 9. NumPy NaN/Inf Handling

```python
# ❌ BAD: NaN/Inf causes invalid JSON
result = {"value": np.sqrt(-1)}  # NaN

# ✅ GOOD: Handle edge cases
val = np.sqrt(-1)
result = {"value": None if np.isnan(val) else float(val)}
```

## Common Commands

### Run Demos

```bash
python demo.py              # Core patterns
python demo_metrics.py      # Metrics system
python demo_fastapi.py      # FastAPI patterns
```

### Run Tests

```bash
pytest tests/ -v                        # All tests
pytest tests/test_good_patterns.py -v   # Core patterns only
pytest --cov=. --cov-report=html        # With coverage
```

### Metrics System

```bash
# Collect metrics from tests
pytest --enable-metrics

# Analyze patterns
feedback-loop analyze

# Generate code
feedback-loop generate "your prompt here"

# View report (text or markdown)
feedback-loop report --format text
feedback-loop report --format markdown > report.md
```

### FastAPI Server

```bash
python examples/fastapi_audio_example.py
# Visit http://localhost:8000/docs
```

## When to Use Each Pattern

| Pattern | Use When | Don't Use When |
|---------|----------|----------------|
| NumPy conversion | Using NumPy with JSON APIs | Pure Python types only |
| Bounds checking | Accessing list/array elements | Length already verified |
| Specific exceptions | Handling expected errors | Re-raising all exceptions |
| Logger.debug() | Adding debug information | User-facing messages |
| Metadata logic | Complex business rules | Simple true/false checks |
| Temp file handling | Working with temp files | In-memory sufficient |
| Large file processing | Files > 10MB | Small files OK in memory |
| FastAPI streaming | Uploads > 10MB | Small uploads < 1MB |
| NaN/Inf handling | Scientific computing | Integer-only data |

## File Locations

```
feedback-loop/
├── documentation/          # Documentation
│   ├── GETTING_STARTED.md
│   └── QUICK_REFERENCE.md  # ← You are here
├── examples/               # Code examples
│   ├── good_patterns.py
│   └── bad_patterns.py
├── metrics/                # Metrics system
│   └── README.md           # API docs
└── tests/                  # Test suite
```

## Need More Detail?

- **Full workflow:** [AI Patterns Guide](AI_PATTERNS_GUIDE.md)
- **Metrics system:** [Metrics Guide](METRICS_GUIDE.md)
- **API reference:** [metrics/README.md](../metrics/README.md)
- **Results:** [Status/RESULTS.md](Status/RESULTS.md)
