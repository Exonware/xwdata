# XWData Quick Reference

**Company:** eXonware.com  
**Version:** 0.0.1.3  
**Date:** 26-Oct-2025

---

## Installation

```bash
# Lite mode (core only)
pip install exonware-xwdata

# Lazy mode (auto-install on demand) - RECOMMENDED
pip install exonware-xwdata[lazy]

# Full mode (all dependencies)
pip install exonware-xwdata[full]
```

---

## Import

```python
# Main import
from exonware.xwdata import XWData

# With configuration
from exonware.xwdata import XWData, XWDataConfig

# All utilities
from exonware.xwdata import (
    XWData, XWDataConfig, DataFormat,
    load, from_native, parse
)
```

---

## Creating XWData

### From Native Python Data (Sync)

```python
# From dict
data = XWData({'name': 'Alice', 'age': 30})

# From list
data = XWData([1, 2, 3, 4, 5])

# With metadata
data = XWData(
    {'key': 'value'},
    metadata={'source': 'manual'}
)
```

### From Files (Async)

```python
import asyncio

async def load_file():
    # Auto-detect format
    data = await XWData.load('config.json')
    
    # With format hint
    data = await XWData.load('data.txt', format_hint='json')
    
    # With configuration
    config = XWDataConfig.fast()
    data = await XWData.load('large.json', config=config)
    
    return data

data = asyncio.run(load_file())
```

### From Content (Async)

```python
async def parse_content():
    content = '{"name": "Alice"}'
    data = await XWData.parse(content, format='json')
    return data

data = asyncio.run(parse_content())
```

### Multi-Source Merge

```python
# Merge multiple sources
data = XWData([
    {'base': 'config'},      # Dict
    'overrides.yaml',        # File path
    existing_data,           # Another XWData
    {'final': 'value'}       # Final overrides
], merge_strategy='deep')
```

---

## Navigation

### Get Values (Async)

```python
import asyncio

async def navigate():
    data = XWData({
        'users': [
            {'name': 'Alice', 'age': 30},
            {'name': 'Bob', 'age': 25}
        ]
    })
    
    # Get nested values
    name = await data.get('users.0.name')      # 'Alice'
    age = await data.get('users.1.age')        # 25
    
    # With default
    email = await data.get('users.0.email', default='N/A')  # 'N/A'
    
    # Check existence
    has_email = await data.exists('users.0.email')  # False

asyncio.run(navigate())
```

### Get Native Data (Sync)

```python
data = XWData({'key': 'value'})

# Get native Python object
native = data.to_native()  # {'key': 'value'}
```

---

## Modification (Copy-on-Write)

### Set Values (Async)

```python
async def modify():
    data = XWData({'counter': 0})
    
    # Set returns new instance (COW)
    data = await data.set('counter', 1)
    data = await data.set('nested.key', 'value')
    
    # Chain operations
    data = await (await data.set('a', 1)).set('b', 2)

asyncio.run(modify())
```

### Delete Values (Async)

```python
async def remove():
    data = XWData({'keep': 'this', 'remove': 'that'})
    
    # Delete returns new instance (COW)
    data = await data.delete('remove')
    
    has_remove = await data.exists('remove')  # False

asyncio.run(remove())
```

---

## Operations

### Merge (Async)

```python
async def merge_data():
    data1 = XWData({'a': 1, 'b': 2})
    data2 = XWData({'b': 3, 'c': 4})
    
    # Deep merge (default)
    merged = await data1.merge(data2, strategy='deep')
    
    native = merged.to_native()  # {'a': 1, 'b': 3, 'c': 4}

asyncio.run(merge_data())
```

### Transform (Async)

```python
async def transform_data():
    data = XWData({'name': 'alice'})
    
    # Transform with function
    transformed = await data.transform(
        lambda d: {k: v.upper() for k, v in d.items()}
    )
    
    name = await transformed.get('name')  # 'ALICE'

asyncio.run(transform_data())
```

---

## Serialization

### Serialize to String/Bytes (Async)

```python
async def serialize():
    data = XWData({'key': 'value'})
    
    # To JSON
    json_str = await data.serialize('json')
    
    # To YAML
    yaml_str = await data.serialize('yaml')
    
    # To XML
    xml_str = await data.serialize('xml')

asyncio.run(serialize())
```

### Save to File (Async)

```python
async def save():
    data = XWData({'key': 'value'})
    
    # Format auto-detected from extension
    await data.save('output.json')
    await data.save('output.yaml')
    
    # Explicit format
    await data.save('output.txt', format='json')
    
    # With options
    await data.save('output.json', indent=4, overwrite=True)

asyncio.run(save())
```

---

## Configuration

### Using Presets

```python
from exonware.xwdata import XWDataConfig

# Default (balanced)
config = XWDataConfig.default()

# High security (untrusted data)
config = XWDataConfig.strict()

# High performance (speed)
config = XWDataConfig.fast()

# Development (debugging)
config = XWDataConfig.development()

# Use with operations
data = await XWData.load('file.json', config=config)
```

### Custom Configuration

```python
from exonware.xwdata import (
    XWDataConfig, SecurityConfig, PerformanceConfig,
    CacheStrategy, COWMode
)

config = XWDataConfig(
    security=SecurityConfig(
        max_file_size_mb=50,
        enable_path_validation=True
    ),
    performance=PerformanceConfig(
        cache_strategy=CacheStrategy.TWO_TIER,
        enable_caching=True,
        cache_size=5000
    ),
    cow=COWConfig(mode=COWMode.ENABLED)
)

data = await XWData.load('data.json', config=config)
```

---

## Streaming

### Stream Load Large Files (Async)

```python
async def stream_large_file():
    # Stream JSONL file
    async for chunk in XWData.stream_load('large_data.jsonl'):
        # Process each chunk
        process(chunk)

asyncio.run(stream_large_file())
```

---

## Error Handling

```python
from exonware.xwdata import (
    XWDataError, XWDataParseError, 
    XWDataIOError, XWDataSecurityError
)

async def handle_errors():
    try:
        data = await XWData.load('file.json')
    except XWDataFileNotFoundError as e:
        print(f"File not found: {e}")
    except XWDataParseError as e:
        print(f"Parse error: {e}")
    except XWDataSecurityError as e:
        print(f"Security violation: {e}")
    except XWDataError as e:
        print(f"General error: {e}")

asyncio.run(handle_errors())
```

---

## Common Patterns

### Configuration Loading with Overrides

```python
async def load_config():
    # Load base config, then merge overrides
    config = XWData([
        'config/base.yaml',
        'config/production.yaml',
        {'runtime_override': True}
    ], merge_strategy='deep')
    
    return config

config = asyncio.run(load_config())
```

### Batch Processing

```python
async def batch_process():
    files = ['data1.json', 'data2.json', 'data3.json']
    
    # Load all concurrently
    tasks = [XWData.load(f) for f in files]
    results = await asyncio.gather(*tasks)
    
    # Merge all
    first, *rest = results
    for other in rest:
        first = await first.merge(other)
    
    return first

combined = asyncio.run(batch_process())
```

---

## Tips & Best Practices

1. **Use async operations** for I/O (load, save, serialize)
2. **Use COW semantics** for safe concurrent access
3. **Configure caching** for repeated operations
4. **Use format strategies** to extend format support
5. **Enable lazy mode** for development (`pip install exonware-xwdata[lazy]`)
6. **Use full mode** for production (`pip install exonware-xwdata[full]`)

---

For more examples, see `examples/` directory.

