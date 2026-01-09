import pytest


@pytest.mark.xfail(reason="Intentional failure to test metrics collection for bounds_checking pattern", strict=True)
def test_dummy_failure():
    """A dummy failing test to trigger metrics collection.
    
    This test intentionally fails to verify that the metrics collection
    system correctly captures and categorizes bounds checking violations.
    """
    # This matches the 'bounds_checking' pattern
    items = []
    _ = items[0]
