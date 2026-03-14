#!/usr/bin/env python3
"""
#exonware/xwdata/tests/0.core/test_core_format_conversion.py
Core tests for format conversion (BaaS feature).
Tests format conversion using xwjson XWJSONConverter.
Company: eXonware.com
Author: eXonware Backend Team
Email: connect@exonware.com
Version: 0.1.0.1
Generation Date: 26-Jan-2025
"""

import pytest
from pathlib import Path

try:
    import exonware.xwsyntax  # noqa: F401
    _has_xwsyntax = True
except Exception:
    _has_xwsyntax = False

@pytest.mark.xwdata_core

class TestCoreFormatConversion:
    """Core format conversion functionality tests."""
    @pytest.fixture

    def sample_data(self):
        """Sample data for conversion tests."""
        return {
            'name': 'Alice',
            'age': 30,
            'city': 'New York',
            'tags': ['developer', 'python']
        }
    @pytest.mark.asyncio
    @pytest.mark.skipif(not _has_xwsyntax, reason="exonware.xwsyntax required for serialize")
    async def test_convert_json_to_yaml(self, sample_data, tmp_path):
        """Test converting JSON to YAML using xwjson converter."""
        from exonware.xwdata import XWData
        from exonware.xwdata.operations.format_conversion import FormatConverter
        # Create data (use from_native in async context)
        data = XWData.from_native(sample_data)
        # Convert JSON to YAML
        converter = FormatConverter()
        json_serialized = await data.serialize('json')
        yaml_data = await converter.convert(
            json_serialized,
            'json',
            'yaml'
        )
        # Verify YAML format
        assert isinstance(yaml_data, str)
        assert 'name' in yaml_data.lower()
        assert 'Alice' in yaml_data or '"Alice"' in yaml_data
        assert 'age' in yaml_data.lower() or '30' in yaml_data
    @pytest.mark.asyncio
    @pytest.mark.skipif(not _has_xwsyntax, reason="exonware.xwsyntax required for save/load")
    async def test_convert_file_json_to_yaml(self, sample_data, tmp_path):
        """Test converting file from JSON to YAML."""
        from exonware.xwdata import XWData
        from exonware.xwdata.operations.format_conversion import FormatConverter
        # Create JSON file
        json_file = tmp_path / 'data.json'
        data = XWData.from_native(sample_data)
        await data.save(json_file, format='json')
        # Convert to YAML
        yaml_file = tmp_path / 'data.yaml'
        converter = FormatConverter()
        await converter.convert_file(json_file, yaml_file, target_format='yaml')
        # Verify YAML file exists and is valid
        assert yaml_file.exists()
        loaded = await XWData.load(yaml_file, format_hint='yaml')
        assert await loaded.get('name') == 'Alice'
    @pytest.mark.asyncio
    @pytest.mark.skipif(not _has_xwsyntax, reason="exonware.xwsyntax required for serialize")
    async def test_conversion_pipeline(self, sample_data):
        """Test multi-step conversion pipeline."""
        from exonware.xwdata import XWData
        from exonware.xwdata.operations.conversion_pipeline import ConversionPipeline
        # Create data
        data = XWData.from_native(sample_data)
        json_data = await data.serialize('json')
        # Execute pipeline: JSON -> YAML -> TOML
        pipeline = ConversionPipeline()
        steps = [
            ('yaml', {}),
            ('toml', {})
        ]
        result = await pipeline.execute(json_data, steps)
        # Verify result is TOML format (serialized string)
        assert isinstance(result, str)
        assert 'name' in result.lower() or 'Alice' in result
    @pytest.mark.asyncio
    @pytest.mark.skipif(not _has_xwsyntax, reason="exonware.xwsyntax required for serialize")
    async def test_format_validator(self, sample_data):
        """Test format validation."""
        from exonware.xwdata import XWData
        from exonware.xwdata.operations.format_validator import FormatValidator
        # Create data
        data = XWData.from_native(sample_data)
        json_data = await data.serialize('json')
        # Validate JSON (validator expects native data, not serialized)
        validator = FormatValidator()
        native_data = data.to_native()
        result = await validator.validate(native_data, 'json')
        assert result['valid'] is True
        assert len(result['errors']) == 0
        assert result['format'] == 'json'
    @pytest.mark.asyncio

    async def test_supports_conversion(self):
        """Test conversion support checking."""
        from exonware.xwdata.operations.format_conversion import FormatConverter
        converter = FormatConverter()
        # JSON to YAML should be supported
        assert converter.supports_conversion('json', 'yaml') is True
        # JSON to JSON (no conversion needed)
        assert converter.supports_conversion('json', 'json') is True
    @pytest.mark.asyncio

    async def test_get_conversion_path(self):
        """Test conversion path generation."""
        from exonware.xwdata.operations.format_conversion import FormatConverter
        converter = FormatConverter()
        # Should use xwjson as intermediate
        path = converter.get_conversion_path('json', 'yaml')
        assert 'xwjson' in path or 'json' in path
        assert path[0] == 'json'
        assert path[-1] == 'yaml'
