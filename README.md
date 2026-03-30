# xwdata

**Build data systems from any format, for any structure.**  
`xwdata` lets you load from one format, shape data into the structure you need, and save to another format through one API.

Use JSON, YAML, TOML, XML, and more as your input language, then model the result as maps, trees, graphs, or domain objects. This is useful for game save systems, data pipelines, config platforms, and runtime in-memory data services.

**Company:** eXonware.com · **Author:** eXonware Backend Team · **Email:** connect@exonware.com  

[![Status](https://img.shields.io/badge/status-beta-blue.svg)](https://exonware.com)
[![Python](https://img.shields.io/badge/python-3.12%2B-blue.svg)](https://www.python.org)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

---

## Install

| Install | What you get | When to use |
|---------|--------------|-------------|
| `pip install exonware-xwdata` | **Lite** - core only | Minimal footprint. |
| `pip install exonware-xwdata[lazy]` | **Lazy** - formats on first use | Development. |
| `pip install exonware-xwdata[full]` | **Full** - common formats pre-installed | Production or CI. |

---

## Quick start

```python
from exonware.xwdata import load_data, save_data

# Load from any format, save to any format; one API
data = load_data("input.json")   # or .yaml, .xml, etc.
data["key"] = "value"
save_data(data, "output.yaml")
```

XWNode for path navigation and graph work; async APIs; reference resolution. See [docs/](docs/) and [docs/GUIDE_01_USAGE.md](docs/GUIDE_01_USAGE.md) when present.

---

## Why developers use xwdata

- **One API, many formats** - stop rewriting loaders and converters for each format.
- **One model, many outputs** - build once, then serialize where it needs to go.
- **Practical architecture freedom** - use XML for game saves, TOML/JSON for graph configs, or mixed formats for DB bootstrap data.
- **In-memory and persisted flows** - use the same patterns for runtime objects and storage/export paths.

---

## What you get

| Area | What's in it |
|------|----------------|
| **Formats** | One API over 30+ formats via xwsystem; partial reads and typed loads. |
| **Data modeling** | Build maps, trees, graph-like layouts, and domain objects from the same source API. |
| **XWNode** | Path and graph operations on in-memory data. |
| **Semantics** | Copy-on-write, universal metadata, reference resolution. |
| **Async** | Async-first operations. |

---

## Docs and tests

- **Start:** [docs/INDEX.md](docs/INDEX.md) or [docs/](docs/).
- **Tests:** From repo root, follow the project's test layout.

---

## License and links

MIT - see [LICENSE](LICENSE). **Homepage:** https://exonware.com · **Repository:** https://github.com/exonware/xwdata  
Version: 0.9.0.10 | Updated: 31-Mar-2026

*Built with ❤️ by eXonware.com - Revolutionizing Python Development Since 2025*
