#!/usr/bin/env python3
"""
#exonware/xwdata/tests/3.advance/test_performance_conversion.py
Performance benchmarks for format conversion.
Company: eXonware.com
Author: eXonware Backend Team
Email: connect@exonware.com
Version: 0.1.0.1
Generation Date: 26-Jan-2025
"""

import pytest
import time
from pathlib import Path
@pytest.mark.xwdata_advance
@pytest.mark.xwdata_performance

class TestFormatConversionPerformance:
    """Performance benchmarks for format conversion."""
    @pytest.fixture

    def converter(self):
        """Create FormatConverter instance."""
        from exonware.xwdata.operations.format_conversion import FormatConverter
        return FormatConverter()
    @pytest.fixture

    def large_data(self):
        """Create large dataset for performance testing."""
        return {
            'items': [
                {
                    'id': i,
                    'name': f'Item {i}',
                    'description': f'Description for item {i}',
                    'tags': [f'tag{j}' for j in range(10)],
                    'metadata': {f'key{k}': f'value{k}' for k in range(5)}
                }
                for i in range(1000)
            ]
        }
    @pytest.mark.asyncio

    async def test_convert_performance_json_to_yaml(self, converter, large_data):
        """Benchmark JSON to YAML conversion performance."""
        start_time = time.time()
        result = await converter.convert(large_data, 'json', 'yaml')
        elapsed = time.time() - start_time
        assert isinstance(result, str)
        assert elapsed < 5.0, f"Conversion took {elapsed:.2f}s, expected < 5.0s"
    @pytest.mark.asyncio

    async def test_convert_performance_caching(self, converter, large_data):
        """Benchmark conversion caching performance."""
        # First conversion (cache miss)
        start1 = time.time()
        result1 = await converter.convert(large_data, 'json', 'yaml')
        elapsed1 = time.time() - start1
        # Second conversion (cache hit - should be faster)
        start2 = time.time()
        result2 = await converter.convert(large_data, 'json', 'yaml')
        elapsed2 = time.time() - start2
        assert result1 == result2
        # Cache hit should be significantly faster (at least 2x)
        assert elapsed2 < elapsed1, f"Cache hit ({elapsed2:.3f}s) should be faster than cache miss ({elapsed1:.3f}s)"
    @pytest.mark.asyncio

    async def test_batch_convert_performance(self, converter):
        """Benchmark batch conversion performance."""
        items = [
            ({'id': i, 'name': f'Item {i}'}, 'json', 'yaml')
            for i in range(100)
        ]
        start_time = time.time()
        results = []
        for data, source, target in items:
            result = await converter.convert(data, source, target)
            results.append(result)
        elapsed = time.time() - start_time
        assert len(results) == 100
        assert elapsed < 10.0, f"Batch conversion took {elapsed:.2f}s, expected < 10.0s"
    @pytest.mark.asyncio

    async def test_pipeline_performance(self, converter):
        """Benchmark conversion pipeline performance."""
        from exonware.xwdata.operations.conversion_pipeline import ConversionPipeline
        pipeline = ConversionPipeline(converter)
        data = {'test': 'data', 'items': list(range(1000))}
        json_data = str(data).replace("'", '"')  # Simple JSON-like string
        steps = [
            ('yaml', {}),
            ('toml', {}),
            ('json', {})
        ]
        start_time = time.time()
        result = await pipeline.execute(json_data, steps)
        elapsed = time.time() - start_time
        assert result is not None
        assert elapsed < 5.0, f"Pipeline took {elapsed:.2f}s, expected < 5.0s"
    @pytest.mark.asyncio

    async def test_file_conversion_performance(self, converter, large_data, tmp_path):
        """Benchmark file conversion performance."""
        # Create source file
        source_file = tmp_path / 'source.json'
        import json
        source_file.write_text(json.dumps(large_data))
        target_file = tmp_path / 'target.yaml'
        start_time = time.time()
        await converter.convert_file(source_file, target_file, target_format='yaml')
        elapsed = time.time() - start_time
        assert target_file.exists()
        assert elapsed < 5.0, f"File conversion took {elapsed:.2f}s, expected < 5.0s"
