# Change: bcrypt/PyO3 compatibility workaround (docs)

**Date:** 2025-01-26  
**Source:** _archive/FIX_BCRYPT_ISSUE.md, _archive/README_BCRYPT_ISSUE.md (value moved 07-Feb-2026)

---

## Issue

With tests run *with* coverage, some environments see:

`ImportError: PyO3 modules compiled for CPython 3.8 or older may only be initialized once per interpreter process` (bcrypt, used by xwsystem).

Cause: bcrypt wheel built for a different Python version than the current interpreter.

## Workaround

- **Recommended:** Run tests without coverage: `python -m pytest tests/ -v`. Tests pass 100% without coverage.
- **Optional:** Reinstall bcrypt for current Python: `pip install --force-reinstall bcrypt`; or make bcrypt optional in xwsystem if not needed for xwdata-only runs.

Usage note: [GUIDE_01_USAGE.md](../GUIDE_01_USAGE.md) sec.  Troubleshooting.

---

*Per GUIDE_41_DOCS.*
