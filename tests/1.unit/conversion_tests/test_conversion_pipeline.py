#!/usr/bin/env python3
"""
#exonware/xwdata/tests/1.unit/conversion_tests/test_conversion_pipeline.py
Unit tests for ConversionPipeline.
Company: eXonware.com
Author: eXonware Backend Team
Email: connect@exonware.com
Version: 0.1.0.1
Generation Date: 26-Jan-2025
"""

import pytest
@pytest.mark.xwdata_unit

class TestConversionPipeline:
    """Unit tests for ConversionPipeline."""
    @pytest.fixture

    def pipeline(self):
        """Create ConversionPipeline instance."""
        from exonware.xwdata.operations.conversion_pipeline import ConversionPipeline
        return ConversionPipeline()
    @pytest.fixture

    def sample_json(self):
        """Sample JSON data."""
        return '{"name": "Alice", "age": 30}'
    @pytest.mark.asyncio

    async def test_execute_single_step(self, pipeline, sample_json):
        """Test single-step pipeline."""
        steps = [('yaml', {})]
        result = await pipeline.execute(sample_json, steps)
        assert isinstance(result, str)
        assert 'name' in result.lower()
    @pytest.mark.asyncio

    async def test_execute_multi_step(self, pipeline, sample_json):
        """Test multi-step pipeline."""
        steps = [
            ('yaml', {}),
            ('toml', {})
        ]
        result = await pipeline.execute(sample_json, steps)
        assert isinstance(result, str)
        # Should be in TOML format after pipeline
        assert 'name' in result.lower() or 'Alice' in result
    @pytest.mark.asyncio

    async def test_execute_file(self, pipeline, sample_json, tmp_path):
        """Test file pipeline execution."""
        # Create source file
        source_file = tmp_path / 'source.json'
        source_file.write_text(sample_json)
        # Execute pipeline
        steps = [('yaml', {})]
        target_file = await pipeline.execute_file(source_file, steps)
        assert target_file.exists()
        assert target_file.suffix == '.yaml'
    @pytest.mark.asyncio

    async def test_execute_empty_steps(self, pipeline, sample_json):
        """Test pipeline with empty steps (should raise error)."""
        with pytest.raises(Exception):  # Should raise XWDataError
            await pipeline.execute(sample_json, [])
