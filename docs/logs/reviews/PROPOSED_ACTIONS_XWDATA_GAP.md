# Proposed Codebase Actions — xwdata Gap (Docs vs Code vs Tests vs Examples vs Benchmarks)

**Source:** [REVIEW_20260207_120000_000_XWDATA_GAP_DOCS_CODE_TESTS_EXAMPLES_BENCHMARKS.md](REVIEW_20260207_120000_000_XWDATA_GAP_DOCS_CODE_TESTS_EXAMPLES_BENCHMARKS.md), [repo REVIEW_20260207_120000_000_GAP_DOCS_CODE_TESTS_EXAMPLES_BENCHMARKS.md](../../../../docs/logs/reviews/REVIEW_20260207_120000_000_GAP_DOCS_CODE_TESTS_EXAMPLES_BENCHMARKS.md)  
**Date:** 07-Feb-2026

---

## Summary

| Priority | Action | Status |
|----------|--------|--------|
| **P1** | Add REF_54_BENCH for xwdata; link benchmarks/ and docs/logs/benchmarks/ | Proposed / Implement |
| **P2** | Add Examples and Benchmarks to REF_14_DX, INDEX, REF_22, GUIDE_01_USAGE | Proposed / Implement |
| **P3** | REF_51_TEST: document --security and --performance; create docs/logs/benchmarks/ INDEX | Implemented |
| **Optional** | 2.integration test that runs basic_usage.py (example-as-test) | Proposed only |

**Implementation completed:** REF_54_BENCH, docs/logs/benchmarks/INDEX.md, INDEX (REF_54 + Examples + Benchmarks), REF_14_DX (Examples), REF_22 (Docs + examples/benchmarks), REF_51_TEST (--security/--performance), GUIDE_01_USAGE (Examples and benchmarks section + REF_51/REF_54 in doc table).

---

## 1. P1 — REF_54_BENCH and benchmark evidence

| # | Action | File(s) | Change |
|---|--------|---------|--------|
| 1.1 | Create REF_54_BENCH | `docs/REF_54_BENCH.md` | New file: benchmark scope (benchmarks/ scripts), SLAs or “no formal SLAs; see benchmarks/”, link to docs/logs/benchmarks/ when present. |
| 1.2 | Create benchmark logs placeholder | `docs/logs/benchmarks/INDEX.md` | New file: “Benchmark evidence for xwdata. Runs: (none logged yet). Scripts: ../../benchmarks/.” |
| 1.3 | Register REF_54 in INDEX and REF_22 | `docs/INDEX.md`, `docs/REF_22_PROJECT.md` | INDEX: add REF_54_BENCH to References table. REF_22 “Docs” row: add REF_54_BENCH. |

---

## 2. P2 — Examples and Benchmarks discoverability

| # | Action | File(s) | Change |
|---|--------|---------|--------|
| 2.1 | Add Examples line to REF_14_DX | `docs/REF_14_DX.md` | After “Usability expectations” or before footer: **Examples:** [examples/](../../examples/) — start with [basic_usage.py](../../examples/basic_usage.py); see [examples/README.md](../../examples/README.md). |
| 2.2 | Add Examples and Benchmarks to INDEX | `docs/INDEX.md` | In “Other” (or new “Examples & benchmarks”): Examples: [examples/](../examples/) (see [examples/README.md](../examples/README.md)); Benchmarks: [benchmarks/](../benchmarks/), [REF_54_BENCH](REF_54_BENCH.md). |
| 2.3 | Add Examples/Benchmarks to REF_22 | `docs/REF_22_PROJECT.md` | In “Docs” row (Project Status Overview): add “examples/ (see examples/README), benchmarks/ (REF_54_BENCH)”. |
| 2.4 | Add Examples to GUIDE_01_USAGE | `docs/GUIDE_01_USAGE.md` | In Documentation table or new “Examples” row: link to examples/ and examples/README.md. |

---

## 3. P3 — REF_51_TEST and benchmark logs

| # | Action | File(s) | Change |
|---|--------|---------|--------|
| 3.1 | Document runner --security and --performance | `docs/REF_51_TEST.md` | In “Running tests”: add “Optional filters: `--security`, `--performance` (subset of advance layer).” |
| 3.2 | Create docs/logs/benchmarks/ and INDEX | `docs/logs/benchmarks/INDEX.md` | As in 1.2; ensures benchmark runs can be logged and linked from REF_54. |

---

## 4. Optional — Example-as-test

| # | Action | File(s) | Change |
|---|--------|---------|--------|
| 4.1 | Add integration test that runs basic_usage | `tests/2.integration/test_example_basic_usage.py` | New test: subprocess or import + run minimal path (e.g. load a small JSON) from examples/basic_usage.py pattern to guard API drift. |

---

## 5. Cross-reference (repo-wide report)

From the ecosystem gap report, applied to xwdata:

- **Docs ↔ Examples:** Actions 2.1, 2.2, 2.4 close this.
- **Docs ↔ Benchmarks:** Actions 1.1, 1.2, 1.3, 2.2, 2.3 close this.
- **Docs ↔ Tests:** Action 3.1 keeps REF_51 in sync with runner.
- **Examples ↔ Tests:** Action 4.1 (optional) implements “example as test.”

---

## Implementation order

1. Create `docs/REF_54_BENCH.md` and `docs/logs/benchmarks/INDEX.md`.
2. Update `docs/INDEX.md` (REF_54 + Examples + Benchmarks rows).
3. Update `docs/REF_14_DX.md` (Examples line).
4. Update `docs/REF_22_PROJECT.md` (Docs row).
5. Update `docs/REF_51_TEST.md` (--security, --performance).
6. Update `docs/GUIDE_01_USAGE.md` (Examples).
7. (Optional) Add `tests/2.integration/test_example_basic_usage.py`.

---

*Proposed from gap reviews; implement in order above. After implementation, update this file or REF_35 to note completion.*
