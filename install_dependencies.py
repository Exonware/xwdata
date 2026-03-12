#!/usr/bin/env python3
"""
#exonware/xwdata/install_dependencies.py
Install missing dependencies and update requirements files.
Company: eXonware.com
Author: eXonware Backend Team
Email: connect@exonware.com
Version: 0.1.0.1
Generation Date: 26-Jan-2025
"""

import subprocess
import sys
from pathlib import Path
# Required dependencies (xwdata cannot work without these)
REQUIRED_DEPS = [
    "exonware-xwsystem>=0.0.1",
    "exonware-xwnode>=0.0.1",
    "exonware-xwquery>=0.0.1",
    "exonware-xwjson>=0.0.1",  # Required for format conversion
    "bcrypt>=4.0.0",  # Required by xwsystem.security (must be compatible with Python version)
]
# Optional dependencies (for extended features)
OPTIONAL_DEPS = [
    "exonware-xwformats>=0.0.1",  # Extended format support
    "exonware-xwschema>=0.0.1",   # Schema validation (optional integration)
    "exonware-xwentity>=0.0.1",   # Entity serialization (optional integration)
    "exonware-xwstorage>=0.0.1",   # Storage integration (optional)
    "exonware-xwsyntax>=0.0.1",    # Grammar-based parsing (optional)
]
# Development dependencies
DEV_DEPS = [
    "pytest>=7.0.0",
    "pytest-cov>=4.0.0",
    "pytest-asyncio>=0.20.0",
    "black>=22.0.0",
    "isort>=5.10.0",
    "flake8>=4.0.0",
    "mypy>=0.950",
]


def install_package(package: str, optional: bool = False) -> bool:
    """Install a package using pip."""
    try:
        print(f"Installing {package}...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", package])
        print(f"✅ {package} installed successfully")
        return True
    except subprocess.CalledProcessError as e:
        if optional:
            print(f"⚠️  {package} installation failed (optional dependency)")
            return False
        else:
            print(f"❌ {package} installation failed (required dependency)")
            raise
    except Exception as e:
        print(f"❌ Error installing {package}: {e}")
        if not optional:
            raise
        return False


def update_requirements_txt():
    """Update requirements.txt with all dependencies."""
    requirements_path = Path(__file__).parent / "requirements.txt"
    # Read existing content
    existing_content = ""
    if requirements_path.exists():
        existing_content = requirements_path.read_text(encoding='utf-8')
    # Build new requirements content
    new_content = """# xwdata Requirements
# Company: eXonware.com
# Author: eXonware Backend Team
# Email: connect@exonware.com
# Version: 0.1.0.1
# Generation Date: 26-Jan-2025
#
# This file contains all dependencies needed for xwdata
# Compatible with Python 3.8+ for maximum compatibility
#
# Usage:
#   pip install -r requirements.txt
#   
# For Replit and other cloud IDEs:
#   Just add this file to your project root and dependencies will be auto-installed
# =============================================================================
# CORE DEPENDENCIES (REQUIRED)
# =============================================================================
# eXonware ecosystem dependencies (xwdata cannot work without these)
exonware-xwsystem>=0.0.1        # Core utilities, serialization, security
exonware-xwnode>=0.0.1           # Node structures and navigation
exonware-xwquery>=0.0.1          # Query engine for data navigation
exonware-xwjson>=0.0.1           # Universal JSON format (required for format conversion)
# =============================================================================
# OPTIONAL DEPENDENCIES (For Extended Features)
# =============================================================================
# Uncomment to enable optional features:
# exonware-xwformats>=0.0.1      # Extended format support (50+ formats)
# exonware-xwschema>=0.0.1        # Schema validation integration
# exonware-xwentity>=0.0.1        # Entity serialization integration
# exonware-xwstorage>=0.0.1       # Storage backend integration
# exonware-xwsyntax>=0.0.1       # Grammar-based parsing (SQL, GraphQL, etc.)
# =============================================================================
# DEVELOPMENT AND TESTING DEPENDENCIES
# =============================================================================
# Testing Framework
pytest>=7.0.0                       # Testing framework
pytest-cov>=4.0.0                   # Coverage reporting
pytest-asyncio>=0.20.0              # Async testing support
# Code Quality
black>=22.0.0                       # Code formatting
isort>=5.10.0                       # Import sorting
flake8>=4.0.0                       # Linting
# Type Checking
mypy>=0.950                          # Static type checking
# =============================================================================
# OPTIONAL PERFORMANCE ENHANCEMENTS
# =============================================================================
# Add optional performance dependencies here
# Example:
# orjson>=3.8.0                       # Ultra-fast JSON parsing (optional)
# =============================================================================
# COMPATIBILITY NOTES
# =============================================================================
#
# Python Version Compatibility:
# - Minimum: Python 3.8 (for maximum compatibility)
# - Recommended: Python 3.12+ for best performance
# - Tested: Python 3.8, 3.9, 3.10, 3.11, 3.12
#
# Platform Compatibility:
# - Windows: Full support
# - Linux: Full support  
# - macOS: Full support
#
# Cloud IDE Support:
# - Replit: ✅ Full support
# - GitHub Codespaces: ✅ Full support  
# - GitPod: ✅ Full support
# - Google Colab: ✅ Full support
# - Jupyter: ✅ Full support
#
# =============================================================================
# INSTALLATION VERIFICATION
# =============================================================================
#
# After installing requirements, verify with:
#   python -c "from exonware.xwdata import *; print('✅ xwdata loaded!')"
#
# Or run comprehensive verification:
#   python tests/verify_installation.py
#
# Expected output:
#   🎉 SUCCESS! exonware.xwdata is ready to use!
"""
    requirements_path.write_text(new_content, encoding='utf-8')
    print(f"✅ Updated {requirements_path}")


def update_pyproject_toml():
    """Update pyproject.toml with missing dependencies."""
    pyproject_path = Path(__file__).parent / "pyproject.toml"
    if not pyproject_path.exists():
        print("⚠️  pyproject.toml not found, skipping update")
        return
    content = pyproject_path.read_text(encoding='utf-8')
    # Check if xwjson is in dependencies
    if "exonware-xwjson" not in content:
        # Find the dependencies section and add xwjson
        if 'dependencies = [' in content:
            # Add xwjson after xwquery
            content = content.replace(
                '    "exonware-xwquery",\n]',
                '    "exonware-xwquery",\n    "exonware-xwjson",\n]'
            )
            print("✅ Added exonware-xwjson to pyproject.toml dependencies")
        else:
            print("⚠️  Could not find dependencies section in pyproject.toml")
    # Add optional dependencies to optional-dependencies.full
    if 'full = [' in content and "exonware-xwjson" not in content:
        # Add optional deps to full section
        full_section = """full = [
        # xwdata leverages xwsystem, xwnode, xwquery, and xwjson full capabilities
        "exonware-xwsystem[full]",
        "exonware-xwnode[full]",
        "exonware-xwquery[full]",
        "exonware-xwjson[full]",
        # Optional format and integration support
        "exonware-xwformats>=0.0.1",
        "exonware-xwschema>=0.0.1",
        "exonware-xwentity>=0.0.1",
        "exonware-xwstorage>=0.0.1",
        "exonware-xwsyntax>=0.0.1",
        # xwdata-specific dependencies
        "json5>=0.9.0",
        "pyyaml>=6.0.0",
        "toml>=0.10.0",
    ]"""
        # Replace existing full section
        import re
        pattern = r'full = \[.*?\]'
        if re.search(pattern, content, re.DOTALL):
            content = re.sub(pattern, full_section, content, flags=re.DOTALL)
            print("✅ Updated optional-dependencies.full in pyproject.toml")
    pyproject_path.write_text(content, encoding='utf-8')
    print(f"✅ Updated {pyproject_path}")


def main():
    """Main installation function."""
    print("=" * 70)
    print("XWData Dependency Installation Script")
    print("=" * 70)
    print()
    # Install required dependencies
    print("📦 Installing REQUIRED dependencies...")
    print("-" * 70)
    for dep in REQUIRED_DEPS:
        install_package(dep, optional=False)
    print()
    # Install optional dependencies (with error handling)
    print("📦 Installing OPTIONAL dependencies...")
    print("-" * 70)
    for dep in OPTIONAL_DEPS:
        install_package(dep, optional=True)
    print()
    # Install development dependencies
    print("📦 Installing DEVELOPMENT dependencies...")
    print("-" * 70)
    for dep in DEV_DEPS:
        install_package(dep, optional=True)
    print()
    # Update requirements files
    print("📝 Updating requirements files...")
    print("-" * 70)
    update_requirements_txt()
    update_pyproject_toml()
    print()
    # Verification
    print("🔍 Verifying installation...")
    print("-" * 70)
    try:
        # Verify bcrypt first (common compatibility issue)
        import bcrypt
        print(f"✅ bcrypt imported successfully (version: {bcrypt.__version__})")
        from exonware.xwdata import XWData
        print("✅ xwdata imported successfully")
        from exonware.xwjson import XWJSONConverter
        print("✅ xwjson imported successfully")
        from exonware.xwnode import XWNode
        print("✅ xwnode imported successfully")
        from exonware.xwquery import XWQuery
        print("✅ xwquery imported successfully")
        print()
        print("=" * 70)
        print("🎉 SUCCESS! All required dependencies are installed!")
        print("=" * 70)
    except ImportError as e:
        print(f"❌ Import verification failed: {e}")
        print("⚠️  Some dependencies may be missing. Check the errors above.")
        sys.exit(1)
if __name__ == "__main__":
    main()
