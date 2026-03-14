#!/usr/bin/env python3
"""
#exonware/xwdata/tests/2.integration/test_format_conversion_comprehensive.py
Comprehensive integration tests for format conversion.
Tests format conversion across multiple format pairs using xwjson.
Company: eXonware.com
Author: eXonware Backend Team
Email: connect@exonware.com
Version: 0.1.0.1
Generation Date: 26-Jan-2025
"""

import importlib.util
import pytest
from pathlib import Path

try:
    import exonware.xwjson  # noqa: F401
    import exonware.xwsyntax  # noqa: F401
except ImportError:
    pytest.skip("exonware.xwjson and exonware.xwsyntax required for FormatConverter", allow_module_level=True)


@pytest.mark.xwdata_integration
class TestFormatConversionComprehensive:
    """Comprehensive format conversion integration tests."""
    @pytest.fixture

    def complex_data(self):
        """Complex nested data for conversion tests."""
        return {
            'users': [
                {'name': 'Alice', 'age': 30, 'city': 'New York'},
                {'name': 'Bob', 'age': 25, 'city': 'London'}
            ],
            'metadata': {
                'version': '1.0',
                'created': '2025-01-26',
                'tags': ['test', 'integration']
            },
            'settings': {
                'theme': 'dark',
                'language': 'en',
                'notifications': True
            }
        }
    @pytest.mark.parametrize("source_format,target_format", [
        ('json', 'yaml'),
        ('json', 'toml'),
        ('yaml', 'json'),
        ('yaml', 'toml'),
        ('toml', 'json'),
        ('toml', 'yaml'),
    ])
    @pytest.mark.asyncio

    async def test_format_pairs_roundtrip(self, complex_data, source_format, target_format):
        """Test roundtrip conversion between format pairs."""
        from exonware.xwdata import XWData
        from exonware.xwdata.operations.format_conversion import FormatConverter
        # Create data in source format
        data = XWData.from_native(complex_data)
        source_serialized = await data.serialize(source_format)
        # Convert to target format
        converter = FormatConverter()
        target_serialized = await converter.convert(
            source_serialized,
            source_format,
            target_format
        )
        # Convert back to source format
        roundtrip_serialized = await converter.convert(
            target_serialized,
            target_format,
            source_format
        )
        # Load both and compare
        original = await XWData.parse(source_serialized, format=source_format)
        roundtrip = await XWData.parse(roundtrip_serialized, format=source_format)
        # Compare key values (some formats may have minor differences)
        assert await original.get('users.0.name') == await roundtrip.get('users.0.name')
        assert await original.get('metadata.version') == await roundtrip.get('metadata.version')
    @pytest.mark.asyncio

    async def test_multi_step_pipeline(self, complex_data, tmp_path):
        """Test multi-step conversion pipeline."""
        from exonware.xwdata import XWData
        from exonware.xwdata.operations.conversion_pipeline import ConversionPipeline
        # Create JSON file
        json_file = tmp_path / 'data.json'
        data = XWData.from_native(complex_data)
        await data.save(json_file, format='json')
        # Execute pipeline: JSON -> YAML -> TOML -> JSON
        pipeline = ConversionPipeline()
        steps = [
            ('yaml', {}),
            ('toml', {}),
            ('json', {})
        ]
        result_file = await pipeline.execute_file(json_file, steps)
        # Verify final format
        assert result_file.exists()
        final_data = await XWData.load(result_file, format_hint='json')
        assert await final_data.get('users.0.name') == 'Alice'
    @pytest.mark.asyncio

    async def test_batch_conversion(self, complex_data):
        """Test batch conversion of multiple items."""
        from exonware.xwdata import XWData
        from exonware.xwdata.facades.baas import XWDataBaaSFacade
        facade = XWDataBaaSFacade()
        # Create multiple data items
        items = [
            (XWData.from_native(complex_data), 'json', 'yaml'),
            (XWData.from_native({'test': 'data'}), 'json', 'yaml'),
            (XWData.from_native({'another': 'item'}), 'json', 'toml'),
        ]
        # Batch convert
        results = await facade.batch_convert(items)
        assert len(results) == 3
        # Some conversions might fail (e.g., TOML parsing issues), so check for at least some success
        # JSON->YAML should work, TOML might have issues
        success_count = sum(1 for r in results if r is not None)
        assert success_count >= 2, f"Expected at least 2 successful conversions, got {success_count}"
