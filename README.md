# xwdata

**Build data systems from any format, for any structure.**  
`xwdata` lets you load from one format, shape data into the structure you need, and save to another format through one API.

Use JSON, YAML, TOML, XML, and more as your input language, then model the result as maps, trees, graphs, or domain objects. This is useful for game save systems, data pipelines, config platforms, and runtime in-memory data services.

**Company:** eXonware.com · **Author:** eXonware Backend Team · **Email:** connect@exonware.com  

[![Status](https://img.shields.io/badge/status-beta-blue.svg)](https://exonware.com)
[![Python](https://img.shields.io/badge/python-3.12%2B-blue.svg)](https://www.python.org)
[![License](https://img.shields.io/badge/license-Apache%202.0-blue.svg)](LICENSE)

---

## 📦 Install

| Install | What you get | When to use |
|---------|--------------|-------------|
| `pip install exonware-xwdata` | **Lite** - core only | Minimal footprint. |
| `pip install exonware-xwdata[lazy]` | **Lazy** - formats on first use | Development. |
| `pip install exonware-xwdata[full]` | **Full** - common formats pre-installed | Production or CI. |

---

## 🚀 Quick start

```python
from exonware.xwdata import load_data, save_data

# Load from any format, save to any format; one API
data = load_data("input.json")   # or .yaml, .xml, etc.
data["key"] = "value"
save_data(data, "output.yaml")
```

XWNode for path navigation and graph work; async APIs; reference resolution. See [docs/](docs/) and [docs/GUIDE_01_USAGE.md](docs/GUIDE_01_USAGE.md) when present.

---

## 🎯 Why developers use xwdata

- **One API, many formats** - stop rewriting loaders and converters for each format.
- **One model, many outputs** - build once, then serialize where it needs to go.
- **Practical architecture freedom** - use XML for game saves, TOML/JSON for graph configs, or mixed formats for DB bootstrap data.
- **In-memory and persisted flows** - use the same patterns for runtime objects and storage/export paths.

---

## ✨ What you get

| Area | What's in it |
|------|----------------|
| **Formats** | One API over 30+ formats via xwsystem; partial reads and typed loads. |
| **Data modeling** | Build maps, trees, graph-like layouts, and domain objects from the same source API. |
| **XWNode** | Path and graph operations on in-memory data. |
| **Semantics** | Copy-on-write, universal metadata, reference resolution. |
| **Async** | Async-first operations. |

---

## 🌐 Ecosystem functional contributions

`xwdata` is the data interchange layer; other XW libraries provide structure, querying, validation, and persistence around those data flows.
You can use `xwdata` standalone for multi-format load/transform/save workflows.
Adding more XW libraries is optional and mostly beneficial for enterprise and mission-critical data infrastructure where you need full control of validation, query, and persistence layers.

| Supporting XW lib | What it provides to xwdata | Functional requirement it satisfies |
|------|----------------|----------------|
| **XWSystem** | Core serializer/runtime infrastructure used for format handling and shared utilities. | One stable data I/O foundation across formats and environments. |
| **XWNode** | Path navigation, graph/tree-aware operations, and structure manipulation. | Complex in-memory structure workflows beyond flat dictionaries. |
| **XWSchema** | Validation contracts applied to loaded/transformed payloads. | Data quality enforcement during ingest/transform/export stages. |
| **XWQuery** | Query and projection over in-memory structured datasets. | Declarative filtering/transformation without custom traversal code. |
| **XWEntity** | Domain model integration when raw data becomes typed entities. | Bridge from flexible data payloads to domain-driven objects. |
| **XWStorage** | Durable persistence destination/source for transformed datasets. | End-to-end pipelines from format conversion to persistent storage. |

This gives `xwdata` a practical edge over format-only libraries: it connects parsing, structure, validation, query, and persistence in one workflow path.

---

## 📖 Docs and tests

- **Start:** [docs/INDEX.md](docs/INDEX.md) or [docs/](docs/).
- **Tests:** From repo root, follow the project's test layout.

---

## 📜 License and links

Apache-2.0 - see [LICENSE](LICENSE). **Homepage:** https://exonware.com · **Repository:** https://github.com/exonware/xwdata  

## ⏱️ Async Support

<!-- async-support:start -->
- xwdata includes asynchronous execution paths in production code.
- Source validation: 181 async def definitions and 216 await usages under src/.
- Use async APIs for I/O-heavy or concurrent workloads to improve throughput and responsiveness.
<!-- async-support:end -->
Version: 0.9.0.15 | Updated: 10-Apr-2026

*Built with ❤️ by eXonware.com - Revolutionizing Python Development Since 2025*
