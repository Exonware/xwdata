# Requirements Reference (REF_01_REQ)

**Project:** xwdata  
**Sponsor:** ExonWare (as with other projects)  
**Version:** 0.0.1  
**Last Updated:** 07-Feb-2026 (Batch 3 filled — reverse‑engineered from codebase)  
**Produced by:** [GUIDE_01_REQ.md](../../docs/guides/GUIDE_01_REQ.md)

---

## Purpose of This Document

This document is the **single source of raw and refined requirements** collected from the project sponsor and stakeholders. It is updated on every requirements-gathering run. When the **Clarity Checklist** (section 12) reaches the agreed threshold, use this content to fill REF_11_COMP, REF_12_IDEA, REF_22_PROJECT, REF_13_ARCH, REF_14_DX, REF_15_API, and REF_21_PLAN (planning artifacts). Template structure: [GUIDE_01_REQ.md](../../docs/guides/GUIDE_01_REQ.md).

---

## 1. Vision and Goals

| Field | Content |
|-------|---------|
| One-sentence purpose | xwdata is an implementation of xwnode plus serialization: enabling serializations (JSON, TOML, and more) to be saved as data nodes; it is the base of any data structure and will be used as the representation for saving data, getting data, and many data operations. |
| Primary users/beneficiaries | Developers. xwschema, xwaction, xwentity, xwstorage and others will use it. Heavily extends XW object (xwsystem) by linking xwnode capabilities and serialization. |
| Success (6 mo / 1 yr) | What we have now: 100% pass rate in all tests; capabilities for saving data immediately, save/load with all advanced features (lazy, referencing, etc.). This stage is where we can say we have succeeded. |
| Top 3–5 goals (ordered) | (1) Support for all serialization formats in ExonWare (xwsystem formats, xwformats, xwjson). (2) Save/load efficiently — performance is a big goal. (3) Extensibility. (4) So other libraries don’t need to worry about save/load and its optimization. (5) xwdata can even play as a database; it links xwnode with xwobject and serialization into one. |
| Problem statement | When we want to create other libraries we don’t need to worry about save/load and the optimization of that. xwdata handles it; it can even play as a database (front-end or backend). It’s linking xwnode with xwobject and serialization — all combined creates xwdata. |

## 2. Scope and Boundaries

| In scope | Out of scope | Dependencies | Anti-goals |
|----------|--------------|--------------|------------|
| Data structure using xwnode; reference and reference capabilities; lazy capabilities (extended from serialization or xwnode). Only the data structure. | Schema: no concrete schema; a schema provider that validates xwdata is acceptable but avoid circular referencing. No actions. No xwentity or entity features (those are in other libraries). No node strategies or edge strategies (that’s in xwnode). | xwsystem, xwformats, xwjson, xwnode (most important), xwlazy (optional — used for almost everything). | Not dwelling on handlers, other data formats, new formats/serialization, node strategies, or other strategies — these are not part of xwdata. xwdata only covers mixing xwobject + xwnode + serialization into one and giving new value. |

## 3. Stakeholders and Sponsor

| Sponsor (name, role, final say) | Main stakeholders | External customers/partners | Doc consumers |
|----------------------------------|-------------------|-----------------------------|---------------|
| ExonWare (main sponsor; same as other projects). | Developers; product uses of the advanced libraries that consume xwdata. | None for now. Maybe in the future: Python sponsorship and showcase of this library. | Mostly developers and other users. |

## 4. Compliance and Standards

| Regulatory/standards | Security & privacy | Certifications/evidence |
|----------------------|--------------------|--------------------------|
| No standard in mind for now; this version stays like that. Developed with highest standards in mind; will review once we reach a version that requires the MARS standard. | Same as above: no specific requirement for this version; highest standards in mind; review when MARS is required. | Same: no specific requirement for this version; highest standards; review when MARS is required. |

## 5. Product and User Experience

| Main user journeys/use cases | Developer persona & 1–3 line tasks | Usability/accessibility | UX/DX benchmarks |
|-----------------------------|------------------------------------|--------------------------|------------------|
| (1) Load from any format (JSON/YAML/XML/TOML/CSV, etc.), modify via path navigation, save to same or different format. (2) Create XWData from native dict/list or merge multiple sources; fluent get/set/delete. (3) Use copy-on-write for safe concurrent access. (4) Resolve references ($ref, @href, anchors); preserve metadata roundtrip. (5) Optional: stream large files (e.g. JSONL), use caching for performance, integrate with schema/storage via providers. | Developer consuming xwdata: create or load data in 1–3 lines (XWData(dict), await XWData.load(path)); navigate and mutate with path API (get/set/delete); save to any format. Advanced: config presets (default/strict/fast/development), reference resolution, merge/diff/patch, batch operations. | Clear API (XWData facade, shortcuts), docs (README, examples, API reference), config presets (SecurityConfig, PerformanceConfig, etc.), typed errors (XWDataError hierarchy). | One API for all formats; “like a universal config/data layer” with xwnode navigation and COW; async-first with sync convenience. |

## 6. API and Surface Area

| Main entry points / "key code" | Easy (1–3 lines) vs advanced | Integration/existing APIs | Not in public API |
|--------------------------------|------------------------------|---------------------------|-------------------|
| XWData (facade), load / from_native / parse; XWDataBuilder; quick_* shortcuts (quick_load, quick_save, quick_convert, quick_get, quick_set, quick_delete, quick_merge, quick_diff, quick_patch, quick_validate); to_* / from_* per format (to_json, from_yaml, etc.); XWDataConfig and config presets (default, strict, fast, development); merge_data, diff_data, patch_data, batch_convert, batch_validate, batch_transform; FormatConverter, ConversionPipeline, FormatValidator (when available); XWDataEngine, XWDataNode, NodeFactory, FormatStrategyRegistry for extension. | Easy: XWData(dict), await XWData.load(path), await data.get/set/delete(path), await data.save(path). Advanced: multi-source merge, reference config, metadata/COW config, streaming, caching, batch ops, format conversion pipeline, BaaS facade (optional). | xwsystem (serialization, security, cache, IO), xwnode (XWDataNode extends XWNode), xwquery (when used), xwjson (format conversion); schema/storage/entity via integration contracts (validator, mapper, adapter) not concrete implementations. | Internal engine wiring, format-strategy internals, cache keys; node/edge strategies stay in xwnode; concrete schema/entity/action implementations are out of scope. |

## 7. Architecture and Technology

| Required/forbidden tech | Preferred patterns | Scale & performance | Multi-language/platform |
|-------------------------|--------------------|----------------------|-------------------------|
| Python ≥3.12; required: xwsystem, xwnode, xwquery, xwjson. Optional: xwlazy, xwformats, xwschema, xwentity, xwstorage (full extra). No reimplementation of serialization handlers — orchestrate xwsystem. | Engine pattern (facade → XWDataEngine → serializer + strategies + metadata + references + cache + node factory); async-first; COW for mutations; format-agnostic API; config presets; optional BaaS facade. | Sub-ms for many formats (benchmarks in repo); configurable cache (e.g. xwsystem global cache); load strategies: full/lazy/partial/streaming/auto; max file size and nesting limits via SecurityConfig. | Python-only for current version; roadmap mentions Rust core/facades and Mars standard in later versions (v2–v4). |

## 8. Non-Functional Requirements (Five Priorities)

| Security | Usability | Maintainability | Performance | Extensibility |
|----------|-----------|-----------------|-------------|---------------|
| SecurityConfig: path validation, sanitization, max file size, nesting depth, safe mode, allowed schemes, deny extensions, timeout. Presets: strict (untrusted data), relaxed (dev). No code execution from data; file_security and validators in core. | Single facade API, README and examples, config presets, typed errors; docs under docs/ (REF_*, architecture, changes, logs). | Engine pattern; REF_* and logs; 4-layer tests (core, unit, integration, advance) plus Five Priorities markers (security, usability, maintainability, performance, extensibility); runner.py with Markdown output. | Sub-ms targets for many formats; caching (global cache, configurable); LoadStrategy (full/lazy/partial/streaming/auto); benchmarks and performance reports in repo. | FormatStrategyRegistry; pluggable format strategies; optional BaaS facade; schema/storage/entity integrations via contracts (validator, mapper, adapter); version and compatibility in config. |

## 9. Milestones and Timeline

| Major milestones | Definition of done (first) | Fixed vs flexible |
|------------------|----------------------------|-------------------|
| M1 — Core engine and format set (v0.1.x); M2 — XWNode, COW, references (v0.1.x); M3 — REF_* and doc placement (v0.1.x). Roadmap (from README): v1 (Q1 2026) production ready; v2 (Q2 2026) Mars Standard draft; v3 (Q3 2026) Rust core & facades; v4 (Q4 2026) Mars implementation. | First milestone (M1): engine and format set done when format-agnostic load/save works with xwsystem serializers and tests pass. Current status: Alpha; ~85%; 84+ files; 4-layer tests; REF_22/REF_13/REF_35 in place. | Dates on roadmap are targets; scope (formats, features) can be prioritized; MARS and Rust are deferred to later versions. |

## 10. Risks and Assumptions

| Top risks | Assumptions | Kill/pivot criteria |
|-----------|-------------|----------------------|
| (1) Dependency chain (xwsystem, xwnode, xwquery, xwjson) — API or behavior changes in dependencies could require non-trivial updates. (2) Performance and format coverage — keeping “all formats” fast and correct as xwsystem grows. (3) Scope creep — staying strictly at “data structure + xwnode + serialization” and not absorbing schema/entity/actions/strategies. (4) MARS / Rust roadmap — later versions depend on external standards and multi-language work. | (1) xwsystem remains the single source for serialization; xwnode for node/graph semantics. (2) Consumers (xwschema, xwaction, xwentity, xwstorage) will use xwdata as the base data layer. (3) Developers are the primary users; no external compliance required for current version. (4) Optional deps (xwlazy, xwformats, etc.) stay optional; core works with required deps only. | If we must reimplement serialization or node strategies inside xwdata (contradicts anti-goals); or if sponsor decides to merge scope with another package or drop the product. |

## 11. Workshop / Session Log (Optional)

| Date | Type | Participants | Outcomes |
|------|------|---------------|----------|
| 07-Feb-2026 | Start (Batch 1) | Sponsor, AI | REF_01_REQ created; Batch 1 questions asked |
| 07-Feb-2026 | Batch 1 answers | Sponsor, AI | Sections 1–2 filled from sponsor (vision, goals, scope, dependencies, anti-goals); clarity 5/14 |
| 07-Feb-2026 | Batch 2 answers | Sponsor, AI | Sections 3–4 filled (ExonWare sponsor, developers, no external/compliance for now, MARS deferred); clarity 7/14 |
| 07-Feb-2026 | Batch 3 (reverse‑engineered) | Sponsor, AI | Sections 5–10 filled from codebase (product, API, arch, NFRs, milestones, risks); clarity 14/14; Ready Yes |
| 07-Feb-2026 | Direction update (PROMPT_01_REQ_03_UPDATE) | Sponsor, AI | Next: fill/refresh downstream REFs (REF_12_IDEA, REF_22_PROJECT, REF_13_ARCH, REF_14_DX, REF_15_API) and planning from REF_01_REQ. Informed by REVIEW_20260207_PROJECT_STATUS. |
| 07-Feb-2026 | Cont downstream (GUIDE_01_USAGE, README, REF_51) | Agent | GUIDE_01_USAGE expanded (quick start, REF links); README docs table added REF_51_TEST, REF_35_REVIEW, GUIDE_01_USAGE; REF_51_TEST added Running tests section. |

## 12. Clarity Checklist

| # | Criterion | ☐ |
|---|-----------|---|
| 1 | Vision and one-sentence purpose filled and confirmed | ☑ |
| 2 | Primary users and success criteria defined | ☑ |
| 3 | Top 3–5 goals listed and ordered | ☑ |
| 4 | In-scope and out-of-scope clear | ☑ |
| 5 | Dependencies and anti-goals documented | ☑ |
| 6 | Sponsor and main stakeholders identified | ☑ |
| 7 | Compliance/standards stated or deferred | ☑ |
| 8 | Main user journeys / use cases listed | ☑ |
| 9 | API / "key code" expectations captured | ☑ |
| 10 | Architecture/technology constraints captured | ☑ |
| 11 | NFRs (Five Priorities) addressed | ☑ |
| 12 | Milestones and DoD for first milestone set | ☑ |
| 13 | Top risks and assumptions documented | ☑ |
| 14 | Sponsor confirmed vision, scope, priorities | ☑ |

**Clarity score:** 14 / 14. **Ready to fill downstream docs?** ☑ Yes

---

## Traceability (downstream REFs)

- **REF_11_COMP:** [REF_11_COMP.md](REF_11_COMP.md) — Compliance stance (sec. 4)
- **REF_12_IDEA:** [REF_12_IDEA.md](REF_12_IDEA.md) — Idea context (sec. 1–2)
- **REF_22_PROJECT:** [REF_22_PROJECT.md](REF_22_PROJECT.md) — Vision, FR/NFR, milestones
- **REF_13_ARCH:** [REF_13_ARCH.md](REF_13_ARCH.md) — Architecture (sec. 7)
- **REF_14_DX:** [REF_14_DX.md](REF_14_DX.md) — Developer experience (sec. 5–6)
- **REF_15_API:** [REF_15_API.md](REF_15_API.md) — API reference (sec. 6)
- **REF_21_PLAN:** [REF_21_PLAN.md](REF_21_PLAN.md) — Milestones and roadmap (sec. 9)

---

*Per GUIDE_01_REQ. Collect thoroughly, then feed downstream REFs.*
