#!/usr/bin/env python3
"""
#exonware/xwdata/tests/0.core/test_core_baas_facade.py
Core tests for BaaS facade (optional BaaS features).
Company: eXonware.com
Author: eXonware Backend Team
Email: connect@exonware.com
Version: 0.1.0.1
Generation Date: 26-Jan-2025
"""

import pytest
from pathlib import Path
@pytest.mark.xwdata_core

class TestCoreBaaSFacade:
    """Core BaaS facade functionality tests."""
    @pytest.fixture

    def sample_data(self):
        """Sample data for tests."""
        return {
            'name': 'Alice',
            'age': 30,
            'city': 'New York'
        }
    @pytest.mark.asyncio

    async def test_baas_facade_convert_format(self, sample_data):
        """Test format conversion via BaaS facade."""
        from exonware.xwdata import XWData
        from exonware.xwdata.facades.baas import XWDataBaaSFacade
        facade = XWDataBaaSFacade()
        data = XWData.from_native(sample_data)
        # Convert JSON to YAML
        converted = await facade.convert_format(data, 'json', 'yaml')
        assert converted is not None
        assert await converted.get('name') == 'Alice'
    @pytest.mark.asyncio

    async def test_baas_facade_convert_file(self, sample_data, tmp_path):
        """Test file conversion via BaaS facade."""
        from exonware.xwdata import XWData
        from exonware.xwdata.facades.baas import XWDataBaaSFacade
        facade = XWDataBaaSFacade()
        data = XWData.from_native(sample_data)
        # Save as JSON
        json_file = tmp_path / 'data.json'
        await data.save(json_file, format='json')
        # Convert to YAML
        yaml_file = tmp_path / 'data.yaml'
        converted = await facade.convert_file(json_file, yaml_file, target_format='yaml')
        assert converted is not None
        assert yaml_file.exists()
    @pytest.mark.asyncio

    async def test_baas_facade_validate_format(self, sample_data):
        """Test format validation via BaaS facade."""
        from exonware.xwdata import XWData
        from exonware.xwdata.facades.baas import XWDataBaaSFacade
        facade = XWDataBaaSFacade()
        data = XWData.from_native(sample_data)
        # Validate JSON format
        result = await facade.validate_format(data, 'json')
        assert result['valid'] is True
        assert result['format'] == 'json'
    @pytest.mark.asyncio

    async def test_baas_facade_batch_convert(self, sample_data):
        """Test batch conversion via BaaS facade."""
        from exonware.xwdata import XWData
        from exonware.xwdata.facades.baas import XWDataBaaSFacade
        facade = XWDataBaaSFacade()
        data1 = XWData.from_native(sample_data)
        data2 = XWData.from_native({'name': 'Bob', 'age': 25})
        # Batch convert
        items = [
            (data1, 'json', 'yaml'),
            (data2, 'json', 'yaml')
        ]
        results = await facade.batch_convert(items)
        assert len(results) == 2
        assert results[0] is not None
        assert results[1] is not None
