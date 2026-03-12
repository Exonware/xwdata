# Archive value capture — xwdata

**Date:** 07-Feb-2026  
**Purpose:** Record where value from `docs/_archive/` was moved (per GUIDE_41_DOCS). Empty or redundant files removed from _archive.

---

## Destination map

| Archived file | Value destination | Notes |
|---------------|-------------------|--------|
| API_REFERENCE.md | REF_15_API | Key API reflected in REF_15; legacy full text was in _archive. |
| ARCHITECTURE.md | REF_13_ARCH | Overview and boundaries in REF_13. |
| BAAS_IMPLEMENTATION_SUMMARY.md | REF_22 (status), REF_15 (BaaS facade) | BaaS facade in API scope; status in project overview. |
| BEST_PRACTICES.md | REF_14_DX, GUIDE_01_USAGE | DX and usage guide. |
| COMPREHENSIVE_BENCHMARKS.md | logs/benchmarks/BENCH_20251028_COMPREHENSIVE_SUMMARY.md | Run summary in benchmark logs. |
| ECOSYSTEM_INTEGRATION_GUIDE.md | REF_22 (ecosystem), REF_13 (boundaries) | Ecosystem alignment in REF_22; integration in REF_13. |
| FIX_BCRYPT_ISSUE.md | GUIDE_01_USAGE sec.  Troubleshooting, changes/CHANGE_20250126_BCRYPT_WORKAROUND.md | Workaround documented. |
| GET_STARTED.md | GUIDE_01_USAGE | Quick start and examples in guide. |
| INSTALL_DEPENDENCIES.md | GUIDE_01_USAGE, REF_22 | Install/usage in guide. |
| MIGRAT_FEATURE_VERIFICATION.md | changes/ (implementation evidence) | Verification captured in changes culture; key in REF_22 status. |
| NAVIGATION_CACHING_BREAKTHROUGH.md | REF_13 (caching), logs (implementation) | Caching in architecture; implementation in logs. |
| PERFORMANCE_RESULTS.md | logs/benchmarks/BENCH_20251028_COMPREHENSIVE_SUMMARY.md, REF_54_BENCH | Benchmark evidence. |
| PHASE_6_XWDATA_ANALYSIS.md | logs/reviews/REVIEW_20251104_PHASE6_XWDATA_FORMAT_STRATEGIES.md | Review created first; conclusion: no migration. |
| PIPELINE_OPTIMIZATION_PLAN.md | REF_21_PLAN, REF_22 | Planning/roadmap. |
| PROJECT_PHASES.md | REF_22_PROJECT sec.  Historical phases | Phases and timeline in REF_22. |
| QUICK_REFERENCE.md | GUIDE_01_USAGE, REF_15_API | Quick ref in guide and API. |
| README_BCRYPT_ISSUE.md | CHANGE_20250126_BCRYPT_WORKAROUND, GUIDE_01 sec.  Troubleshooting | Same as FIX_BCRYPT. |
| README_PYTEST_CACHE_MISPLACED.md | (none) | Pytest cache notice only; no doc value. Deleted. |
| README.md (_archive) | INDEX, this log | Archive overview; value in INDEX and this capture. |
| READY_TO_USE.md | GUIDE_01_USAGE | Usage and readiness in guide. |
| REAL_WORLD_EXAMPLES.md | examples/, GUIDE_01 | Examples in repo and guide. |
| STANDARDIZED_BENCHMARKS.md | logs/benchmarks/, REF_54_BENCH | Benchmark scripts and evidence. |
| test_data.md | REF_51_TEST, tests/ | Test data and structure in REF_51. |
| TEST_COVERAGE_REPORT.md | logs/tests/TEST_20250126_XWDATA_COVERAGE.md | Coverage summary in logs/tests. |
| TEST_RESULTS_SUMMARY.md | logs/tests/TEST_20250126_XWDATA_COVERAGE.md, REF_51_TEST | Same as coverage. |
| TUTORIAL_QUICK_START.md | GUIDE_01_USAGE | Quick start in guide. |
| V7_MULTI_FORMAT_PERFORMANCE.md | logs (implementation), REF_54 | Version comparison in logs; performance in REF_54. |
| V8_FORMAT_AGNOSTIC_FEATURES.md | REF_22, REF_15 | Features in project and API. |
| XWDATA_XWQUERY_INTEGRATION_COMPLETE.md | changes/CHANGE_20251026_XWDATA_XWQUERY_INTEGRATION.md | Full change log with test evidence. |

---

*All added value preserved in REF documents or in logs/changes. Empty or duplicate files removed from _archive.*
