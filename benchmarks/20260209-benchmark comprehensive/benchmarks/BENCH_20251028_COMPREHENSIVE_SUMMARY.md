# Benchmark run summary — comprehensive (historical)

**Date:** 2025-10-28  
**Source:** _archive/COMPREHENSIVE_BENCHMARKS.md, _archive/PERFORMANCE_RESULTS.md, _archive/STANDARDIZED_BENCHMARKS.md (value moved 07-Feb-2026)

---

## Summary

- **Script:** comprehensive_benchmarks.py (and related performance/standardized runs).
- **Operations:** FROM_NATIVE, LOAD, MODIFICATION COW, NAVIGATION, PARSE, SAVE, SERIALIZE across sizes (small, medium, large, huge) and formats (JSON, TOML, XML, YAML).
- **Sample (Oct 2025):** 53 tests, 49 successful, 4 failed (navigation await expression issues). Fastest: modification_small ~0.0004ms; slowest: from_native_huge ~255ms. Large YAML load ~227ms; large JSON load ~16ms.
- **Evidence:** Scripts in repo [benchmarks/](../../../benchmarks/). Current runs: add new BENCH_*.md here and link from [REF_54_BENCH](../../REF_54_BENCH.md).

---

*Per REF_54_BENCH and GUIDE_54_BENCH.*
