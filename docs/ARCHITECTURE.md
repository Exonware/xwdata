# XWData Architecture

**Company:** eXonware.com  
**Author:** Eng. Muhammad AlShehri  
**Version:** 0.0.1.3  
**Date:** 26-Oct-2025

---

## Overview

xwdata uses a **pure engine pattern** inspired by xwquery, orchestrating xwsystem serialization, XWNode navigation, and xwdata-specific features through a single intelligent `XWDataEngine`.

## Architecture Diagram

```
┌──────────────────────────────────────────────────────────────┐
│                    XWData (Facade)                            │
│  - Multi-type __init__ (dict/list/path/XWData/merge)         │
│  - Fluent API (get/set/delete/merge/transform)              │
│  - Async operations                                          │
└────────────────────────┬─────────────────────────────────────┘
                         │
                         ▼
┌──────────────────────────────────────────────────────────────┐
│                 XWDataEngine (Orchestrator)                   │
│  ┌────────────────────────────────────────────────────────┐  │
│  │ Composes:                                              │  │
│  │ - XWSerializer (xwsystem) ← REUSE!                    │  │
│  │ - FormatStrategyRegistry                              │  │
│  │ - MetadataProcessor                                   │  │
│  │ - ReferenceResolver                                   │  │
│  │ - CacheManager                                        │  │
│  │ - NodeFactory                                         │  │
│  └────────────────────────────────────────────────────────┘  │
└──┬───────────────┬──────────────┬────────────────┬──────────┘
   │               │              │                │
   ▼               ▼              ▼                ▼
┌─────────┐  ┌──────────┐  ┌──────────┐   ┌──────────────┐
│XWSerializer│Format     │Metadata    │   │Reference     │
│(xwsystem) ││Strategies ││Processor   │   │Resolver      │
│24+ formats││JSON, XML, ││Universal   │   │Circular      │
│           ││YAML, etc. ││metadata    │   │detection     │
└─────────┘  └──────────┘  └──────────┘   └──────────────┘
     │
     ▼
┌──────────┐
│XWDataNode│
│Extends   │
│XWNode    │
│+ COW     │
│+ Metadata│
└──────────┘
```

## Key Components

### 1. XWData (Facade)
**File:** `src/exonware/xwdata/facade.py`

- User-facing API
- Multi-type constructor
- Fluent method chaining
- Delegates to engine

### 2. XWDataEngine (Orchestrator)
**File:** `src/exonware/xwdata/data/engine.py`

- Core orchestration
- Composes all services
- Lazy initialization
- Performance monitoring

### 3. XWDataNode (Smart Node)
**File:** `src/exonware/xwdata/data/node.py`

- Extends XWNode from xwnode
- Copy-on-write semantics
- Format metadata
- Reference tracking

### 4. Format Strategies (Lightweight)
**Directory:** `src/exonware/xwdata/data/strategies/`

- JSON: 50 lines (metadata extraction, $ref detection)
- XML: 50 lines (attribute handling, @href detection)
- YAML: 50 lines (anchor detection, multi-doc support)

**Key:** Strategies do NOT serialize - they provide format-specific metadata logic only!

### 5. Services

**Metadata System:**
- `MetadataProcessor` - Orchestrates extraction
- `MetadataExtractor` - Converts format-specific → universal
- `UniversalMetadata` - Format-agnostic metadata

**Reference System:**
- `ReferenceDetector` - Finds references ($ref, @href, *anchor)
- `ReferenceResolver` - Loads and resolves external files
- Circular dependency detection

**Caching System:**
- `CacheManager` - Coordinates caching
- `ParseCache` - Caches parse operations
- `SerializeCache` - Caches serialize operations
- LRU eviction policy

---

## Design Principles

### 1. Reuse, Don't Duplicate
✅ Uses xwsystem.serialization.XWSerializer (24+ formats)  
✅ Uses xwnode.XWNode (navigation and graphs)  
❌ NO reimplementation of serialization logic  

### 2. Engine Orchestration
✅ Single engine coordinates all operations  
✅ Lazy initialization of components  
✅ Composition over inheritance  

### 3. Async-First
✅ All I/O operations are async  
✅ Concurrent loading support  
✅ Async generators for streaming  

### 4. Copy-on-Write
✅ Immutable by default  
✅ Safe concurrent access  
✅ Efficient structural sharing  

### 5. Extensibility
✅ Plugin format strategies  
✅ Custom serializers in `serialization/`  
✅ Configurable services  

---

## Data Flow

### Load Pipeline

```
1. User calls: await XWData.load('config.json')
              ↓
2. Engine validates path (security)
              ↓
3. XWSerializer deserializes (xwsystem - reuse!)
              ↓
4. FormatStrategy extracts metadata (JSON-specific)
              ↓
5. ReferenceDetector finds $ref patterns
              ↓
6. MetadataProcessor creates UniversalMetadata
              ↓
7. NodeFactory creates XWDataNode (XWNode + COW)
              ↓
8. CacheManager caches result
              ↓
9. Return XWData instance to user
```

### Save Pipeline

```
1. User calls: await data.save('config.yaml')
              ↓
2. Engine validates path (security)
              ↓
3. Node extracts native data
              ↓
4. XWSerializer serializes to YAML (xwsystem)
              ↓
5. Write file
```

---

## Extension Points

### Adding New Format Strategy

```python
# data/strategies/toml.py
from ...base import AFormatStrategy

class TOMLFormatStrategy(AFormatStrategy):
    def __init__(self):
        super().__init__()
        self._name = 'toml'
        self._extensions = ['toml']
    
    async def extract_metadata(self, data, **opts):
        # TOML-specific metadata
        return {'format': 'toml', 'has_tables': True}
    
    async def detect_references(self, data, **opts):
        # TOML-specific references
        return []

# Auto-registered by FormatStrategyRegistry!
```

### Adding Extended Serializer

```python
# serialization/json5.py
from ..base import AXWDataSerializer

class JSON5Serializer(AXWDataSerializer):
    def __init__(self):
        self._name = 'json5'
        self._extensions = ['json5']
    
    async def serialize(self, data, **opts):
        import json5
        return json5.dumps(data)
    
    async def deserialize(self, content, **opts):
        import json5
        return json5.loads(content)

# Auto-registered by XWDataSerializerRegistry!
```

---

## Performance Optimizations

1. **Lazy Initialization** - Components created only when needed
2. **LRU Caching** - Parse and serialize caches
3. **Structural Hashing** - Fast equality checks
4. **Object Pooling** - Node reuse for hot paths
5. **Async Operations** - Non-blocking I/O
6. **xwsystem Integration** - Leverages optimized serializers

---

## Security Features

1. **Path Validation** - Prevents path traversal
2. **File Size Limits** - DoS protection
3. **Nesting Depth Limits** - Stack overflow protection
4. **Sanitization** - Input validation
5. **Circular Reference Detection** - Prevents infinite loops

---

For more details, see:
- **[QUICK_REFERENCE.md](QUICK_REFERENCE.md)** - API quick reference
- **[FORMAT_STRATEGIES.md](FORMAT_STRATEGIES.md)** - Format strategy guide
- **[ASYNC_GUIDE.md](ASYNC_GUIDE.md)** - Async patterns

