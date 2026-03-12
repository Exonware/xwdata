#!/usr/bin/env python3
"""
#exonware/xwdata/scripts/check_coverage.py
Check test coverage for xwdata.
Company: eXonware.com
Author: eXonware Backend Team
Email: connect@exonware.com
Version: 0.1.0.1
Generation Date: 26-Jan-2025
"""

import subprocess
import sys
from pathlib import Path


def main():
    """Run coverage analysis for xwdata."""
    root_dir = Path(__file__).parent.parent
    print("=" * 60)
    print("XWData Test Coverage Analysis")
    print("=" * 60)
    # Run pytest with coverage
    cmd = [
        sys.executable, "-m", "pytest",
        "tests/",
        "--cov=exonware.xwdata",
        "--cov-report=term-missing",
        "--cov-report=html:htmlcov",
        "-v",
        "--tb=short"
    ]
    print(f"\nRunning: {' '.join(cmd)}\n")
    result = subprocess.run(cmd, cwd=root_dir)
    if result.returncode == 0:
        print("\n" + "=" * 60)
        print("Coverage report generated in htmlcov/index.html")
        print("=" * 60)
        return 0
    else:
        print("\n" + "=" * 60)
        print("Coverage analysis completed with some test failures")
        print("Check htmlcov/index.html for detailed coverage report")
        print("=" * 60)
        return 1
if __name__ == "__main__":
    sys.exit(main())
