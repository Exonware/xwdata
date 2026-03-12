# xwdata — Usage Guide

**Last Updated:** 07-Feb-2026

How to use xwdata (output of GUIDE_41_DOCS). See [REF_01_REQ.md](REF_01_REQ.md), [REF_22_PROJECT.md](REF_22_PROJECT.md), [REF_14_DX.md](REF_14_DX.md) (key code), [REF_15_API.md](REF_15_API.md).

---

## Quick start (REF_01_REQ sec. 5–6)

One API for all formats: create or load, navigate with paths, save to any format.

```python
from exonware.xwdata import XWData
import asyncio

# From native data
data = XWData({'name': 'Alice', 'age': 30})

# Load → modify → save (async)
async def main():
    data = await XWData.load('config.json')
    data = await data.set('api.timeout', 30)
    await data.save('config.yaml')  # JSON → YAML

asyncio.run(main())
```

---

## Easy vs advanced (REF_15_API)

- **Easy:** `XWData(dict)`, `await XWData.load(path)`, `await data.get/set/delete(path)`, `await data.save(path)`.
- **Advanced:** Multi-source merge, reference config, metadata/COW config, streaming, caching, batch ops, format conversion pipeline. See [REF_15_API.md](REF_15_API.md).

---

## Examples and benchmarks

- **Examples:** [examples/](../../examples/) — start with [basic_usage.py](../../examples/basic_usage.py); see [examples/README.md](../../examples/README.md).
- **Benchmarks:** [benchmarks/](../../benchmarks/) and [REF_54_BENCH.md](REF_54_BENCH.md).

---

## Documentation

| Doc | Purpose |
|-----|---------|
| [REF_01_REQ.md](REF_01_REQ.md) | Requirements (vision, scope, API expectations) |
| [REF_12_IDEA.md](REF_12_IDEA.md) | Idea context and evaluation |
| [REF_11_COMP.md](REF_11_COMP.md) | Compliance stance and standards |
| [REF_22_PROJECT.md](REF_22_PROJECT.md) | Project vision, goals, FR/NFR, milestones |
| [REF_13_ARCH.md](REF_13_ARCH.md) | Architecture and boundaries |
| [REF_14_DX.md](REF_14_DX.md) | Developer experience, key code (1–3 lines) |
| [REF_15_API.md](REF_15_API.md) | Public API reference |
| [REF_21_PLAN.md](REF_21_PLAN.md) | Milestones and roadmap |
| [INDEX.md](INDEX.md) | Docs index |
| [REF_51_TEST.md](REF_51_TEST.md) | Test layers and how to run tests |
| [REF_54_BENCH.md](REF_54_BENCH.md) | Benchmark scripts and evidence |

Getting started (legacy): Key points from former GET_STARTED and TUTORIAL_QUICK_START are reflected in this guide and in [examples/](../../examples/).

---

## Troubleshooting

- **bcrypt / PyO3 with coverage:** If you see `ImportError: PyO3 modules compiled for CPython 3.8 or older may only be initialized once` when running tests *with* coverage, bcrypt (xwsystem dependency) may be built for a different Python. Run tests without coverage: `python -m pytest tests/ -v`. See [changes/CHANGE_20250126_BCRYPT_WORKAROUND.md](changes/CHANGE_20250126_BCRYPT_WORKAROUND.md) for workarounds.

---

*Per GUIDE_00_MASTER and GUIDE_41_DOCS.*
