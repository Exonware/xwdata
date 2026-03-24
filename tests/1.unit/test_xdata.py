#!/usr/bin/env python3
"""Basic smoke tests for the current XWData API."""

from exonware.xwdata import XWData


def test_basic_functionality():
    """Create, read, mutate, and serialize via the public facade API."""
    data = XWData.from_native({"test": "data", "number": 42})
    assert data.get("test") == "data"
    assert data.get("number") == 42
    json_str = data.to_format("json")
    assert '"test"' in json_str
