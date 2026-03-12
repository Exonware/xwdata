# Agent brief — xwdata

**Purpose:** Persistent context for agents (and maintainers) working on xwdata. Keeps scope, conventions, and priorities in one place.  
**Last updated:** 07-Feb-2026  
**Source:** Ecosystem review (REVIEW_20260208_112135_654_FULL), REF_35_REVIEW, gap review (REVIEW_20260207_120000_000_XWDATA_GAP_*).

---

## 1. Context and current status

- **Role:** xwdata is the **format-agnostic data engine**: "xwnode plus serialization." XWData facade, engine, 50+ formats (via xwsystem), XWNode integration (XWDataNode), CoW, references, metadata, async/sync API. **Base data layer** for xwschema, xwaction, xwentity, xwstorage, xwquery.
- **Ecosystem review (REVIEW_20260208_112135_654_FULL):** **Alpha high (4/5)**. Deep-dive: **D=5, C=4, T=4**, composite **4.25**. Maturity uses **25% docs, 50% codebase, 25% tests**. Not Beta mainly due to C=4 and T=4 (code depth and test volume vs. e.g. xwnode/xwjson).
- **Project review (REF_35_REVIEW):** Alpha (medium–high), ~85%; no blocking issues; IDEA/requirements clear; REF_01_REQ 14/14; downstream REFs refreshed from REF_01_REQ (07-Feb-2026). M3 (REF_* and doc placement) done.

---

## 2. What is already strong (preserve this)

- **Docs:** Full REF set: REF_01_REQ, REF_11_COMP, REF_12_IDEA, REF_13_ARCH, REF_14_DX, REF_15_API, REF_21_PLAN, REF_22_PROJECT, REF_35_REVIEW, REF_51_TEST, REF_54_BENCH. `docs/INDEX.md` is the hub; traceability REF_01 → downstream REFs is explicit. Root .md moved to docs/ (per REF_35).
- **Requirements and scope:** REF_01_REQ and REF_22_PROJECT state scope: **in scope** = data structure using xwnode, reference/lazy; **out of scope** = concrete schema, actions, xwentity features, node/edge strategies. "xwdata only covers xwobject + xwnode + serialization into one."
- **Architecture:** REF_13_ARCH describes engine pattern (XWData → XWDataEngine → serializer, strategies, metadata, resolver, cache, node factory), XWDataNode, delegation to xwsystem/xwnode, consumers. No circular dependency on consumers.
- **Tests:** 4-layer layout (0.core–3.advance), ~30 test files, runner.py, Five Priorities markers. REF_51_TEST documents layers and runner (including --security, --performance).
- **Benchmarks:** REF_54_BENCH links to `benchmarks/` and `docs/logs/benchmarks/`. INDEX "Other" points to examples and benchmarks. REF_14_DX and REF_22 link to examples/ and benchmarks/.

---

## 3. Prioritized next steps

**High priority (push toward Beta; codebase + tests = 50% + 25%)**

1. **Strengthen codebase depth (C=4 → 5)**  
   Ensure engine, conversion pipeline, reference resolution, and metadata are clearly structured and documented in REF_13/REF_15; add or refactor only within existing boundaries (orchestrate xwsystem; no node strategies in xwdata). Prefer completing existing engine/component surface over new features.

2. **Increase test coverage and substance (T=4 → 5)**  
   Add tests in 1.unit and 2.integration: more format combinations, reference resolution edge cases, CoW behavior, metadata roundtrip, async vs sync paths. Keep 4-layer structure and Five Priorities markers.

**Medium priority (discoverability and consistency)** — *mostly done*

3. ~~Examples and benchmarks in REF_14_DX and REF_22~~ — Done (REF_14_DX, REF_22, INDEX).
4. ~~REF_51_TEST vs runner options~~ — Done (--security, --performance in REF_51).
5. **Benchmark evidence when runs exist:** When benchmark runs are produced, add entries to `docs/logs/benchmarks/INDEX.md` and link from REF_54_BENCH.

**Lower priority**

6. ~~**Optional: example-as-test**~~ — Done: `tests/2.integration/test_example_basic_usage.py` mirrors examples/basic_usage.py minimal flow (create, get, set).
7. **Keep REF_01_REQ as single source** — When changing vision/goals/scope, update REF_01_REQ first, then refresh REF_22, REF_13, REF_12, REF_14, REF_15, REF_21.

---

## 4. Conventions

- **Guides:** GUIDE_00_MASTER, GUIDE_41_DOCS (only README at root; all other .md under `docs/`), GUIDE_51_TEST (4-layer, REF_51_TEST), GUIDE_35_REVIEW, GUIDE_13_ARCH, GUIDE_54_BENCH.
- **Naming:** REF_* in docs/; change logs in docs/changes/ (e.g. CHANGE_YYYYMMDD_HHMMSS_mmm_DESCRIPTION); test/review logs under docs/logs/tests/ and docs/logs/reviews/.
- **Dependencies:** xwdata depends on **xwsystem, xwnode, xwjson** (and optional xwlazy, xwformats, xwschema, xwentity, xwstorage for [full]). No circular dependency with xwschema, xwaction, xwentity, xwstorage (they consume xwdata).
- **Traceability:** When changing behavior or scope, update REF_22_PROJECT (and milestones if needed), REF_13_ARCH if architecture changes, REF_51_TEST if test layout/runner changes. REF_01_REQ remains single requirements source.

---

## 5. Pitfalls to avoid

- **Scope creep:** No concrete schema implementation, no actions, no xwentity features, no node/edge strategies in xwdata. Schema via provider; node strategies in xwnode.
- **Reimplementing serialization:** Use xwsystem (and xwformats/xwjson where applicable). xwdata orchestrates.
- **Adding .md at repo root:** New project-level doc under `docs/` (or `docs/_archive/`). Only README.md at root.
- **Skipping 4-layer test structure:** New behavior in the appropriate layer (0.core facade/imports, 1.unit engine/components, 2.integration format/storage/schema, 3.advance security/performance/extensibility).
- **Drift between REF_15 and code:** When changing public API (facade, `__all__`), update REF_15_API.
- **Circular dependency with consumers:** xwdata must not depend on xwschema, xwaction, xwentity, xwstorage in a way that creates a cycle.

---

## 6. Key file references

| Purpose | Path |
|--------|------|
| Requirements source | docs/REF_01_REQ.md |
| Vision, goals, FR/NFR, milestones, scope | docs/REF_22_PROJECT.md |
| Architecture, engine, boundaries | docs/REF_13_ARCH.md |
| API reference | docs/REF_15_API.md |
| Test layers and runner | docs/REF_51_TEST.md, tests/runner.py |
| Benchmarks | docs/REF_54_BENCH.md, benchmarks/ |
| Doc hub | docs/INDEX.md |
| Project review and next steps | docs/REF_35_REVIEW.md |
| REF_01 alignment and plan | docs/logs/reviews/REVIEW_20260207_163000_000_REQUIREMENTS.md |
| Gap (docs vs code vs tests vs examples vs benchmarks) | docs/logs/reviews/REVIEW_20260207_120000_000_XWDATA_GAP_DOCS_CODE_TESTS_EXAMPLES_BENCHMARKS.md |
| Ecosystem full review | repo docs/logs/reviews/REVIEW_20260208_112135_654_FULL.md |

---

*Update this brief when maturity, scope, or priorities change. Link from REF_35_REVIEW or INDEX.*
