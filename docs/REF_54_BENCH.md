# Benchmark Reference — xwdata (REF_54_BENCH)

**Library:** exonware-xwdata  
**Last Updated:** 07-Feb-2026  
**Requirements source:** [REF_01_REQ.md](REF_01_REQ.md) sec. 8 (performance), [REF_22_PROJECT.md](REF_22_PROJECT.md) FR-007  
**Producing guide:** [GUIDE_54_BENCH.md](../../docs/guides/GUIDE_54_BENCH.md)

---

## Purpose

Benchmark scope and evidence for xwdata. Scripts live in `benchmarks/`; optional run evidence in `docs/logs/benchmarks/`. Per REF_01_REQ sec. 8: “benchmarks and performance reports in repo.”

---

## Scope (benchmarks in repo)

| Script | Purpose |
|--------|---------|
| [benchmarks/comprehensive_benchmarks.py](../../benchmarks/comprehensive_benchmarks.py) | Comprehensive format and operation benchmarks |
| [benchmarks/performance_comparison.py](../../benchmarks/performance_comparison.py) | Performance comparison runs |
| [benchmarks/standardized_benchmarks.py](../../benchmarks/standardized_benchmarks.py) | Standardized benchmark suite |
| [benchmarks/diagnose_navigation.py](../../benchmarks/diagnose_navigation.py) | Navigation/path performance diagnostics |

Additional benchmark-style scripts exist under `examples/chatdb_bigfile/operations/` (e.g. benchmark_*.py) for JSON/encoder and large-file scenarios.

---

## Performance expectations (from REF_01_REQ sec. 8)

- **Sub-ms for many formats**; configurable cache; LoadStrategy (full/lazy/partial/streaming/auto).
- No formal SLA table in this REF yet; targets are “benchmarks in repo” and “performance reports.” When runs are logged, add SLAs or summary here and link [logs/benchmarks/](logs/benchmarks/).

---

## Benchmark evidence

- **Scripts:** [benchmarks/](../../benchmarks/) (repo root).
- **Logs (when produced):** [docs/logs/benchmarks/](logs/benchmarks/) — see [INDEX.md](logs/benchmarks/INDEX.md).

---

## Traceability

- **Requirements:** [REF_01_REQ.md](REF_01_REQ.md) sec. 8, [REF_22_PROJECT.md](REF_22_PROJECT.md) FR-007.
- **Review:** Gap (docs vs benchmarks) addressed in [logs/reviews/REVIEW_20260207_120000_000_XWDATA_GAP_DOCS_CODE_TESTS_EXAMPLES_BENCHMARKS.md](logs/reviews/REVIEW_20260207_120000_000_XWDATA_GAP_DOCS_CODE_TESTS_EXAMPLES_BENCHMARKS.md).

---

*Per GUIDE_54_BENCH. For run-by-run evidence, add entries under docs/logs/benchmarks/ and link from this REF.*
