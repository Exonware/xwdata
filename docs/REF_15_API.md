# xwdata — API Reference (REF_15_API)

**Library:** exonware-xwdata  
**Last Updated:** 07-Feb-2026  
**Requirements source:** [REF_01_REQ.md](REF_01_REQ.md) sec. 6  
**Producing guide:** [GUIDE_15_API.md](../../docs/guides/GUIDE_15_API.md)

API reference for xwdata (output of GUIDE_15_API). See REF_22_PROJECT and REF_13_ARCH for overview. Legacy full API text was in _archive/API_REFERENCE.md (value moved 07-Feb-2026 to this REF and [logs/ARCHIVE_VALUE_CAPTURE_XWDATA.md](logs/ARCHIVE_VALUE_CAPTURE_XWDATA.md)).

---

## Scope (from REF_01_REQ sec. 6)

### Main entry points / “key code”

| Area | Symbols |
|------|--------|
| **Facade** | `XWData`, `load`, `from_native`, `parse` |
| **Builder** | `XWDataBuilder` |
| **Shortcuts** | `quick_load`, `quick_save`, `quick_convert`, `quick_get`, `quick_set`, `quick_delete`, `quick_merge`, `quick_diff`, `quick_patch`, `quick_validate` |
| **Format helpers** | `to_json`, `to_yaml`, `to_xml`, `to_toml`, `to_csv`, `from_json`, `from_yaml`, `from_xml`, `from_toml`, `from_csv` |
| **Config** | `XWDataConfig`, `SecurityConfig`, `PerformanceConfig`, `ReferenceConfig`, `MetadataConfig`, `COWConfig` — presets: default, strict, fast, development |
| **Operations** | `merge_data`, `diff_data`, `patch_data`, `batch_convert`, `batch_validate`, `batch_transform`; `MergeStrategy`, `DiffMode`, `PatchOperation`, `DataMerger`, `DataDiffer`, `DataPatcher`, `BatchOperations` |
| **Format conversion** (when available) | `FormatConverter`, `convert_format`, `ConversionPipeline`, `FormatValidator` |
| **Optional BaaS** | `XWDataBaaSFacade` (when available) |
| **Extension** | `XWDataEngine`, `XWDataNode`, `NodeFactory`, `FormatStrategyRegistry` |
| **Errors** | `XWDataError` hierarchy (e.g. `XWDataSecurityError`, `XWDataParseError`, `XWDataIOError`) |
| **Enums** | `DataFormat`, `EngineMode`, `CacheStrategy`, `ReferenceResolutionMode`, `MergeStrategy`, `SerializationMode`, `COWMode`, `MetadataMode`, `ValidationMode`, `PerformanceTrait`, `SecurityTrait` |

### Easy (1–3 lines) vs advanced

- **Easy:** `XWData(dict)`, `await XWData.load(path)`, `await data.get/set/delete(path)`, `await data.save(path)`.
- **Advanced:** Multi-source merge, reference config, metadata/COW config, streaming, caching, batch ops, format conversion pipeline, BaaS facade.

### Not in public API (from REF_01_REQ sec. 6)

Internal engine wiring, format-strategy internals, cache keys; node/edge strategies stay in xwnode; concrete schema/entity/action implementations are out of scope.

### xwsystem reuse

**Caching:** Engine uses **xwsystem** `create_cache` for the global xwdata cache (configurable capacity/namespace). **JSON:** All JSON parsing in the engine (including the hyper-fast path for tiny `.json` files) uses **get_serializer(JsonSerializer)** so the same parser stack and flyweight as xwschema, xwstorage.connect json_utils, and xwsystem indexing/catalog are used.

---

*Per GUIDE_00_MASTER and GUIDE_15_API.*
