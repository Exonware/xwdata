# Test coverage summary — xwdata (historical)

**Source:** _archive/TEST_COVERAGE_REPORT.md, _archive/TEST_RESULTS_SUMMARY.md  
**Date:** 26-Jan-2025  
**Captured:** 07-Feb-2026 (value moved from _archive per GUIDE_41_DOCS)

---

## Summary

BaaS multi-format storage test structure is GUIDE_TEST compliant. Coverage by feature:

| Feature | Location | Status |
|---------|----------|--------|
| Format conversion (FormatConverter) | tests/0.core, tests/1.unit/conversion_tests | Complete |
| Conversion pipeline | test_core_format_conversion, test_conversion_pipeline, test_format_conversion_comprehensive | Complete |
| Format validator | test_core_format_conversion, test_format_validator | Complete |
| BaaS facade (XWDataBaaSFacade) | test_core_baas_facade | Complete |
| Storage integration (optional) | test_storage_integration | Interface tests complete |
| Schema integration (optional) | test_schema_integration | Interface tests complete |
| Entity integration (optional) | test_entity_integration | Interface tests complete |

Markers: `@pytest.mark.xwdata_core`, `@pytest.mark.xwdata_unit`, `@pytest.mark.xwdata_integration`. Async tests use `@pytest.mark.asyncio`. Current layer structure and runner: see [REF_51_TEST](../../REF_51_TEST.md).

---

*Legacy reports: value preserved here; original files removed from _archive.*
