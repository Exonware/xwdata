# Change: docs root — REF/INDEX/GUIDE only (07-Feb-2026)

**Per:** GUIDE_41_DOCS; user request to have only standard docs (REF_*, INDEX, GUIDE_01_USAGE) in docs root; everything else in _archive or logs.

## xwdata

- **Moved to _archive:** `docs/README.md` (was pytest cache content) → `_archive/README_PYTEST_CACHE_MISPLACED.md`.
- **Moved to logs:** `docs/AGENT_BRIEF_XWDATA.md` → `logs/AGENT_BRIEF_XWDATA.md`. Value unchanged; agents/maintainers context lives in logs. INDEX "Evidence (logs)" and REF_35_REVIEW link to `logs/AGENT_BRIEF_XWDATA.md`.
- **Deleted from docs root:** README.md, AGENT_BRIEF_XWDATA.md (after copy in _archive/logs).

**Docs root now:** INDEX.md, REF_01_REQ.md through REF_54_BENCH.md, GUIDE_01_USAGE.md only (+ _archive/, changes/, logs/).

## xwschema

- **Moved to _archive:** `docs/INSTALL_DEPENDENCIES.md` → `_archive/INSTALL_DEPENDENCIES.md`. Value merged into GUIDE_01_USAGE.md sec.  Install.
- **Moved to _archive:** `docs/README.md` (was pytest cache content) → `_archive/README_PYTEST_CACHE_MISPLACED.md`.
- **Deleted from docs root:** INSTALL_DEPENDENCIES.md, README.md.
- **INDEX:** "Other" no longer links to INSTALL_DEPENDENCIES in root; _archive and GUIDE_01_USAGE referenced.

---

*Per GUIDE_41_DOCS. Standard: only REF_*, INDEX.md, GUIDE_01_USAGE.md in docs root.*
