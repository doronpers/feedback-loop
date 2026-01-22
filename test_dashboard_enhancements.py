#!/usr/bin/env python3
"""
Test script for dashboard UX enhancements.

Tests the new features:
- Date range filtering
- Export functionality
- Dark mode support
- Loading states
- Error handling
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def test_imports():
    """Test that all modules import correctly."""
    print("Testing imports...")
    try:
        from src.feedback_loop.api.dashboard import router, parse_date_range
        print("✓ Dashboard module imports successfully")
        return True
    except Exception as e:
        print(f"✗ Import failed: {e}")
        return False

def test_date_range_parsing():
    """Test date range parsing function."""
    print("\nTesting date range parsing...")
    try:
        from src.feedback_loop.api.dashboard import parse_date_range
        from datetime import datetime, timedelta

        test_cases = [
            ("7d", 7),
            ("30d", 30),
            ("90d", 90),
            ("1y", 365),
            ("all", None),
        ]

        for date_range, expected_days in test_cases:
            start_date, end_date = parse_date_range(date_range)

            if date_range == "all":
                assert start_date is None, f"Expected None for 'all', got {start_date}"
                print(f"  ✓ {date_range}: start_date=None (correct)")
            else:
                expected_start = end_date - timedelta(days=expected_days)
                # Allow 1 second tolerance for timing
                diff = abs((start_date - expected_start).total_seconds())
                assert diff < 2, f"Expected ~{expected_days} days, got {diff/86400:.1f} days"
                print(f"  ✓ {date_range}: {expected_days} days (correct)")

        print("✓ All date range parsing tests passed")
        return True
    except Exception as e:
        print(f"✗ Date range parsing test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_file_structure():
    """Test that all required files exist."""
    print("\nTesting file structure...")
    files = {
        "dashboard.py": "src/feedback_loop/api/dashboard.py",
        "dashboard.js": "src/feedback_loop/api/static/dashboard.js",
        "dashboard.css": "src/feedback_loop/api/static/dashboard.css",
        "dashboard.html": "src/feedback_loop/api/templates/dashboard.html",
    }

    all_exist = True
    for name, path in files.items():
        file_path = project_root / path
        if file_path.exists():
            size = file_path.stat().st_size
            print(f"  ✓ {name}: {size:,} bytes")
        else:
            print(f"  ✗ {name}: MISSING")
            all_exist = False

    return all_exist

def test_css_features():
    """Test that CSS includes new features."""
    print("\nTesting CSS features...")
    css_path = project_root / "src/feedback_loop/api/static/dashboard.css"

    if not css_path.exists():
        print("  ✗ CSS file not found")
        return False

    css_content = css_path.read_text()

    features = {
        "Dark mode variables": "[data-theme=\"dark\"]" in css_content,
        "Loading skeleton": ".skeleton-line" in css_content,
        "Error state": ".error-state" in css_content,
        "Empty state": ".empty-state" in css_content,
        "Theme toggle": ".theme-toggle" in css_content,
        "Dashboard controls": ".dashboard-controls" in css_content,
    }

    all_present = True
    for feature, present in features.items():
        if present:
            print(f"  ✓ {feature}")
        else:
            print(f"  ✗ {feature} - MISSING")
            all_present = False

    return all_present

def test_javascript_features():
    """Test that JavaScript includes new features."""
    print("\nTesting JavaScript features...")
    js_path = project_root / "src/feedback_loop/api/static/dashboard.js"

    if not js_path.exists():
        print("  ✗ JavaScript file not found")
        return False

    js_content = js_path.read_text()

    features = {
        "Dark mode init": "initDarkMode" in js_content,
        "Date range filter": "createDashboardControls" in js_content,
        "Export function": "exportDashboardData" in js_content,
        "Loading states": "showLoadingStates" in js_content,
        "Error handling": "showErrorState" in js_content,
        "Enhanced chart config": "getChartConfig" in js_content,
        "Date range update": "updateDateRange" in js_content,
    }

    all_present = True
    for feature, present in features.items():
        if present:
            print(f"  ✓ {feature}")
        else:
            print(f"  ✗ {feature} - MISSING")
            all_present = False

    return all_present

def test_html_features():
    """Test that HTML includes accessibility features."""
    print("\nTesting HTML features...")
    html_path = project_root / "src/feedback_loop/api/templates/dashboard.html"

    if not html_path.exists():
        print("  ✗ HTML file not found")
        return False

    html_content = html_path.read_text()

    features = {
        "ARIA labels": "aria-label" in html_content,
        "ARIA live regions": "aria-live" in html_content,
        "Role attributes": "role=" in html_content,
        "Card IDs": 'id="total-bugs-card"' in html_content,
    }

    all_present = True
    for feature, present in features.items():
        if present:
            print(f"  ✓ {feature}")
        else:
            print(f"  ✗ {feature} - MISSING")
            all_present = False

    return all_present

def main():
    """Run all tests."""
    print("=" * 60)
    print("Dashboard UX Enhancement Tests")
    print("=" * 60)

    tests = [
        ("File Structure", test_file_structure),
        ("Imports", test_imports),
        ("Date Range Parsing", test_date_range_parsing),
        ("CSS Features", test_css_features),
        ("JavaScript Features", test_javascript_features),
        ("HTML Features", test_html_features),
    ]

    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"\n✗ {test_name} raised exception: {e}")
            results.append((test_name, False))

    print("\n" + "=" * 60)
    print("Test Summary")
    print("=" * 60)

    passed = sum(1 for _, result in results if result)
    total = len(results)

    for test_name, result in results:
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{status}: {test_name}")

    print(f"\nTotal: {passed}/{total} tests passed")

    if passed == total:
        print("\n🎉 All tests passed! Dashboard enhancements are ready.")
        return 0
    else:
        print(f"\n⚠️  {total - passed} test(s) failed. Please review.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
