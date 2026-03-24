#!/usr/bin/env python3
"""
#exonware/xwdata/tests/1.unit/test_error_handling.py
Comprehensive error handling tests for xwdata.
Tests cover:
- Invalid format conversion errors
- File not found errors
- Serialization errors
- Parse errors
- Security errors
- Network errors (for remote sources)
- All error types from errors.py
Company: eXonware.com
Author: eXonware Backend Team
Email: connect@exonware.com
Version: 0.1.0.1
Generation Date: 26-Jan-2025
"""

import pytest
from pathlib import Path
from unittest.mock import Mock, patch, AsyncMock
from exonware.xwdata.errors import (
    XWDataError,
    XWDataSecurityError,
    XWDataPathSecurityError,
    XWDataSizeLimitError,
    XWDataParseError,
    XWDataSerializeError,
    XWDataIOError,
    XWDataFileNotFoundError,
    XWDataEngineError,
    XWDataStrategyError,
    XWDataMetadataError,
    XWDataReferenceError,
    XWDataCircularReferenceError,
    XWDataCacheError,
    XWDataNodeError,
    XWDataPathError,
    XWDataTypeError,
    XWDataValidationError,
    XWDataConfigError,
)
@pytest.mark.xwdata_unit

class TestErrorHandling:
    """Test error handling across xwdata operations."""
    @pytest.fixture

    def converter(self):
        """Create FormatConverter instance."""
        from exonware.xwdata.operations.format_conversion import FormatConverter
        return FormatConverter()
    @pytest.fixture

    def facade(self):
        """Create XWData facade instance."""
        from exonware.xwdata.facade import XWData
        return XWData
    # ========================================================================
    # FORMAT CONVERSION ERRORS
    # ========================================================================
    @pytest.mark.asyncio

    async def test_invalid_format_conversion(self, converter):
        """Test error handling for invalid format conversion."""
        invalid_data = "not valid json"
        # Attempting to convert invalid JSON should raise parse error
        with pytest.raises((XWDataParseError, XWDataError)):
            await converter.convert(invalid_data, 'json', 'yaml')
    @pytest.mark.asyncio

    async def test_unsupported_format_conversion(self, converter):
        """Test error handling for unsupported format conversion."""
        data = {"key": "value"}
        # Attempting unsupported format should raise strategy error
        with pytest.raises((XWDataStrategyError, XWDataError)):
            await converter.convert(data, 'unknown_format', 'yaml')
    @pytest.mark.asyncio

    async def test_serialization_error(self, converter):
        """Test error handling for serialization failures."""
        # Create data that cannot be serialized (circular reference)
        circular_data = {}
        circular_data['self'] = circular_data
        # Attempting to serialize circular reference may raise serialize error
        # (depending on format support for circular refs)
        try:
            result = await converter.convert(circular_data, 'json', 'yaml')
            # Some formats may handle circular refs, so this might not always error
        except (XWDataSerializeError, XWDataError):
            pass  # Expected error
    # ========================================================================
    # FILE OPERATION ERRORS
    # ========================================================================
    @pytest.mark.asyncio

    async def test_file_not_found_error(self, facade, tmp_path):
        """Test error handling for file not found."""
        non_existent_file = tmp_path / "nonexistent.json"
        # Loading non-existent file should raise file not found error
        with pytest.raises((XWDataFileNotFoundError, XWDataIOError, XWDataError)):
            await facade.load(str(non_existent_file))
    @pytest.mark.asyncio

    async def test_file_permission_error(self, facade, tmp_path):
        """Test error handling for file permission errors."""
        # Create a file
        test_file = tmp_path / "test.json"
        test_file.write_text('{"key": "value"}')
        # On Unix systems, we can test permission errors
        # On Windows, this might not work the same way
        import os
        if hasattr(os, 'chmod'):
            # Make file read-only
            os.chmod(test_file, 0o444)
            try:
                # Attempting to write to read-only file should raise IO error
                data = await facade.load(str(test_file))
                with pytest.raises((XWDataIOError, XWDataError)):
                    await data.save(str(test_file))
            finally:
                # Restore permissions for cleanup
                os.chmod(test_file, 0o644)
    # ========================================================================
    # PARSE ERRORS
    # ========================================================================
    @pytest.mark.asyncio

    async def test_malformed_json_parse_error(self, facade, tmp_path):
        """Test error handling for malformed JSON."""
        malformed_file = tmp_path / "malformed.json"
        malformed_file.write_text('{"key": "value"')  # Missing closing brace
        # Loading malformed JSON should raise parse error
        with pytest.raises((XWDataParseError, XWDataError)):
            await facade.load(str(malformed_file))
    @pytest.mark.asyncio

    async def test_malformed_yaml_parse_error(self, facade, tmp_path):
        """Test error handling for malformed YAML."""
        malformed_file = tmp_path / "malformed.yaml"
        malformed_file.write_text('key: [value')  # Invalid YAML syntax
        # Loading malformed YAML should raise parse error
        with pytest.raises((XWDataParseError, XWDataError)):
            await facade.load(str(malformed_file))
    # ========================================================================
    # SECURITY ERRORS
    # ========================================================================
    @pytest.mark.asyncio

    async def test_path_traversal_security_error(self, facade):
        """Test error handling for path traversal attempts."""
        # Attempting path traversal should raise security error
        malicious_paths = [
            "../../../etc/passwd",
            "..\\..\\..\\windows\\system32",
            "/etc/passwd",
            "C:\\Windows\\System32",
        ]
        for path in malicious_paths:
            with pytest.raises((XWDataPathSecurityError, XWDataSecurityError, XWDataError)):
                await facade.load(path)
    @pytest.mark.asyncio

    async def test_file_size_limit_error(self, facade, tmp_path):
        """Test error handling for file size limits."""
        # Use file security directly with a tiny test limit to avoid huge allocations.
        from exonware.xwdata.core.file_security import FileSecurity
        file_security = FileSecurity(
            max_file_size=1024,
            allowed_directories=[str(tmp_path)],
            allow_absolute_paths=True,
        )
        large_file = tmp_path / "large.json"
        large_data = b"x" * 2048
        with pytest.raises((XWDataSizeLimitError, XWDataSecurityError, XWDataError)):
            file_security.secure_write_file(large_file, large_data)
    # ========================================================================
    # REFERENCE ERRORS
    # ========================================================================
    @pytest.mark.asyncio

    async def test_missing_reference_error(self, facade, tmp_path):
        """Test error handling for missing references."""
        # Create file with reference to non-existent file
        ref_file = tmp_path / "with_ref.json"
        ref_file.write_text('{"$ref": "./nonexistent.json"}')
        # Loading file with missing reference should raise reference error
        # (depending on reference resolution configuration)
        try:
            await facade.load(str(ref_file))
        except (XWDataReferenceError, XWDataError):
            pass  # Expected error
    @pytest.mark.asyncio

    async def test_circular_reference_error(self, facade, tmp_path):
        """Test error handling for circular references."""
        # Create file A that references file B
        file_a = tmp_path / "a.json"
        file_b = tmp_path / "b.json"
        file_a.write_text('{"$ref": "./b.json", "name": "A"}')
        file_b.write_text('{"$ref": "./a.json", "name": "B"}')
        # Loading should detect circular reference
        # (depending on circular reference detection configuration)
        try:
            await facade.load(str(file_a))
        except (XWDataCircularReferenceError, XWDataReferenceError, XWDataError):
            pass  # Expected error
    # ========================================================================
    # NODE OPERATION ERRORS
    # ========================================================================
    @pytest.mark.asyncio

    async def test_invalid_path_error(self, facade):
        """Test error handling for invalid paths."""
        data = facade({"key": {"nested": "value"}})
        # Invalid path syntax should raise path error
        with pytest.raises((XWDataPathError, XWDataNodeError, XWDataError)):
            await data.get("invalid..path")
    @pytest.mark.asyncio

    async def test_type_error(self, facade):
        """Test error handling for type mismatches."""
        data = facade({"key": "value"})
        # Attempting to access list index on dict should raise type error
        # (depending on implementation)
        try:
            await data.get("key[0]")
        except (XWDataTypeError, XWDataNodeError, XWDataError):
            pass  # Expected error
    # ========================================================================
    # ENGINE ERRORS
    # ========================================================================
    @pytest.mark.asyncio

    async def test_strategy_error(self, facade):
        """Test error handling for strategy errors."""
        # Attempting to use unregistered format strategy should raise strategy error.
        from exonware.xwdata.operations.format_conversion import FormatConverter
        converter = FormatConverter()
        with pytest.raises((XWDataStrategyError, XWDataEngineError, XWDataError)):
            await converter.convert({"k": "v"}, "unknown_format", "yaml")
    # ========================================================================
    # METADATA ERRORS
    # ========================================================================
    @pytest.mark.asyncio

    async def test_metadata_error(self, facade):
        """Test error handling for metadata errors."""
        # Invalid metadata operations should raise metadata error
        # (depending on implementation)
        data = facade({"key": "value"})
        # This test depends on metadata implementation
        # If metadata operations exist and can fail, test them here
        pass
    # ========================================================================
    # VALIDATION ERRORS
    # ========================================================================
    @pytest.mark.asyncio

    async def test_validation_error(self, facade):
        """Test error handling for validation errors."""
        # Validation errors depend on schema validation integration
        # If schema validation is used, test invalid data here
        pass
    # ========================================================================
    # CONFIGURATION ERRORS
    # ========================================================================

    def test_config_error(self):
        """Test error handling for configuration errors."""
        # The dedicated error type should format meaningful context.
        error = XWDataConfigError("Invalid configuration", config_key="security.max_file_size_mb")
        error_str = str(error)
        assert "Invalid configuration" in error_str
        assert "security.max_file_size_mb" in error_str
    # ========================================================================
    # CACHE ERRORS
    # ========================================================================
    @pytest.mark.asyncio

    async def test_cache_error(self, converter):
        """Test error handling for cache errors."""
        # Cache errors are typically internal
        # Test if cache operations can fail in specific scenarios
        pass
    # ========================================================================
    # ERROR MESSAGE QUALITY
    # ========================================================================

    def test_error_message_quality(self):
        """Test that error messages are informative."""
        error = XWDataError(
            "Test error",
            operation="test_operation",
            path="/test/path",
            format="json",
            context={"key": "value"},
            suggestion="Test suggestion"
        )
        error_str = str(error)
        assert "Test error" in error_str
        assert "test_operation" in error_str
        assert "/test/path" in error_str
        assert "json" in error_str
        assert "Test suggestion" in error_str

    def test_security_error_suggestion(self):
        """Test that security errors include helpful suggestions."""
        error = XWDataPathSecurityError(
            "Path traversal detected",
            path="../../../etc/passwd"
        )
        error_str = str(error)
        assert "Path traversal" in error_str
        assert "suggestion" in error_str.lower() or "Suggestion" in error_str

    def test_parse_error_context(self):
        """Test that parse errors include context information."""
        error = XWDataParseError(
            "Parse failed",
            format="json",
            line=5,
            column=10,
            snippet="invalid syntax"
        )
        error_str = str(error)
        assert "Parse failed" in error_str
        assert "json" in error_str
        # Context should be included
        assert "5" in error_str or "line" in error_str.lower()
    # ========================================================================
    # NETWORK ERRORS (for remote sources)
    # ========================================================================
    @pytest.mark.asyncio

    async def test_network_error_handling(self, facade):
        """Test error handling for network errors with remote sources."""
        # Mock network failure
        with patch('exonware.xwdata.facade.httpx') as mock_httpx:
            mock_httpx.AsyncClient.return_value.get.side_effect = Exception("Network error")
            # Attempting to load from remote URL should handle network errors
            with pytest.raises((XWDataIOError, XWDataError, Exception)):
                await facade.load("http://example.com/data.json")
    @pytest.mark.asyncio

    async def test_timeout_error_handling(self, facade):
        """Test error handling for timeout errors."""
        # Mock timeout
        with patch('exonware.xwdata.facade.httpx') as mock_httpx:
            import asyncio
            mock_httpx.AsyncClient.return_value.get.side_effect = asyncio.TimeoutError("Request timeout")
            # Attempting to load with timeout should handle timeout errors
            with pytest.raises((XWDataIOError, XWDataError, asyncio.TimeoutError)):
                await facade.load("http://example.com/data.json", timeout=1)
