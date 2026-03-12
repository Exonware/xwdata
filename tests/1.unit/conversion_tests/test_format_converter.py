#!/usr/bin/env python3
"""
#exonware/xwdata/tests/1.unit/conversion_tests/test_format_converter.py
Unit tests for FormatConverter.
Company: eXonware.com
Author: eXonware Backend Team
Email: connect@exonware.com
Version: 0.1.0.1
Generation Date: 26-Jan-2025
"""

import pytest
from pathlib import Path
@pytest.mark.xwdata_unit

class TestFormatConverter:
    """Unit tests for FormatConverter."""
    @pytest.fixture

    def converter(self):
        """Create FormatConverter instance."""
        from exonware.xwdata.operations.format_conversion import FormatConverter
        return FormatConverter(enable_caching=True)
    @pytest.fixture

    def sample_json(self):
        """Sample JSON data."""
        return '{"name": "Alice", "age": 30}'
    @pytest.mark.asyncio

    async def test_convert_json_to_yaml(self, converter, sample_json):
        """Test JSON to YAML conversion."""
        result = await converter.convert(sample_json, 'json', 'yaml')
        assert isinstance(result, str)
        assert 'name' in result.lower()
        assert 'Alice' in result or '"Alice"' in result
    @pytest.mark.asyncio

    async def test_convert_same_format(self, converter, sample_json):
        """Test conversion to same format (should return unchanged)."""
        result = await converter.convert(sample_json, 'json', 'json')
        # Should return same data (or equivalent)
        assert isinstance(result, str)
        assert 'Alice' in result
    @pytest.mark.asyncio

    async def test_convert_file(self, converter, sample_json, tmp_path):
        """Test file conversion."""
        # Create source file
        source_file = tmp_path / 'source.json'
        source_file.write_text(sample_json)
        # Convert to YAML
        target_file = tmp_path / 'target.yaml'
        result_path = await converter.convert_file(
            source_file,
            target_file,
            target_format='yaml'
        )
        assert result_path == target_file
        assert target_file.exists()
        assert 'name' in target_file.read_text().lower()
    @pytest.mark.asyncio

    async def test_conversion_caching(self, converter, sample_json):
        """Test conversion result caching."""
        # First conversion
        result1 = await converter.convert(sample_json, 'json', 'yaml')
        # Second conversion (should use cache)
        result2 = await converter.convert(sample_json, 'json', 'yaml')
        # Results should be equivalent
        assert result1 == result2

    def test_get_conversion_path(self, converter):
        """Test conversion path generation."""
        path = converter.get_conversion_path('json', 'yaml')
        # Should use xwjson as intermediate
        assert len(path) >= 2
        assert path[0] == 'json'
        assert path[-1] == 'yaml'
        assert 'xwjson' in path or 'json' in path

    def test_supports_conversion(self, converter):
        """Test conversion support checking."""
        # JSON to YAML should be supported
        assert converter.supports_conversion('json', 'yaml') is True
        # Unknown formats
        # Note: This depends on what's registered in SerializationRegistry
        # For now, we test with known formats
        assert converter.supports_conversion('json', 'json') is True
