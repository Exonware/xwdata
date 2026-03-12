"""
Core functionality tests for xwdata
Company: eXonware.com
Author: eXonware Backend Team
Email: connect@exonware.com
Version: 0.0.1
Generation Date: 26-Oct-2025
"""
import pytest
import exonware.xwdata


class TestCore:
    """Test core functionality."""
    def test_import(self):
        """Test that the library can be imported."""
        import exonware.xwdata
        assert True

    def test_convenience_import(self):
        """Test that the convenience import works."""
        import xdata
        assert True

    def test_version_info(self):
        """Test that version information is available."""
        assert hasattr(exonware.xwdata, '__version__')
        assert hasattr(exonware.xwdata, '__author__')
        assert hasattr(exonware.xwdata, '__email__')
        assert hasattr(exonware.xwdata, '__company__')
        # Verify values are strings
        assert isinstance(exonware.xwdata.__version__, str)
        assert isinstance(exonware.xwdata.__author__, str)
        assert isinstance(exonware.xwdata.__email__, str)
        assert isinstance(exonware.xwdata.__company__, str)
    def test_sample_functionality(self, sample_data):
        """Sample test using fixture data."""
        # Replace this with actual tests for your library
        assert sample_data["test_data"] == "sample"
        assert len(sample_data["numbers"]) == 5
        assert sample_data["nested"]["key"] == "value"
