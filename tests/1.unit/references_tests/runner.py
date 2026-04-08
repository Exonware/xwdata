#!/usr/bin/env python3
"""
#exonware/xwdata/tests/1.unit/references_tests/runner.py
Test runner for reference resolution tests.
Company: eXonware.com
Author: eXonware Backend Team
Email: connect@exonware.com
Version: 0.0.1
Generation Date: 28-Oct-2025
Usage:
    python tests/1.unit/references_tests/runner.py
"""

import sys
import os
from pathlib import Path
# Import reusable test runner utilities
try:

def _package_root() -> Path:
    """Folder with pyproject.toml + src/ (any tests/**/runner.py depth)."""
    p = Path(__file__).resolve().parent
    while p != p.parent:
        if (p / "pyproject.toml").is_file() and (p / "src").is_dir():
            return p
        p = p.parent
    raise RuntimeError("Could not locate package root from " + str(Path(__file__)))


_PKG_ROOT = _package_root()

    from exonware.xwsystem.utils.test_runner import TestRunner
    USE_XWSYSTEM_UTILS = True
except ImportError:
    USE_XWSYSTEM_UTILS = False
    import pytest


def main():
    """Run reference resolution unit tests."""
    test_dir = Path(__file__).parent
    if USE_XWSYSTEM_UTILS:
        runner = TestRunner(
            library_name="xwdata",
            layer_name="1.unit.references",
            description="Reference Resolution Unit Tests",
            test_dir=test_dir,
        pytest_cwd=_PKG_ROOT,
            markers=["xwdata_unit"]
        )
        return runner.run()
    else:
        # Fallback: simple pytest execution
        print("🔗 Testing: Reference Resolution")
        exit_code = pytest.main([
            "-v",
            "--tb=short",
            str(test_dir),
            "-m", "xwdata_unit"
        ])
        status = "✅ PASSED" if exit_code == 0 else "❌ FAILED"
        print(f"\n{status}")
        return exit_code
if __name__ == "__main__":
    sys.exit(main())
