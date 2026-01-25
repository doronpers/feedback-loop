#!/usr/bin/env python
"""
Example: Cloud Sync Integration

This example demonstrates how to use the cloud sync features of feedback-loop.

Requirements:
1. API server running (python api/main.py)
2. User account registered
"""

import json
from pathlib import Path

from metrics.integrate import MetricsIntegration
from metrics.sync_client import CloudSyncClient, LocalSyncClient, create_sync_client


def example_local_sync():
    """Example using local file system sync (default behavior)."""
    print("=" * 60)
    print("Example 1: Local File System Sync (Default)")
    print("=" * 60)

    # Create local sync client
    client = LocalSyncClient(
        patterns_file="example_patterns.json", metrics_file="example_metrics.json"
    )

    # Sync some patterns
    patterns = [
        {
            "name": "error_handling",
            "description": "Always use specific exception types",
            "category": "best_practices",
        },
        {
            "name": "resource_cleanup",
            "description": "Use context managers for file operations",
            "category": "safety",
        },
    ]

    result = client.sync_patterns(patterns)
    print(f"\n✓ Synced {result['synced_count']} patterns")
    print(f"  Storage: {result['storage']}")
    print(f"  Timestamp: {result['timestamp']}")

    # Pull patterns back
    pulled = client.pull_patterns()
    print(f"\n✓ Pulled {len(pulled)} patterns:")
    for p in pulled:
        print(f"  - {p['name']}: {p['description']}")

    # Cleanup
    Path("example_patterns.json").unlink(missing_ok=True)
    Path("example_metrics.json").unlink(missing_ok=True)


def example_cloud_sync():
    """Example using cloud sync (requires authentication)."""
    print("\n" + "=" * 60)
    print("Example 2: Cloud Sync (Authenticated)")
    print("=" * 60)

    # Check for saved credentials
    auth_file = Path.home() / ".feedback-loop" / "auth.json"

    if not auth_file.exists():
        print("\n⚠ Not logged in. Run 'feedback-loop login' first.")
        print("\nAlternatively, create a cloud client manually:")
        print("  client = CloudSyncClient(")
        print("    api_url='http://localhost:8000',")
        print("    api_key='your_api_key'")
        print("  )")
        return

    # Load credentials
    with open(auth_file) as f:
        auth = json.load(f)

    print(f"\n✓ Logged in as: {auth['username']}")
    print(f"  Organization: {auth['organization_id']}")

    # Create cloud sync client
    client = CloudSyncClient(
        api_url=auth["api_url"],
        api_key=auth["api_key"],
        organization_id=str(auth["organization_id"]),
    )

    # Sync patterns to cloud
    patterns = [
        {
            "name": "numpy_json_serialization",
            "description": "Convert NumPy types before JSON serialization",
            "category": "serialization",
            "version": 1,
        }
    ]

    result = client.sync_patterns(patterns)
    print(f"\n✓ Synced to cloud: {result['synced_count']} patterns")
    print(f"  Storage: {result['storage']}")

    # Pull patterns from cloud
    pulled = client.pull_patterns()
    print(f"\n✓ Team patterns available: {len(pulled)}")
    for p in pulled:
        print(f"  - {p['name']} (v{p.get('version', 1)})")


def example_metrics_integration():
    """Example using MetricsIntegration with sync client."""
    print("\n" + "=" * 60)
    print("Example 3: MetricsIntegration with Cloud Sync")
    print("=" * 60)

    # Check for authentication
    auth_file = Path.home() / ".feedback-loop" / "auth.json"

    if auth_file.exists():
        # Load credentials
        with open(auth_file) as f:
            auth = json.load(f)

        # Create cloud sync client
        sync_client = CloudSyncClient(
            api_url=auth["api_url"],
            api_key=auth["api_key"],
            organization_id=str(auth["organization_id"]),
        )
        print("\n✓ Using cloud sync")
    else:
        # Fall back to local sync
        sync_client = LocalSyncClient()
        print("\n✓ Using local sync (not logged in)")

    # Create integration with sync client
    _integration = MetricsIntegration(sync_client=sync_client)

    print(f"  Sync client type: {type(sync_client).__name__}")
    print(f"  Authenticated: {sync_client.is_authenticated()}")


def example_factory():
    """Example using the factory function."""
    print("\n" + "=" * 60)
    print("Example 4: Using Factory Function")
    print("=" * 60)

    # Create local client (default)
    client = create_sync_client(use_cloud=False)
    print(f"\n✓ Created client: {type(client).__name__}")
    print(f"  Authenticated: {client.is_authenticated()}")

    # Try to create cloud client (will fall back if not authenticated)
    client = create_sync_client(
        use_cloud=True,
        api_url="http://localhost:8000",
        api_key="",  # Empty key - will fall back
    )
    print(f"\n✓ Attempted cloud client: {type(client).__name__}")
    print("  (Falls back to local when credentials missing)")


def main():
    """Run all examples."""
    print("\n" + "=" * 60)
    print("Feedback Loop - Cloud Sync Examples")
    print("=" * 60)

    try:
        # Run examples
        example_local_sync()
        example_cloud_sync()
        example_metrics_integration()
        example_factory()

        print("\n" + "=" * 60)
        print("Examples completed successfully!")
        print("=" * 60)

        print("\nNext steps:")
        print("1. Start API server: python api/main.py")
        print("2. Login: feedback-loop login")
        print("3. Use cloud features: feedback-loop analyze")

    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    main()
