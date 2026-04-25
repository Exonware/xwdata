# Project Reference — xwdata

**Library:** exonware-xwdata  
**Last Updated:** 07-Feb-2026  
**Requirements source:** [REF_01_REQ.md](REF_01_REQ.md)

Requirements and project status (output of GUIDE_22_PROJECT). Per REF_35_REVIEW.

---

## Scope and boundaries (REF_01_REQ sec. 2)

| In scope | Out of scope | Dependencies | Anti-goals |
|----------|--------------|--------------|------------|
| Data structure using xwnode; reference and lazy capabilities. Only the data structure. | Schema: no concrete schema; schema provider that validates xwdata is acceptable but avoid circular referencing. No actions; no xwentity/entity features; no node/edge strategies (those are in xwnode). | xwsystem, xwformats, xwjson, xwnode (most important), xwlazy (optional). | Not dwelling on handlers, other data formats, new formats/serialization, node strategies—xwdata only covers xwobject + xwnode + serialization into one. |

---

## Vision (from REF_01_REQ sec. 1)

xwdata is an implementation of **xwnode plus serialization**: enabling serializations (JSON, TOML, and more) to be saved as data nodes; it is the base of any data structure and will be used as the representation for saving data, getting data, and many data operations. It links xwobject (xwsystem) with xwnode capabilities and serialization into one.

---

## Goals (from REF_01_REQ sec. 1, ordered)

1. **Support for all serialization formats** in ExonWare (xwsystem formats, xwformats, xwjson).
2. **Save/load efficiently** — performance is a big goal.
3. **Extensibility** — pluggable strategies, optional facades.
4. **Other libraries don’t worry** about save/load and its optimization; xwdata handles it.
5. **xwdata can play as a database** (front-end or backend); it links xwnode with xwobject and serialization into one.

**Ecosystem alignment (future):** When used with xwstorage.connect/xwquery, xwdata can align with a Firebase Firestore/Realtime DB–style data layer role. This is not in REF_01_REQ scope; it is ecosystem positioning only.

---

## Functional Requirements (Summary)

| ID | Requirement | Priority | Status |
|----|-------------|----------|--------|
| FR-001 | Format-agnostic engine (XWDataEngine) | High | Done |
| FR-002 | 50+ formats via xwsystem serialization | High | Done |
| FR-003 | XWNode integration (navigation, graph) | High | Done |
| FR-004 | Copy-on-write semantics | High | Done |
| FR-005 | Reference resolution and metadata | High | Done |
| FR-006 | Async and sync API | High | Done |
| FR-007 | 4-layer tests, benchmarks | High | Done |

---

## Non-Functional Requirements (5 Priorities, from REF_01_REQ sec. 8)

1. **Security:** SecurityConfig (path validation, sanitization, max file size, nesting, safe mode); presets strict/relaxed; no code execution from data.
2. **Usability:** Single facade API, README and examples, config presets, typed errors; docs under docs/.
3. **Maintainability:** Engine pattern; REF_* and logs; 4-layer tests plus Five Priorities markers; runner.py with Markdown output.
4. **Performance:** Sub-ms for many formats; caching; LoadStrategy (full/lazy/partial/streaming/auto); benchmarks in repo.
5. **Extensibility:** FormatStrategyRegistry; pluggable strategies; optional BaaS facade; schema/storage/entity integration contracts.

---

## Project Status Overview

- **Current phase:** Alpha (Medium–High). ~85%; 84+ files; 4-layer tests; docs in docs/ (REF_*, architecture, changes, logs).
- **Docs:** REF_01_REQ, REF_11_COMP, REF_12_IDEA, REF_13_ARCH, REF_14_DX, REF_15_API, REF_21_PLAN, REF_22_PROJECT (this file), REF_35_REVIEW, REF_51_TEST, REF_54_BENCH. **Examples:** [examples/](../../examples/) (see [examples/README.md](../../examples/README.md)). **Benchmarks:** [benchmarks/](../../benchmarks/) (see [REF_54_BENCH](REF_54_BENCH.md)).

---

## Milestones (from REF_01_REQ sec. 9)

| Milestone | Target | Status |
|-----------|--------|--------|
| M1 — Core engine and format set | v0.1.x | Done |
| M2 — XWNode, CoW, references | v0.1.x | Done |
| M3 — REF_* and doc placement | v0.1.x | Done |

Roadmap (v1–v4): see [REF_21_PLAN.md](REF_21_PLAN.md).

---

## Historical phases (xData roadmap)

*Value from _archive/PROJECT_PHASES.md (captured 07-Feb-2026).*

- **Version 0 (experimental):** Core data manipulation, format-agnostic API, COW, hybrid registration, two-tier caching, fluent config, rich errors, test coverage. Status: foundation complete.
- **Version 1 (production):** Production hardening, benchmarks, security audit, docs, CI/CD. Target: Q1 2026.
- **Version 2 (Mars standard draft):** Interoperability, cross-platform API, validation suite. Target: Q2 2026.
- **Version 3 (RUST core & facades):** RUST core, Python/TypeScript/Go/Rust facades. Target: Q3 2026.
- **Version 4 (Mars standard):** Full Mars compliance, enterprise deployment. Target: Q4 2026.
- **Principles:** Phase transitions build on previous; quality over speed; >95% test coverage, benchmarks per phase, security audit at milestones.

---

## Success criteria (REF_01_REQ sec. 1)

- **6 mo / 1 yr:** What we have now: 100% pass rate in all tests; capabilities for saving data immediately, save/load with all advanced features (lazy, referencing, etc.). This stage is where we can say we have succeeded.

---

## Risks and assumptions (REF_01_REQ sec. 10)

- **Risks:** Dependency chain (xwsystem, xwnode, xwquery, xwjson); performance and format coverage; scope creep (staying at data structure + xwnode + serialization); MARS/Rust roadmap.
- **Assumptions:** xwsystem remains single source for serialization; xwnode for node/graph semantics; consumers use xwdata as base data layer; optional deps stay optional.
- **Kill/pivot:** If we must reimplement serialization or node strategies inside xwdata; or sponsor merges scope or drops the product.

---

## Traceability

- **Requirements source:** [REF_01_REQ.md](REF_01_REQ.md)
- **Ideas | DX | API | Planning:** [REF_12_IDEA.md](REF_12_IDEA.md) | [REF_14_DX.md](REF_14_DX.md) | [REF_15_API.md](REF_15_API.md) | [REF_21_PLAN.md](REF_21_PLAN.md)
- **Project → Arch:** This document → [REF_13_ARCH.md](REF_13_ARCH.md)
- **Review evidence:** [REF_35_REVIEW.md](REF_35_REVIEW.md), [logs/reviews/](logs/reviews/)
- **Consumers (use xwdata as base):** [xwschema](../../xwschema/docs/REF_22_PROJECT.md), [xwaction](../../xwaction/docs/REF_22_PROJECT.md), [xwentity](../../xwentity/docs/REF_13_ARCH.md), [xwstorage.connect](../../xwstorage.connect/docs/REF_22_PROJECT.md), [xwquery](../../xwquery/docs/REF_22_PROJECT.md) — each links back to xwdata docs.

---

*See GUIDE_22_PROJECT.md for requirements process.*
