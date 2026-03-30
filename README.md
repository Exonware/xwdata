# xwdata

**Format-agnostic data engine with XWNode.** Load and save across many formats (via xwsystem), navigate paths and graphs on `XWNode`, copy-on-write semantics, async-first. Docs in `docs/`.

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

## What you get

| Area | What's in it |
|------|----------------|
| **Formats** | One API over 30+ formats via xwsystem; partial reads, typed loads. |
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
Version: 0.9.0.9 | Updated: 30-Mar-2026

*Built with ❤️ by eXonware.com - Revolutionizing Python Development Since 2025*
