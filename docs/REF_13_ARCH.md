# Architecture Reference — xwdata

**Library:** exonware-xwdata  
**Last Updated:** 07-Feb-2026  
**Requirements source:** [REF_01_REQ.md](REF_01_REQ.md)  
**Producing guide:** [GUIDE_13_ARCH.md](../../docs/guides/GUIDE_13_ARCH.md)

Architecture and design (output of GUIDE_13_ARCH). Per REF_35_REVIEW. Legacy detail was in _archive/ARCHITECTURE.md (value moved 07-Feb-2026; see [logs/ARCHIVE_VALUE_CAPTURE_XWDATA.md](logs/ARCHIVE_VALUE_CAPTURE_XWDATA.md)).

---

## Overview

xwdata uses a **pure engine pattern**: the XWData facade delegates to XWDataEngine, which orchestrates xwsystem serialization (XWSerializer), format strategies, metadata processing, reference resolution, cache, and node factory. XWDataNode extends XWNode for navigation and graph operations.

---

## Boundaries

- **Public API:** XWData facade; multi-type init (dict/list/path/XWData/merge); fluent get/set/delete/merge/transform; async operations.
- **Engine:** XWDataEngine composes XWSerializer (xwsystem), FormatStrategyRegistry, MetadataProcessor, ReferenceResolver, CacheManager, NodeFactory.
- **Formats:** 50+ via xwsystem (and xwformats where used); format-agnostic at API level.
- **Node layer:** XWDataNode extends XWNode; path navigation, graph ops, metadata.

---

## Delegation

- **xwsystem:** Serialization (24+ formats), security, utilities.
- **xwnode:** Graph and node operations via XWDataNode.
- **xwstorage.connect / xwquery:** Data persistence and query when integrated.

## Consumed by

xwdata is used as the base data layer by: [xwschema](../../xwschema/docs/INDEX.md), [xwaction](../../xwaction/docs/REF_22_PROJECT.md), [xwentity](../../xwentity/docs/REF_13_ARCH.md), [xwstorage.connect](../../xwstorage.connect/docs/REF_22_PROJECT.md), [xwquery](../../xwquery/docs/REF_22_PROJECT.md). Their REFs link to xwdata docs.

---

## Layering

1. **Facade:** XWData (public API).
2. **Engine:** XWDataEngine (orchestrator).
3. **Components:** Serializer, strategies, metadata, resolver, cache, node factory.
4. **Node:** XWDataNode (xwnode integration).

---

## Technology (from REF_01_REQ sec. 7)

- **Required:** Python ≥3.12; xwsystem, xwnode, xwquery, xwjson. Optional: xwlazy, xwformats, xwschema, xwentity, xwstorage.connect (full extra). No reimplementation of serialization handlers — orchestrate xwsystem.
- **Patterns:** Engine pattern; async-first; COW for mutations; format-agnostic API; config presets.
- **Scale/performance:** Sub-ms for many formats; configurable cache; LoadStrategy (full/lazy/partial/streaming/auto); SecurityConfig limits.
- **Platform:** Python-only for current version; roadmap v2–v4 (Mars, Rust core/facades) per REF_21_PLAN.

---

*See ARCHITECTURE.md for detailed diagram. Requirements: REF_01_REQ.md, REF_22_PROJECT.md.*
