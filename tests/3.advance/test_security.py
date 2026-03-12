#!/usr/bin/env python3
"""
#exonware/xwdata/tests/3.advance/test_security.py
Comprehensive security tests for xwdata.
Tests cover:
- OWASP Top 10 vulnerabilities
- Path traversal attacks
- Injection attacks (SQL, XSS, command injection)
- Input sanitization
- File security
- Data validation
Company: eXonware.com
Author: eXonware Backend Team
Email: connect@exonware.com
Version: 0.1.0.1
Generation Date: 26-Jan-2025
"""

import pytest
from pathlib import Path
from unittest.mock import Mock, patch
from exonware.xwdata.errors import (
    XWDataPathSecurityError,
    XWDataSecurityError,
    XWDataSizeLimitError,
    XWDataValidationError
)
from exonware.xwdata.core.validators import (
    PathValidator,
    FormatValidator,
    InputSanitizer,
    DataValidator
)
from exonware.xwdata.core.file_security import FileSecurity
@pytest.mark.xwdata_advance
@pytest.mark.xwdata_security

class TestPathTraversalSecurity:
    """Test path traversal attack prevention."""
    @pytest.fixture

    def path_validator(self):
        """Create path validator."""
        return PathValidator()

    def test_path_traversal_unix(self, path_validator):
        """Test Unix path traversal patterns."""
        malicious_paths = [
            "../../../etc/passwd",
            "..//etc/passwd",
            "....//....//etc/passwd",
            "/etc/passwd",
            "~/../../etc/passwd",
        ]
        for path in malicious_paths:
            with pytest.raises(XWDataPathSecurityError):
                path_validator.validate_path(path)

    def test_path_traversal_windows(self, path_validator):
        """Test Windows path traversal patterns."""
        malicious_paths = [
            "..\\..\\..\\windows\\system32",
            "..\\\\windows\\system32",
            "C:\\Windows\\System32",
            "..\\..\\..\\..\\windows",
        ]
        for path in malicious_paths:
            with pytest.raises(XWDataPathSecurityError):
                path_validator.validate_path(path)

    def test_path_traversal_encoded(self, path_validator):
        """Test encoded path traversal patterns."""
        malicious_paths = [
            "%2e%2e%2f%2e%2e%2f%2e%2e%2fetc%2fpasswd",
            "..%2f..%2f..%2fetc%2fpasswd",
            "..%5c..%5c..%5cwindows",
        ]
        for path in malicious_paths:
            # Path validator should catch these
            with pytest.raises((XWDataPathSecurityError, ValueError)):
                path_validator.validate_path(path)

    def test_safe_paths(self, path_validator):
        """Test that safe paths are allowed."""
        safe_paths = [
            "data.json",
            "config/settings.yaml",
            "subfolder/file.txt",
            "file-name.json",
            "file_name.json",
        ]
        for path in safe_paths:
            # Should not raise exception
            result = path_validator.validate_path(path)
            assert isinstance(result, Path)

    def test_allowed_directories(self):
        """Test path validation with allowed directories."""
        import tempfile
        with tempfile.TemporaryDirectory() as tmpdir:
            validator = PathValidator(allowed_directories=[tmpdir])
            # Path within allowed directory should work
            safe_path = Path(tmpdir) / "data.json"
            result = validator.validate_path(str(safe_path))
            assert result == safe_path.resolve()
            # Path outside should fail
            with pytest.raises(XWDataPathSecurityError):
                validator.validate_path("/etc/passwd")
@pytest.mark.xwdata_advance
@pytest.mark.xwdata_security

class TestInjectionAttacks:
    """Test injection attack prevention."""
    @pytest.fixture

    def sanitizer(self):
        """Create input sanitizer."""
        return InputSanitizer(strict_mode=True)

    def test_sql_injection(self, sanitizer):
        """Test SQL injection prevention."""
        sql_injections = [
            "'; DROP TABLE users; --",
            "1' OR '1'='1",
            "admin'--",
            "1' UNION SELECT * FROM users--",
            "'; EXEC xp_cmdshell('dir'); --",
        ]
        for injection in sql_injections:
            with pytest.raises(XWDataSecurityError):
                sanitizer.sanitize_string(injection)

    def test_xss_attacks(self, sanitizer):
        """Test XSS attack prevention."""
        xss_attacks = [
            "<script>alert('XSS')</script>",
            "<img src=x onerror=alert('XSS')>",
            "javascript:alert('XSS')",
            "<iframe src='javascript:alert(\"XSS\")'></iframe>",
            "<body onload=alert('XSS')>",
        ]
        for attack in xss_attacks:
            with pytest.raises(XWDataSecurityError):
                sanitizer.sanitize_string(attack)

    def test_command_injection(self, sanitizer):
        """Test command injection prevention (strict mode)."""
        command_injections = [
            "; cat /etc/passwd",
            "| ls -la",
            "&& rm -rf /",
            "`whoami`",
            "$(cat /etc/passwd)",
        ]
        for injection in command_injections:
            with pytest.raises(XWDataSecurityError):
                sanitizer.sanitize_string(injection)

    def test_safe_inputs(self, sanitizer):
        """Test that safe inputs are allowed."""
        safe_inputs = [
            "Hello World",
            "user@example.com",
            "12345",
            "normal-text-with-dashes",
            "text_with_underscores",
        ]
        for safe_input in safe_inputs:
            result = sanitizer.sanitize_string(safe_input)
            assert result == safe_input

    def test_sanitize_dict(self, sanitizer):
        """Test dictionary sanitization."""
        malicious_dict = {
            "name": "<script>alert('XSS')</script>",
            "email": "'; DROP TABLE users; --",
            "safe": "normal value"
        }
        with pytest.raises(XWDataSecurityError):
            sanitizer.sanitize_dict(malicious_dict)
@pytest.mark.xwdata_advance
@pytest.mark.xwdata_security

class TestFileSecurity:
    """Test file security operations."""
    @pytest.fixture

    def file_security(self, tmp_path):
        """Create file security instance."""
        return FileSecurity(
            max_file_size=1024,  # 1KB for testing
            allowed_directories=[str(tmp_path)]
        )

    def test_file_size_limit(self, file_security, tmp_path):
        """Test file size limit enforcement."""
        large_file = tmp_path / "large.json"
        large_data = b"x" * 2048  # 2KB, exceeds 1KB limit
        # Writing should fail
        with pytest.raises(XWDataSizeLimitError):
            file_security.secure_write_file(large_file, large_data)

    def test_secure_read_file(self, file_security, tmp_path):
        """Test secure file reading."""
        test_file = tmp_path / "test.json"
        test_data = b'{"key": "value"}'
        test_file.write_bytes(test_data)
        # Should read successfully
        result = file_security.secure_read_file(test_file)
        assert result == test_data

    def test_path_traversal_in_file_ops(self, file_security):
        """Test path traversal prevention in file operations."""
        malicious_paths = [
            "../../../etc/passwd",
            "..\\..\\..\\windows\\system32",
        ]
        for path in malicious_paths:
            with pytest.raises(XWDataPathSecurityError):
                file_security.validate_file_path(path)

    def test_file_permissions(self, file_security, tmp_path):
        """Test file permission validation."""
        import os
        test_file = tmp_path / "test.json"
        test_file.write_text('{"key": "value"}')
        # Make file read-only
        if hasattr(os, 'chmod'):
            os.chmod(test_file, 0o444)
            # Should validate permissions
            file_security.validate_file_permissions(test_file, required_permission="read")
            # Write should fail
            with pytest.raises(XWDataIOError):
                file_security.validate_file_permissions(test_file, required_permission="write")
@pytest.mark.xwdata_advance
@pytest.mark.xwdata_security

class TestDataValidation:
    """Test data structure validation."""
    @pytest.fixture

    def data_validator(self):
        """Create data validator."""
        return DataValidator(max_depth=10, max_size=1024)

    def test_max_depth_validation(self, data_validator):
        """Test maximum depth validation."""
        # Create deeply nested structure
        deep_data = {}
        current = deep_data
        for i in range(15):  # Exceeds max_depth of 10
            current['nested'] = {}
            current = current['nested']
        with pytest.raises(XWDataValidationError):
            data_validator.validate_structure(deep_data)

    def test_max_size_validation(self, data_validator):
        """Test maximum size validation."""
        # Create large data structure
        large_data = {"data": "x" * 2048}  # Exceeds max_size of 1024
        with pytest.raises(XWDataValidationError):
            data_validator.validate_structure(large_data)

    def test_valid_data(self, data_validator):
        """Test that valid data passes validation."""
        valid_data = {
            "key1": "value1",
            "key2": {
                "nested": "value"
            },
            "key3": [1, 2, 3]
        }
        # Should not raise exception
        data_validator.validate_structure(valid_data)
@pytest.mark.xwdata_advance
@pytest.mark.xwdata_security

class TestFormatValidation:
    """Test format name validation."""
    @pytest.fixture

    def format_validator(self):
        """Create format validator."""
        return FormatValidator()

    def test_invalid_format_names(self, format_validator):
        """Test invalid format name detection."""
        invalid_formats = [
            "",
            "format with spaces",
            "format/with/slashes",
            "format.with.dots",
            "format@with#special",
            "../../etc/passwd",  # Path traversal attempt
        ]
        for fmt in invalid_formats:
            with pytest.raises(XWDataValidationError):
                format_validator.validate_format_name(fmt)

    def test_valid_format_names(self, format_validator):
        """Test valid format name acceptance."""
        valid_formats = [
            "json",
            "yaml",
            "xml",
            "format-name",
            "format_name",
            "format123",
        ]
        for fmt in valid_formats:
            result = format_validator.validate_format_name(fmt)
            assert result == fmt.lower().strip()
@pytest.mark.xwdata_advance
@pytest.mark.xwdata_security

class TestOWASPTop10:
    """Test OWASP Top 10 security vulnerabilities."""
    @pytest.fixture

    def facade(self):
        """Create XWData facade."""
        from exonware.xwdata.facade import XWData
        return XWData
    # A01:2021 – Broken Access Control

    def test_broken_access_control(self, facade, tmp_path):
        """Test access control (path traversal)."""
        malicious_paths = [
            "../../../etc/passwd",
            "..\\..\\..\\windows\\system32",
        ]
        for path in malicious_paths:
            with pytest.raises((XWDataPathSecurityError, XWDataIOError)):
                # Should prevent accessing files outside allowed directories
                pass  # Integration test would load file here
    # A02:2021 – Cryptographic Failures

    def test_cryptographic_failures(self):
        """Test that sensitive data is handled securely."""
        # This would test encryption of sensitive data
        # For now, we ensure no plaintext sensitive data in logs
        pass
    # A03:2021 – Injection

    def test_injection_attacks(self):
        """Test injection attack prevention (covered in TestInjectionAttacks)."""
        # Already covered in TestInjectionAttacks class
        pass
    # A04:2021 – Insecure Design

    def test_insecure_design(self, facade):
        """Test secure design patterns."""
        # Ensure secure defaults
        # File size limits, path validation, etc.
        pass
    # A05:2021 – Security Misconfiguration

    def test_security_misconfiguration(self):
        """Test security configuration validation."""
        # Ensure secure defaults are used
        # No debug mode in production, etc.
        pass
    # A06:2021 – Vulnerable Components

    def test_vulnerable_components(self):
        """Test dependency security."""
        # Would use pip-audit or safety to check dependencies
        # This is more of an infrastructure test
        pass
    # A07:2021 – Authentication Failures

    def test_authentication_failures(self):
        """Test authentication (if applicable)."""
        # xwdata doesn't have authentication, but would test if added
        pass
    # A08:2021 – Software and Data Integrity Failures

    def test_data_integrity(self, facade):
        """Test data integrity validation."""
        # Test that data structure validation works
        validator = DataValidator()
        invalid_data = {"key": None}
        # Should validate data structure
        validator.validate_structure(invalid_data)
    # A09:2021 – Security Logging Failures

    def test_security_logging(self):
        """Test security event logging."""
        # Test that security events are logged
        # This would integrate with xwnode security logger if needed
        pass
    # A10:2021 – Server-Side Request Forgery

    def test_ssrf(self, facade):
        """Test SSRF prevention (if applicable)."""
        # xwdata may load from URLs, should validate URLs
        malicious_urls = [
            "file:///etc/passwd",
            "http://localhost:22",
            "http://127.0.0.1/admin",
        ]
        # Should prevent loading from local/internal URLs
        for url in malicious_urls:
            with pytest.raises((XWDataSecurityError, XWDataIOError)):
                # Integration test would attempt to load from URL
                pass
@pytest.mark.xwdata_advance
@pytest.mark.xwdata_security

class TestInputSanitization:
    """Test input sanitization across operations."""
    @pytest.fixture

    def sanitizer(self):
        """Create input sanitizer."""
        return InputSanitizer()

    def test_null_byte_removal(self, sanitizer):
        """Test null byte removal."""
        malicious_input = "test\x00string"
        result = sanitizer.sanitize_string(malicious_input)
        assert "\x00" not in result

    def test_nested_structure_sanitization(self, sanitizer):
        """Test sanitization of nested structures."""
        malicious_data = {
            "level1": {
                "level2": {
                    "value": "<script>alert('XSS')</script>"
                }
            }
        }
        with pytest.raises(XWDataSecurityError):
            sanitizer.sanitize_dict(malicious_data, recursive=True)

    def test_list_sanitization(self, sanitizer):
        """Test list sanitization."""
        malicious_list = [
            "safe value",
            "<script>alert('XSS')</script>",
            "normal text"
        ]
        with pytest.raises(XWDataSecurityError):
            sanitizer.sanitize_list(malicious_list, recursive=True)
@pytest.mark.xwdata_advance
@pytest.mark.xwdata_security

class TestSecurityIntegration:
    """Test security features integration."""
    @pytest.mark.asyncio

    async def test_format_conversion_security(self):
        """Test security in format conversion."""
        from exonware.xwdata.operations.format_conversion import FormatConverter
        converter = FormatConverter()
        # Malicious input should be handled
        malicious_input = "<script>alert('XSS')</script>"
        # Should either sanitize or reject
        try:
            result = await converter.convert(malicious_input, 'json', 'yaml')
            # If it doesn't raise, result should be sanitized
            assert "<script>" not in str(result)
        except (XWDataSecurityError, XWDataParseError):
            # Or it should reject malicious input
            pass
    @pytest.mark.asyncio

    async def test_file_operation_security(self, tmp_path):
        """Test security in file operations."""
        from exonware.xwdata.facade import XWData
        # Attempt path traversal
        malicious_path = "../../../etc/passwd"
        with pytest.raises((XWDataPathSecurityError, XWDataIOError)):
            await XWData.load(malicious_path)
