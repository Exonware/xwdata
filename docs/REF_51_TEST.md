# xwdata — Test Status and Coverage (REF_51_TEST)

**Last Updated:** 07-Feb-2026  
**Requirements source:** [REF_01_REQ.md](REF_01_REQ.md) sec. 8 (maintainability), [REF_22_PROJECT.md](REF_22_PROJECT.md)

Test status and coverage (output of GUIDE_51_TEST). Evidence: repo `tests/`, docs/logs/. Per REF_01_REQ: 4-layer tests and Five Priorities markers.

---

## Structure (from REF_01_REQ sec. 8)

- **4 layers:** `0.core` (xwdata_core), `1.unit` (xwdata_unit), `2.integration` (xwdata_integration), `3.advance` (xwdata_advance).
- **Five Priorities markers:** xwdata_security, xwdata_usability, xwdata_maintainability, xwdata_performance, xwdata_extensibility (see pytest.ini and test modules).
- **Runner:** `tests/runner.py` with Markdown output; `--core`, `--unit`, `--integration`, `--advance`. Optional filters: `--security`, `--performance` (subset of advance layer).

---

## Running tests

```bash
python tests/runner.py
python tests/runner.py --core
python tests/runner.py --unit
python tests/runner.py --integration
python tests/runner.py --advance
# Optional: python tests/runner.py --security   # security-tagged tests only
# Optional: python tests/runner.py --performance   # performance-tagged tests only
```

---

## Traceability

- **Requirements:** REF_01_REQ sec. 8 (maintainability, 4-layer tests, Five Priorities); REF_22_PROJECT FR-007.
- **Legacy:** Value from _archive (TEST_COVERAGE_REPORT, TEST_RESULTS_SUMMARY) in [logs/tests/TEST_20250126_XWDATA_COVERAGE.md](logs/tests/TEST_20250126_XWDATA_COVERAGE.md) and [logs/ARCHIVE_VALUE_CAPTURE_XWDATA.md](logs/ARCHIVE_VALUE_CAPTURE_XWDATA.md).

---

*Per GUIDE_00_MASTER and GUIDE_51_TEST.*
