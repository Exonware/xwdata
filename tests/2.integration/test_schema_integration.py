#!/usr/bin/env python3
"""
#exonware/xwdata/tests/2.integration/test_schema_integration.py
Integration tests for schema integration (optional - requires xwschema).
Company: eXonware.com
Author: eXonware Backend Team
Email: connect@exonware.com
Version: 0.1.0.1
Generation Date: 26-Jan-2025
"""

import pytest
@pytest.mark.xwdata_integration

class TestSchemaIntegration:
    """Integration tests for schema integration."""
    @pytest.fixture

    def sample_data(self):
        """Sample data for schema tests."""
        return {
            'name': 'Alice',
            'age': 30,
            'email': 'alice@example.com'
        }
    @pytest.mark.asyncio

    async def test_schema_validator_interface(self, sample_data):
        """Test schema validator interface (mocked)."""
        pytest.importorskip("exonware.xwdata.integrations.schema")
        from exonware.xwdata import XWData
        from exonware.xwdata.integrations.schema import SchemaValidator
        validator = SchemaValidator()
        data = XWData(sample_data)
        assert validator is not None
    @pytest.mark.asyncio

    async def test_schema_mapper(self):
        """Test schema format mapping."""
        from exonware.xwdata.integrations.schema import SchemaMapper
        mapper = SchemaMapper()
        # Test format to schema mapping
        json_schema = mapper.map_format_to_schema('json', 'json_schema')
        assert json_schema == 'json_schema'
        yaml_schema = mapper.map_format_to_schema('yaml', 'json_schema')
        assert yaml_schema == 'json_schema'
        avro_schema = mapper.map_format_to_schema('avro', 'avro_schema')
        assert avro_schema == 'avro_schema'
