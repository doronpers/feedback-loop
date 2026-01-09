"""
Example: MemU Integration for Pattern Memory

Demonstrates the MemU integration features:
- Storing patterns to semantic memory
- Semantic pattern retrieval
- Pattern recommendations
- Cross-session learning
"""

import asyncio
import os
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from metrics.memory_service import FeedbackLoopMemory
from metrics.pattern_manager import PatternManager


async def demo_basic_memory():
    """Demonstrate basic memory operations."""
    print("="*60)
    print("DEMO 1: Basic Memory Operations")
    print("="*60 + "\n")
    
    # Initialize memory service
    memory = FeedbackLoopMemory(storage_type="inmemory")
    
    print("1. Initializing MemU memory service...")
    if not await memory.initialize():
        print("   ✗ Failed to initialize. Make sure memu-py is installed:")
        print("     pip install memu-py")
        return False
    
    print("   ✓ Memory service initialized (in-memory storage)\n")
    
    # Store a pattern
    print("2. Storing a pattern to memory...")
    pattern = {
        "name": "numpy_json_serialization",
        "pattern_id": "np-json-001",
        "description": "Convert NumPy types before JSON serialization",
        "good_example": """
# Convert NumPy types to native Python types
import json
import numpy as np

data = {"value": float(np_array[0])}
json_str = json.dumps(data)
""",
        "bad_example": """
# Don't serialize NumPy types directly
import json
import numpy as np

data = {"value": np_array[0]}  # TypeError!
json_str = json.dumps(data)
""",
        "severity": "high",
        "occurrence_frequency": 5
    }
    
    result = await memory.memorize_pattern(pattern)
    if result:
        print("   ✓ Pattern stored successfully\n")
    else:
        print("   ✗ Failed to store pattern\n")
        return False
    
    # Get memory stats
    print("3. Memory statistics:")
    stats = await memory.get_memory_stats()
    if stats:
        print(f"   Total memories: {stats.get('total_memories', 0)}")
        print(f"   Patterns: {stats.get('patterns_count', 0)}")
        print(f"   Storage: {stats.get('storage_type', 'unknown')}\n")
    
    return True


async def demo_semantic_search():
    """Demonstrate semantic pattern search."""
    print("="*60)
    print("DEMO 2: Semantic Pattern Search")
    print("="*60 + "\n")
    
    # Initialize memory and store multiple patterns
    memory = FeedbackLoopMemory(storage_type="inmemory")
    if not await memory.initialize():
        print("✗ Failed to initialize memory")
        return False
    
    # Store several patterns
    patterns = [
        {
            "name": "numpy_json_serialization",
            "description": "Convert NumPy types to Python types before JSON serialization",
            "good_example": "json.dumps({'val': float(np_val)})",
            "severity": "high"
        },
        {
            "name": "bounds_checking",
            "description": "Check list bounds before accessing elements",
            "good_example": "if items: first = items[0]",
            "severity": "medium"
        },
        {
            "name": "specific_exceptions",
            "description": "Use specific exception types instead of bare except",
            "good_example": "except ValueError as e:",
            "severity": "medium"
        },
        {
            "name": "logger_debug",
            "description": "Use logger.debug() instead of print() statements",
            "good_example": "logger.debug('Processing item')",
            "severity": "low"
        }
    ]
    
    print("1. Storing patterns to memory...")
    for pattern in patterns:
        await memory.memorize_pattern(pattern)
    print(f"   ✓ Stored {len(patterns)} patterns\n")
    
    # Semantic search queries
    queries = [
        "How do I handle JSON serialization with NumPy arrays?",
        "Best practices for accessing list elements safely",
        "What's the recommended way to log debug information?"
    ]
    
    print("2. Semantic search examples:\n")
    for query in queries:
        print(f"   Query: {query}")
        result = await memory.retrieve_patterns(query, method="rag", limit=2)
        
        if result and result.get("results"):
            print(f"   Results: {len(result['results'])} patterns found")
            for idx, item in enumerate(result["results"], 1):
                metadata = item.get("metadata", {})
                print(f"      {idx}. {metadata.get('pattern_name', 'Unknown')}")
        else:
            print("   No results found")
        print()
    
    return True


async def demo_pattern_recommendations():
    """Demonstrate context-aware pattern recommendations."""
    print("="*60)
    print("DEMO 3: Pattern Recommendations")
    print("="*60 + "\n")
    
    # Initialize memory
    memory = FeedbackLoopMemory(storage_type="inmemory")
    if not await memory.initialize():
        print("✗ Failed to initialize memory")
        return False
    
    # Store patterns
    patterns = [
        {
            "name": "fastapi_file_upload",
            "description": "Handle file uploads in FastAPI using UploadFile",
            "good_example": "async def upload(file: UploadFile = File(...))",
            "tags": ["fastapi", "file-handling"]
        },
        {
            "name": "async_file_processing",
            "description": "Process large files asynchronously",
            "good_example": "async with aiofiles.open(path) as f:",
            "tags": ["async", "file-handling", "performance"]
        },
        {
            "name": "input_validation",
            "description": "Validate user input with Pydantic models",
            "good_example": "class UserInput(BaseModel):",
            "tags": ["fastapi", "validation", "security"]
        }
    ]
    
    print("1. Storing patterns...")
    for pattern in patterns:
        await memory.memorize_pattern(pattern)
    print(f"   ✓ Stored {len(patterns)} patterns\n")
    
    # Get recommendations for different contexts
    contexts = [
        "Building a FastAPI endpoint that accepts file uploads",
        "Need to validate user input in my API",
        "Processing large CSV files asynchronously"
    ]
    
    print("2. Getting pattern recommendations:\n")
    for context in contexts:
        print(f"   Context: {context}")
        recommendations = await memory.get_pattern_recommendations(context, limit=2)
        
        if recommendations:
            print(f"   Recommended {len(recommendations)} pattern(s):")
            for idx, rec in enumerate(recommendations, 1):
                print(f"      {idx}. {rec['pattern_name']} (score: {rec['score']:.2f})")
        else:
            print("   No recommendations")
        print()
    
    return True


async def demo_pattern_manager_integration():
    """Demonstrate PatternManager with memory integration."""
    print("="*60)
    print("DEMO 4: PatternManager + Memory Integration")
    print("="*60 + "\n")
    
    # Create a temporary patterns file
    import tempfile
    import json
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        patterns_file = f.name
        json.dump({
            "patterns": [
                {
                    "pattern_id": "test-001",
                    "name": "test_pattern",
                    "description": "A test pattern",
                    "good_example": "# Good code",
                    "bad_example": "# Bad code",
                    "severity": "low",
                    "occurrence_frequency": 1
                }
            ],
            "changelog": []
        }, f)
    
    try:
        # Initialize PatternManager with memory
        print("1. Initializing PatternManager with memory...")
        manager = PatternManager(
            pattern_library_path=patterns_file,
            use_memory=True,
            memory_config={"storage_type": "inmemory"}
        )
        
        if not manager.memory:
            print("   ✗ Memory not initialized")
            return False
        
        await manager.memory.initialize()
        print("   ✓ PatternManager initialized with memory\n")
        
        # Sync patterns to memory
        print("2. Syncing patterns to memory...")
        synced = await manager.sync_patterns_to_memory()
        print(f"   ✓ Synced {synced} pattern(s)\n")
        
        # Semantic search through PatternManager
        print("3. Searching for patterns...")
        query = "test pattern for demonstration"
        results = await manager.retrieve_similar_patterns(query, limit=1)
        
        if results:
            print(f"   ✓ Found {len(results)} matching pattern(s)")
            for result in results:
                if isinstance(result, dict):
                    metadata = result.get("metadata", {})
                    print(f"      - {metadata.get('pattern_name', 'Unknown')}")
        else:
            print("   No patterns found")
        
        print()
        
    finally:
        # Clean up
        Path(patterns_file).unlink(missing_ok=True)
    
    return True


async def main():
    """Run all demos."""
    print("\n" + "="*60)
    print("MemU Integration Demo")
    print("="*60 + "\n")
    
    # Check if MemU is available
    try:
        import memu
        print("✓ MemU library is available\n")
    except ImportError:
        print("✗ MemU library not found")
        print("  Install with: pip install memu-py\n")
        return
    
    # Check for OpenAI API key
    if not os.getenv("OPENAI_API_KEY"):
        print("⚠  Warning: OPENAI_API_KEY not set")
        print("   Some features may not work without an API key\n")
    
    # Run demos
    demos = [
        ("Basic Memory Operations", demo_basic_memory),
        ("Semantic Pattern Search", demo_semantic_search),
        ("Pattern Recommendations", demo_pattern_recommendations),
        ("PatternManager Integration", demo_pattern_manager_integration)
    ]
    
    for name, demo_func in demos:
        try:
            success = await demo_func()
            if not success:
                print(f"\n⚠  {name} demo encountered issues\n")
        except Exception as e:
            print(f"\n✗ {name} demo failed: {e}\n")
        
        # Pause between demos
        await asyncio.sleep(1)
    
    print("="*60)
    print("Demo Complete!")
    print("="*60 + "\n")
    
    print("Next steps:")
    print("  1. Enable memory in your project: export FEEDBACK_LOOP_MEMORY_ENABLED=true")
    print("  2. Sync patterns: feedback-loop memory sync")
    print("  3. Query patterns: feedback-loop memory query 'your question'")
    print("  4. Get recommendations: feedback-loop memory recommend --context 'your context'")
    print()


if __name__ == "__main__":
    asyncio.run(main())
