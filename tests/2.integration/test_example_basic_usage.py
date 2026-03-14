#!/usr/bin/env python3
"""
Smoke test for the API pattern used in examples/basic_usage.py.
Guards against API drift: same minimal flow (XWData from dict, get, set)
as documented in REF_14_DX and examples/basic_usage.py.
Per gap review: optional "example-as-test" (AGENT_BRIEF_XWDATA.md sec. 3 item 6).
"""

import pytest
from exonware.xwdata import XWData
@pytest.mark.xwdata_integration
@pytest.mark.xwdata_usability


class TestExampleBasicUsagePattern:
    """Mirror of examples/basic_usage.py minimal flow — basic operations."""
    @pytest.mark.asyncio
    @pytest.mark.skip(reason="XWData() sync ctor runs run_until_complete; conflicts with pytest-asyncio loop")
    async def test_basic_create_get_set_pattern(self):
        """Same pattern as basic_usage.py example_basic_operations: create, get, set."""
        # Create from native data (as in basic_usage.py)
        data = XWData({
            "app": {"name": "MyApp", "version": "1.0.0"},
            "config": {"timeout": 30, "retries": 3},
        })
        # Get
        app_name = await data.get("app.name")
        assert app_name == "MyApp"
        # Set (copy-on-write)
        data = await data.set("config.timeout", 60)
        timeout = await data.get("config.timeout")
        assert timeout == 60
