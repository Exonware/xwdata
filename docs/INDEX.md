# Documentation index — xwdata

**Last Updated:** 07-Feb-2026

Navigation hub for xwdata docs. Per GUIDE_41_DOCS and GUIDE_00_MASTER.

## Why xwdata matters

`xwdata` is built for teams that need one data pipeline across many formats and data shapes.

- Load from one format and save to another with one API.
- Build multiple structures (maps, trees, graph-like models) from the same source input.
- Keep the same developer workflow for runtime memory use and persisted storage flows.

For practical usage patterns, start with [GUIDE_01_USAGE.md](GUIDE_01_USAGE.md) and [REF_15_API.md](REF_15_API.md).

## Requirements (source of truth)

| Document | Purpose | Producing guide |
|----------|---------|------------------|
| [REF_01_REQ.md](REF_01_REQ.md) | **Requirements source** (sponsor input); feeds REF_12, REF_13, REF_14, REF_15, REF_21, REF_22 | GUIDE_01_REQ |

## References (REF_*)

| Document | Purpose | Producing guide |
|----------|---------|------------------|
| [REF_11_COMP.md](REF_11_COMP.md) | Compliance stance and standards (from REF_01_REQ sec. 4) | GUIDE_11_COMP |
| [REF_12_IDEA.md](REF_12_IDEA.md) | Idea context and evaluation (from REF_01_REQ sec. 1–2) | GUIDE_12_IDEA |
| [REF_13_ARCH.md](REF_13_ARCH.md) | Architecture and engine (from REF_01_REQ) | GUIDE_13_ARCH |
| [REF_14_DX.md](REF_14_DX.md) | Developer experience, key code (from REF_01_REQ sec. 5–6) | GUIDE_14_DX |
| [REF_15_API.md](REF_15_API.md) | API reference (from REF_01_REQ sec. 6) | GUIDE_15_API |
| [REF_21_PLAN.md](REF_21_PLAN.md) | Milestones and roadmap (from REF_01_REQ sec. 9) | GUIDE_21_PLAN |
| [REF_22_PROJECT.md](REF_22_PROJECT.md) | Vision, requirements, milestones (from REF_01_REQ) | GUIDE_22_PROJECT |
| [REF_35_REVIEW.md](REF_35_REVIEW.md) | Review summary and status | GUIDE_35_REVIEW |
| [REF_51_TEST.md](REF_51_TEST.md) | Test status and coverage (from REF_01_REQ sec. 8) | GUIDE_51_TEST |
| [REF_54_BENCH.md](REF_54_BENCH.md) | Benchmark scope and evidence (from REF_01_REQ sec. 8) | GUIDE_54_BENCH |

## Usage

| Document | Purpose |
|----------|---------|
| [GUIDE_01_USAGE.md](GUIDE_01_USAGE.md) | How to use xwdata (GUIDE_41_DOCS) |

## Other

| Path | Purpose |
|------|---------|
| [examples/](../examples/) | Example scripts and demos; start with [basic_usage.py](../examples/basic_usage.py); see [examples/README.md](../examples/README.md) |
| [benchmarks/](../benchmarks/) | Benchmark scripts; see [REF_54_BENCH.md](REF_54_BENCH.md) |
| [_archive/](_archive/) | Legacy docs; value moved 07-Feb-2026 to REF_*, GUIDE_01_USAGE, [logs/](logs/) (see [logs/ARCHIVE_VALUE_CAPTURE_XWDATA.md](logs/ARCHIVE_VALUE_CAPTURE_XWDATA.md)) |
| [changes/](changes/) | Change notes |
| [logs/](logs/) | Implementation/status logs |

## Evidence (logs)

| Location | Content |
|----------|---------|
| [logs/reviews/](logs/reviews/) | REVIEW_* (GUIDE_35_REVIEW); [REVIEW_*_REQUIREMENTS.md](logs/reviews/REVIEW_20260207_163000_000_REQUIREMENTS.md) — REF_01_REQ alignment; [REVIEW_*_XWDATA_GAP_*.md](logs/reviews/REVIEW_20260207_120000_000_XWDATA_GAP_DOCS_CODE_TESTS_EXAMPLES_BENCHMARKS.md) — gap (docs vs code vs tests vs examples vs benchmarks) |
| [logs/AGENT_BRIEF_XWDATA.md](logs/AGENT_BRIEF_XWDATA.md) | Context, priorities, conventions, and pitfalls for agents and maintainers (from ecosystem and gap reviews). |

## Standards

- Only `README.md` at repo root; all other Markdown under `docs/` (GUIDE_41_DOCS).

---

*Per GUIDE_00_MASTER and GUIDE_41_DOCS.*
