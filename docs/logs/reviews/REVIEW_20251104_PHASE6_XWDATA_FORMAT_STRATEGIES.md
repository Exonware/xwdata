# Review: Phase 6 — xwdata format strategies (no migration needed)

**Date:** 2025-11-04  
**Conclusion:** xwdata already uses registered xwsystem codecs; no migration required.  
**Source:** _archive/PHASE_6_XWDATA_ANALYSIS.md (value moved 07-Feb-2026)

---

## Scope

Whether xwdata format strategies (JSONFormatStrategy, XMLFormatStrategy, etc.) should be migrated into a universal codec registry.

## Finding

xwdata format strategies are **metadata processors**, not serializers. They:

1. **Extract format-specific metadata** (reserved chars, schema info, semantics).
2. **Detect format-specific references** (e.g. JSON $ref, XML @href, YAML anchors).
3. **Map format types to universal types** (e.g. JSON string → str).

Actual serialization is **delegated to xwsystem serializers** (already registered). So:

- **Separation of concerns:** Serialization = xwsystem codecs; metadata = xwdata strategies.
- **No duplication:** xwdata reuses xwsystem serializers.
- **Correct architecture:** xwdata strategies work *with* codecs, not *as* codecs.

## Resolution

No migration needed. UniversalCodecRegistry holds xwsystem serializers and xwformats codecs; xwdata format strategies remain as metadata layer above them.

---

*Per GUIDE_35_REVIEW; review outcome preserved in logs/reviews.*
