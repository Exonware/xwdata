#!/usr/bin/env python3
"""
Integration tests for async/sync event loop patterns.
Tests that sync wrappers work correctly without hanging or event loop conflicts.
Company: eXonware.com
Author: eXonware Backend Team
Email: connect@exonware.com
Version: 0.0.1.3
Generation Date: October 27, 2025
"""

import pytest
import asyncio
from exonware.xwdata import XWData
@pytest.mark.xdata_integration

class TestAsyncSyncPatterns:
    """Test async/sync event loop patterns work correctly."""

    def test_save_no_hang(self, tmp_path):
        """Test save() completes without hanging."""
        # Create XWData instance
        data = XWData({'key': 'value', 'number': 42})
        # Save to file via canonical async API
        output_path = tmp_path / "test.json"
        result = asyncio.run(data.save(output_path))
        # Should complete and return self
        assert result is data
        assert output_path.exists()
        # Verify content
        content = output_path.read_text()
        assert 'key' in content
        assert 'value' in content

    def test_sync_load_from_file(self, tmp_path):
        """Test sync loading from file in __init__."""
        # Create test file
        test_file = tmp_path / "test.json"
        test_file.write_text('{"name": "test", "value": 123}')
        # Load using sync init (should use new event loop pattern)
        data = XWData(test_file)
        # Verify data loaded
        assert data['name'] == 'test'
        assert data['value'] == 123

    def test_sync_create_from_dict(self):
        """Test sync creation from dict in __init__."""
        # Create from dict (should use new event loop pattern)
        data = XWData({'a': 1, 'b': 2, 'c': 3})
        # Verify data
        assert data['a'] == 1
        assert data['b'] == 2
        assert data['c'] == 3

    def test_sync_create_from_list(self):
        """Test sync creation from list in __init__."""
        # Create from list (should use new event loop pattern)
        data = XWData([1, 2, 3, 4, 5])
        # Verify data
        assert len(data) == 5
        assert data[0] == 1
        assert data[4] == 5

    def test_multiple_sync_operations(self, tmp_path):
        """Test multiple sync operations in sequence."""
        # This tests that event loops are properly cleaned up
        # First operation
        data1 = XWData({'first': 'operation'})
        file1 = tmp_path / "first.json"
        asyncio.run(data1.save(file1))
        # Second operation
        data2 = XWData({'second': 'operation'})
        file2 = tmp_path / "second.json"
        asyncio.run(data2.save(file2))
        # Third operation - load back
        data3 = XWData(file1)
        # All should work
        assert file1.exists()
        assert file2.exists()
        assert data3['first'] == 'operation'

    def test_save_with_formats(self, tmp_path):
        """Test save() with different formats."""
        data = XWData({'test': 'data', 'nested': {'x': 1}})
        # JSON
        json_file = tmp_path / "test.json"
        asyncio.run(data.save(json_file))
        assert json_file.exists()
        # YAML
        yaml_file = tmp_path / "test.yaml"
        asyncio.run(data.save(yaml_file))
        assert yaml_file.exists()
        # XML
        xml_file = tmp_path / "test.xml"
        asyncio.run(data.save(xml_file))
        assert xml_file.exists()

    def test_sync_wrapper_with_universal_options(self, tmp_path):
        """Test save() accepts universal options."""
        data = XWData({'z': 1, 'a': 2, 'm': 3})
        # Save with universal options
        output_path = tmp_path / "sorted.json"
        asyncio.run(data.save(output_path, sorted=True, pretty=True))
        # Verify file created
        assert output_path.exists()
        # Verify sorted (a should come before m, m before z)
        content = output_path.read_text()
        assert content.index('"a"') < content.index('"m"')
        assert content.index('"m"') < content.index('"z"')

    def test_no_event_loop_conflict(self, tmp_path):
        """Test that repeated save() calls don't conflict with each other."""
        # Create multiple instances and save them
        datasets = [
            XWData({'dataset': i, 'value': i * 10})
            for i in range(5)
        ]
        # Save all with separate event loops
        for i, data in enumerate(datasets):
            output_path = tmp_path / f"dataset_{i}.json"
            asyncio.run(data.save(output_path))
        # Verify all saved
        for i in range(5):
            assert (tmp_path / f"dataset_{i}.json").exists()
    @pytest.mark.asyncio

    async def test_async_methods_still_work(self, tmp_path):
        """Test that async methods still work correctly."""
        # Create via canonical sync factory
        data = XWData.from_native({'async': 'test'})
        # Save via async method
        output_path = tmp_path / "async_test.json"
        await data.save(output_path)
        # Load via async method
        loaded = await XWData.load(output_path)
        # Verify
        assert loaded['async'] == 'test'
@pytest.mark.xdata_integration

class TestEventLoopCleanup:
    """Test that event loops are properly cleaned up."""

    def test_event_loop_cleanup(self):
        """Test that sync wrappers clean up event loops."""
        # Before operation - get initial state
        try:
            loop = asyncio.get_event_loop()
            initial_running = loop.is_running()
        except RuntimeError:
            initial_running = False
        # Perform sync operation
        data = XWData({'test': 'cleanup'})
        # After operation - event loop should be in same state
        try:
            loop = asyncio.get_event_loop()
            final_running = loop.is_running()
        except RuntimeError:
            final_running = False
        # State should match
        assert initial_running == final_running

    def test_no_lingering_event_loop(self, tmp_path):
        """Test no event loops linger after sync operations."""
        # Perform operation
        data = XWData({'test': 'data'})
        output_path = tmp_path / "test.json"
        asyncio.run(data.save(output_path))
        # Event loop should be None or not running
        try:
            loop = asyncio.get_event_loop()
            assert not loop.is_running()
        except RuntimeError:
            # No event loop is also fine
            pass
if __name__ == '__main__':
    pytest.main([__file__, '-v'])
