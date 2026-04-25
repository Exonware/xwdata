# Developer Experience Reference — xwdata (REF_14_DX)

**Library:** exonware-xwdata  
**Last Updated:** 07-Feb-2026  
**Requirements source:** [REF_01_REQ.md](REF_01_REQ.md) sec. 5–6  
**Producing guide:** [GUIDE_14_DX.md](../../docs/guides/GUIDE_14_DX.md)

---

## Purpose

DX contract for xwdata: happy paths, “key code,” and ergonomics. Filled from REF_01_REQ.

---

## Key code (1–3 lines)

| Task | Code |
|------|------|
| Create from native data | `data = XWData({'name': 'Alice', 'age': 30})` |
| Load from file | `data = await XWData.load('config.json')` |
| Get by path | `value = await data.get('api.timeout')` |
| Set (copy-on-write) | `data = await data.set('api.timeout', 30)` |
| Save to any format | `await data.save('config.yaml')`  # JSON → YAML |

---

## Developer persona (from REF_01_REQ sec. 5)

Developer consuming xwdata: create or load data in 1–3 lines; navigate and mutate with path API (get/set/delete); save to any format. Advanced: config presets (default/strict/fast/development), reference resolution, merge/diff/patch, batch operations.

---

## Easy vs advanced

| Easy (1–3 lines) | Advanced |
|------------------|----------|
| `XWData(dict)`, `await XWData.load(path)`, `await data.get/set/delete(path)`, `await data.save(path)` | Multi-source merge, reference config, metadata/COW config, streaming, caching, batch ops, format conversion pipeline, BaaS facade (optional). |

---

## Main entry points (from REF_01_REQ sec. 6)

- **Facade:** `XWData`, `load`, `from_native`, `parse`
- **Shortcuts:** `quick_load`, `quick_save`, `quick_convert`, `quick_get`, `quick_set`, `quick_delete`, `quick_merge`, `quick_diff`, `quick_patch`, `quick_validate`
- **Format helpers:** `to_json`, `from_yaml`, etc.
- **Config:** `XWDataConfig`, presets: default, strict, fast, development
- **Operations:** `merge_data`, `diff_data`, `patch_data`, `batch_convert`, `batch_validate`, `batch_transform`
- **Extension:** `XWDataEngine`, `XWDataNode`, `NodeFactory`, `FormatStrategyRegistry`

---

## Usability expectations (from REF_01_REQ sec. 8)

Single facade API, README and examples, config presets, typed errors (XWDataError hierarchy); docs under docs/ (REF_*, architecture, changes, logs).

**Examples:** [examples/](../../examples/) — start with [basic_usage.py](../../examples/basic_usage.py); see [examples/README.md](../../examples/README.md).

**Consumers:** xwschema, xwaction, xwentity, xwstorage.connect, xwquery — see [REF_22_PROJECT](REF_22_PROJECT.md) traceability.

---

*See [REF_01_REQ.md](REF_01_REQ.md), [REF_15_API.md](REF_15_API.md), and [REF_21_PLAN.md](REF_21_PLAN.md) for milestones. Per GUIDE_14_DX.*
