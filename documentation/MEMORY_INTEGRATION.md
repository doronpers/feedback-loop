# Memory Integration Guide

feedback-loop integrates with [MemU](https://github.com/NevaMind-AI/memU), an agentic memory framework, to provide intelligent, long-term memory for development patterns.

## Overview

The MemU integration transforms feedback-loop from a static pattern library into a **self-evolving knowledge system** that learns from your development sessions over time.

### Benefits

- **Semantic Pattern Retrieval**: Query patterns by concept, not just by name
- **Self-Evolving Patterns**: Patterns improve based on actual usage
- **Cross-Project Learning**: Share patterns across all your projects
- **Multimodal Memory**: Store code, logs, test results, and code reviews together
- **Intelligent Recommendations**: Get context-aware pattern suggestions
- **Zero Config Required**: Works with in-memory storage out of the box

## Installation

```bash
# Install feedback-loop with MemU support
pip install -e .
pip install memu-py>=0.1.0
```

## Configuration

Memory integration is **opt-in** via environment variables:

```bash
# Enable MemU integration (default: false)
export FEEDBACK_LOOP_MEMORY_ENABLED=true

# OpenAI API key for embeddings
export OPENAI_API_KEY=sk-...

# Storage type (default: inmemory)
export FEEDBACK_LOOP_MEMORY_STORAGE=inmemory

# PostgreSQL connection (only for postgres storage)
export FEEDBACK_LOOP_MEMORY_DB_URL=postgresql://user:pass@localhost:5432/feedback_loop
```

### Storage Options

#### In-Memory Storage (Default)

Perfect for getting started - no database required:

```bash
export FEEDBACK_LOOP_MEMORY_STORAGE=inmemory
```

**Pros:**
- Zero configuration
- Fast performance
- Great for development and testing

**Cons:**
- Memory cleared on restart
- Not suitable for long-term persistence

#### PostgreSQL Storage

For production use with persistent storage:

```bash
export FEEDBACK_LOOP_MEMORY_STORAGE=postgres
export FEEDBACK_LOOP_MEMORY_DB_URL=postgresql://user:pass@localhost:5432/feedback_loop
```

**Pros:**
- Persistent storage
- Scales with your data
- Production-ready

**Cons:**
- Requires PostgreSQL setup
- Additional infrastructure

## CLI Commands

### Sync Patterns to Memory

Store all patterns from `patterns.json` into MemU memory:

```bash
feedback-loop memory sync
```

Example output:
```
=== Feedback Loop - Memory Sync ===

📚 Syncing 12 patterns to memory...

✓ Synced 12 patterns to MemU memory
  Storage: inmemory
```

### Semantic Pattern Query

Search patterns using natural language:

```bash
feedback-loop memory query "How do I safely serialize NumPy arrays in JSON?"
```

Example output:
```
=== Feedback Loop - Memory Query ===

Query: How do I safely serialize NumPy arrays in JSON?
Limit: 5

🔍 Searching patterns...

✓ Found 2 patterns:

1. numpy_json_serialization (score: 0.92)
   Convert NumPy types to Python types before JSON serialization...

2. json_encoding_validation (score: 0.78)
   Validate JSON encoding before sending to API...
```

### Get Pattern Recommendations

Get context-aware pattern suggestions:

```bash
feedback-loop memory recommend --context "Building a FastAPI endpoint that accepts file uploads"
```

Example output:
```
=== Feedback Loop - Pattern Recommendations ===

Context: Building a FastAPI endpoint that accepts file uploads
Limit: 3

💡 Getting recommendations...

✓ Recommended 3 patterns:

1. fastapi_file_upload (score: 0.95)
   Handle file uploads in FastAPI using UploadFile...

2. async_file_processing (score: 0.88)
   Process large files asynchronously...

3. input_validation (score: 0.82)
   Validate user input with Pydantic models...
```

### Memory Statistics

View memory usage stats:

```bash
feedback-loop memory stats
```

Example output:
```
=== Feedback Loop - Memory Statistics ===

📊 Memory Statistics:
  Total memories: 25
  Patterns: 12
  Sessions: 8
  Reviews: 5
  Storage type: inmemory
  Status: ✓ Initialized
```

## Programmatic Usage

### Basic Memory Operations

```python
import asyncio
from metrics.memory_service import FeedbackLoopMemory

async def main():
    # Initialize memory service
    memory = FeedbackLoopMemory(storage_type="inmemory")
    await memory.initialize()

    # Store a pattern
    pattern = {
        "name": "numpy_json_serialization",
        "description": "Convert NumPy types before JSON serialization",
        "good_example": "json.dumps({'val': float(np_val)})",
        "severity": "high"
    }
    await memory.memorize_pattern(pattern)

    # Semantic search
    results = await memory.retrieve_patterns(
        "How do I handle JSON with NumPy?",
        method="rag",
        limit=5
    )

    # Get recommendations
    recommendations = await memory.get_pattern_recommendations(
        context="Building FastAPI endpoint",
        limit=3
    )

asyncio.run(main())
```

### PatternManager with Memory

```python
import asyncio
from metrics.pattern_manager import PatternManager

async def main():
    # Initialize with memory enabled
    manager = PatternManager(
        pattern_library_path="patterns.json",
        use_memory=True,
        memory_config={
            "storage_type": "inmemory",
            "openai_api_key": "sk-..."
        }
    )

    # Initialize memory
    await manager.memory.initialize()

    # Sync all patterns to memory
    synced_count = await manager.sync_patterns_to_memory()
    print(f"Synced {synced_count} patterns")

    # Semantic search through manager
    results = await manager.retrieve_similar_patterns(
        "safe file handling",
        limit=5
    )

    for result in results:
        print(f"Found: {result.get('name')}")

asyncio.run(main())
```

### MetricsCollector with Memory

```python
import asyncio
from metrics.collector import MetricsCollector
from metrics.memory_service import FeedbackLoopMemory

async def main():
    # Initialize memory
    memory = FeedbackLoopMemory()
    await memory.initialize()

    # Create collector with memory
    collector = MetricsCollector(memory_service=memory)

    # Log metrics
    collector.log_bug(
        pattern="numpy_json_serialization",
        error="TypeError: Object of type float32 is not JSON serializable",
        code="json.dumps({'val': np_val})",
        file_path="api/endpoints.py",
        line=42
    )

    collector.log_code_generation(
        prompt="Create JSON API endpoint",
        patterns_applied=["numpy_json_serialization", "input_validation"],
        confidence=0.9,
        success=True
    )

    # Store session to memory
    await collector.store_session_to_memory(session_id="dev-session-001")

asyncio.run(main())
```

## Architecture

```
┌─────────────────────────────────────────┐
│         feedback-loop Core              │
│  (patterns.json, metrics, collector)    │
└──────────────┬──────────────────────────┘
               │
               ▼
┌─────────────────────────────────────────┐
│      FeedbackLoopMemory Service         │
│      (memory_service.py)                │
└──────────────┬──────────────────────────┘
               │
               ▼
┌─────────────────────────────────────────┐
│           MemU Framework                │
│   (semantic storage & retrieval)        │
└──────────────┬──────────────────────────┘
               │
               ▼
┌──────────────┬──────────────────────────┐
│  In-Memory   │    PostgreSQL + pgvector  │
│   Storage    │         Storage           │
└──────────────┴──────────────────────────┘
```

### Component Roles

- **FeedbackLoopMemory**: Bridge between feedback-loop and MemU
- **PatternManager**: Optional memory-enhanced pattern operations
- **MetricsCollector**: Stores development sessions to memory
- **MemU**: Handles semantic embeddings, storage, and retrieval

## Use Cases

### 1. Onboarding New Team Members

```bash
# New developer asks: "How do we handle database connections?"
feedback-loop memory query "database connection patterns"

# Get patterns with real examples from your codebase
```

### 2. Context-Aware Code Review

```python
# During code review, get relevant patterns
recommendations = await memory.get_pattern_recommendations(
    context="Reviewing FastAPI endpoint with file upload",
    limit=5
)
```

### 3. Pattern Evolution Tracking

```python
# Store development session
await collector.store_session_to_memory()

# Later, MemU helps identify which patterns are most effective
```

### 4. Cross-Project Pattern Sharing

When working across multiple projects, patterns stored in memory are available everywhere:

```bash
# In project A
cd project-a
feedback-loop memory sync

# In project B - patterns from A are available
cd ../project-b
feedback-loop memory query "authentication patterns"
```

## Examples

Run the comprehensive example script:

```bash
python examples/example_memory_patterns.py
```

This demonstrates:
- Basic memory operations
- Semantic pattern search
- Pattern recommendations
- PatternManager integration

## Backward Compatibility

**Important:** MemU integration is completely **opt-in**.

- If `FEEDBACK_LOOP_MEMORY_ENABLED` is not set, feedback-loop works exactly as before
- All existing tests and functionality remain unchanged
- JSON pattern storage continues to be the primary data store
- MemU is an enhancement layer on top of existing functionality

### Migration Path

1. **Phase 1**: Continue using JSON patterns as usual
2. **Phase 2**: Enable memory and sync patterns
3. **Phase 3**: Start using semantic queries alongside JSON
4. **Phase 4**: Leverage recommendations in your workflow

## Performance Considerations

### In-Memory Storage

- **Initialization**: < 100ms
- **Pattern storage**: < 50ms per pattern
- **Semantic query**: ~200-500ms (depends on OpenAI API)
- **Memory usage**: ~50MB for 1000 patterns

### PostgreSQL Storage

- **Initialization**: < 500ms
- **Pattern storage**: < 100ms per pattern
- **Semantic query**: ~300-700ms
- **Scalability**: Handles 100K+ patterns efficiently

## Troubleshooting

### MemU Not Available

```bash
✗ Memory integration is not enabled
  Set FEEDBACK_LOOP_MEMORY_ENABLED=true to enable
```

**Solution:** Install MemU and set environment variable:
```bash
pip install memu-py
export FEEDBACK_LOOP_MEMORY_ENABLED=true
```

### OpenAI API Key Missing

Some features require an OpenAI API key for embeddings:

```bash
export OPENAI_API_KEY=sk-...
```

### PostgreSQL Connection Error

If using PostgreSQL storage, ensure:
1. PostgreSQL is running
2. Database exists
3. pgvector extension is installed
4. Connection string is correct

```bash
# Install pgvector in PostgreSQL
CREATE EXTENSION IF NOT EXISTS vector;
```

## Best Practices

1. **Start with in-memory**: Test the integration before committing to PostgreSQL
2. **Sync regularly**: Run `feedback-loop memory sync` after updating patterns
3. **Use descriptive queries**: More context = better results
4. **Review recommendations**: MemU suggests patterns, but human review is valuable
5. **Track effectiveness**: Monitor which patterns MemU recommends most

## License Compatibility

- **feedback-loop**: MIT License
- **MemU**: Apache 2.0 License

✅ **Compatible**: Apache 2.0 code can be used in MIT projects

## References

- [MemU Repository](https://github.com/NevaMind-AI/memU)
- [MemU Documentation](https://memu.pro/docs)
- [MemU API Reference](https://memu.pro/docs#cloud-version)
- [OpenAI Embeddings API](https://platform.openai.com/docs/guides/embeddings)

## Support

For issues related to:
- **feedback-loop memory integration**: Open an issue in this repository
- **MemU framework**: Visit the [MemU repository](https://github.com/NevaMind-AI/memU)

## Future Enhancements

Planned features for memory integration:

- [ ] Automatic pattern effectiveness learning
- [ ] Multi-LLM embedding support (beyond OpenAI)
- [ ] Pattern version tracking and evolution
- [ ] Team-based pattern sharing
- [ ] Integration with code review workflows
- [ ] Pattern conflict detection and resolution
