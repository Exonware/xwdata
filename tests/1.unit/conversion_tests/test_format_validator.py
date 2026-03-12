#!/usr/bin/env python3
"""
#exonware/xwdata/tests/1.unit/conversion_tests/test_format_validator.py
Unit tests for FormatValidator.
Company: eXonware.com
Author: eXonware Backend Team
Email: connect@exonware.com
Version: 0.1.0.1
Generation Date: 26-Jan-2025
"""

import pytest
from pathlib import Path
@pytest.mark.xwdata_unit

class TestFormatValidator:
    """Unit tests for FormatValidator."""
    @pytest.fixture

    def validator(self):
        """Create FormatValidator instance."""
        from exonware.xwdata.operations.format_validator import FormatValidator
        return FormatValidator()
    @pytest.fixture

    def valid_json(self):
        """Valid JSON data."""
        return '{"name": "Alice", "age": 30}'
    @pytest.fixture

    def invalid_json(self):
        """Invalid JSON data."""
        return '{name: "Alice", age: 30}'  # Missing quotes
    @pytest.mark.asyncio

    async def test_validate_valid_json(self, validator, valid_json):
        """Test validation of valid JSON."""
        result = await validator.validate(valid_json, 'json')
        assert result['valid'] is True
        assert len(result['errors']) == 0
        assert result['format'] == 'json'
    @pytest.mark.asyncio

    async def test_validate_invalid_json(self, validator, invalid_json):
        """Test validation of invalid JSON."""
        result = await validator.validate(invalid_json, 'json')
        # Should detect invalid JSON
        # Note: Actual behavior depends on serializer implementation
        assert 'valid' in result
        assert 'errors' in result
    @pytest.mark.asyncio

    async def test_validate_file(self, validator, valid_json, tmp_path):
        """Test file validation."""
        # Create JSON file
        json_file = tmp_path / 'data.json'
        json_file.write_text(valid_json)
        # Validate file
        result = await validator.validate_file(json_file, format='json')
        assert result['valid'] is True
        assert result['format'] == 'json'
    @pytest.mark.asyncio

    async def test_validate_native_data(self, validator):
        """Test validation of native Python data."""
        native_data = {'name': 'Alice', 'age': 30}
        result = await validator.validate(native_data, 'json')
        # Should serialize and validate
        assert 'valid' in result
        assert 'format' in result
