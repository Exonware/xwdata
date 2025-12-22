# XWData Ecosystem Integration Guide

> **Complete implementation of the XWData Enhancement Plans**
>
> This guide covers the integration between XWData, XWQuery, XWNode, and XWSystem.

## Overview

The XWData ecosystem provides three major enhancements:

1. **XWData + XWQuery Integration** - Query data files with multiple formats
2. **XWQuery Format Auto-Detection** - Automatic query language detection
3. **XWData Format Detection Metadata** - Transparent format detection information

## Table of Contents

- [Quick Start](#quick-start)
- [Plan 1: XWData + XWQuery Integration](#plan-1-xwdata--xwquery-integration)
- [Plan 2: XWQuery Format Auto-Detection](#plan-2-xwquery-format-auto-detection)
- [Plan 3: Format Detection Metadata](#plan-3-format-detection-metadata)
- [Complete Workflows](#complete-workflows)
- [Best Practices](#best-practices)
- [Troubleshooting](#troubleshooting)

---

## Quick Start

### Installation

```bash
# Install XWData with query support
pip install exonware-xwdata exonware-xwquery

# Or install the full ecosystem
pip install exonware-xwdata[full]
```

### Basic Example

```python
from exonware.xwdata import XWData

# Load data (auto-detects JSON format)
data = await XWData.load('users.json')

# Check what format was detected
print(f"Format: {data.get_detected_format()}")
print(f"Confidence: {data.get_detection_confidence():.0%}")

# Query the data (auto-detects SQL)
result = await data.query("SELECT * FROM users WHERE age > 25")

# Save as different format
await data.save('users.yaml')
```

---

## Plan 1: XWData + XWQuery Integration

### Method 1: `as_xwnode()` - For Power Users

Get the underlying XWNode for advanced operations with XWQuery, XWSchema, and other libraries.

```python
from exonware.xwdata import XWData
from exonware.xwquery import XWQuery

# Load data
data = await XWData.load('products.json')

# Get XWNode for advanced operations
node = data.as_xwnode()

# Use with XWQuery directly
result = XWQuery.execute(
    "SELECT * FROM products WHERE price > 100",
    node,
    format='sql'
)
```

**When to use:**
- You need full control over XWQuery configuration
- Working with multiple XW libraries (xwschema, xwentity, etc.)
- Building complex query pipelines
- Need to cache and reuse the node

### Method 2: `query()` - Convenience Wrapper

Single-call querying without extracting the XWNode first.

```python
from exonware.xwdata import XWData

# Load data
data = await XWData.load('users.json')

# Query directly (SQL - auto-detected)
result = await data.query("SELECT * FROM users WHERE age > 18")

# Query with JMESPath
result = await data.query(
    "users[?age > `18`].name",
    format='jmespath'
)

# Query with GraphQL
result = await data.query(
    "{ users(filter: {age: {gt: 18}}) { name email } }",
    format='graphql'
)
```

**When to use:**
- Quick one-off queries
- Simple data filtering and transformation
- Prototyping and exploration
- Jupyter notebooks and scripts

### Supported Query Formats

```python
# SQL (default, auto-detected)
await data.query("SELECT * FROM users WHERE active = true")

# Cypher (graph queries)
await data.query(
    "MATCH (u:User)-[:FOLLOWS]->(f) RETURN u.name, f.name",
    format='cypher'
)

# JMESPath (JSON path queries)
await data.query("users[?age > `25`].{name: name, email: email}")

# JSONPath
await data.query("$.users[?(@.age > 25)].name", format='jsonpath')

# XPath (for XML data)
await data.query("//user[@age>25]/name", format='xpath')

# GraphQL
await data.query("""
    query GetActiveUsers {
        users(filter: {active: true}) {
            name
            email
        }
    }
""", format='graphql')

# SPARQL (for RDF/semantic data)
await data.query("""
    PREFIX foaf: <http://xmlns.com/foaf/0.1/>
    SELECT ?name WHERE { ?person foaf:name ?name }
""", format='sparql')
```

### Error Handling

```python
from exonware.xwdata import XWData

try:
    data = await XWData.load('data.json')
    result = await data.query("SELECT * FROM items")
except ImportError as e:
    print("XWQuery not installed. Install with: pip install exonware-xwquery")
except ValueError as e:
    print(f"No XWNode available: {e}")
```

---

## Plan 2: XWQuery Format Auto-Detection

XWQuery automatically detects the query language from the query string using a multi-stage pipeline.

### How Auto-Detection Works

```python
from exonware.xwquery import detect_query_format

# SQL query
format, confidence = detect_query_format("SELECT * FROM users")
print(f"{format} ({confidence:.0%})")  # SQL (95%)

# Cypher query
format, confidence = detect_query_format("MATCH (u:User) RETURN u.name")
print(f"{format} ({confidence:.0%})")  # Cypher (95%)

# JMESPath query
format, confidence = detect_query_format("users[?age > `25`]")
print(f"{format} ({confidence:.0%})")  # JMESPath (90%)
```

### Multi-Stage Detection Pipeline

1. **Stage 1: Quick Keyword Check** (fast path for 80-90% of queries)
   - Checks for format-specific keywords
   - Returns immediately if confidence ≥ 90%

2. **Stage 2: Pattern Matching** (structure analysis)
   - Uses regex to detect query patterns
   - Handles complex query structures

3. **Stage 3: Keyword Frequency Analysis** (statistical)
   - Analyzes keyword distribution
   - Weights by keyword uniqueness

4. **Stage 4: Confidence Scoring** (ranking)
   - Combines all signals
   - Returns best match with confidence score

### Using Auto-Detection

```python
from exonware.xwdata import XWData

data = await XWData.load('data.json')

# Auto-detect query format (default)
result = await data.query("SELECT * FROM users WHERE age > 25")

# Disable auto-detection (explicit format required)
result = await data.query(
    "SELECT * FROM users",
    format='sql',
    auto_detect=False  # Only when called via XWQuery.execute directly
)
```

### Confidence Thresholds

```python
from exonware.xwquery.parsers.format_detector import QueryFormatDetector

# Create detector with custom threshold
detector = QueryFormatDetector(confidence_threshold=0.85)

# Check if confident
query = "SELECT * FROM users"
if detector.is_confident(query):
    format, confidence = detector.detect_format(query)
    print(f"Detected: {format} ({confidence:.0%})")
else:
    print("Low confidence - please specify format explicitly")
```

### Viewing All Candidates

```python
from exonware.xwquery.parsers.format_detector import QueryFormatDetector

detector = QueryFormatDetector()

query = "SELECT * FROM users WHERE age > 25"
candidates = detector.detect_format_with_candidates(query)

print("Format candidates:")
for format_name, confidence in candidates.items():
    print(f"  {format_name}: {confidence:.0%}")

# Output:
#   SQL: 95%
#   SPARQL: 30%
#   GraphQL: 10%
```

### Fallback Behavior

When confidence is low (< 80%), XWQuery:
1. Logs a warning
2. Suggests using explicit `format=` parameter
3. Falls back to SQL (default)

```python
# Example of low-confidence warning in logs
# WARNING: Low confidence format detection (65%).
#          Consider specifying format explicitly with format='sql' parameter.
```

---

## Plan 3: Format Detection Metadata

XWData exposes format detection metadata for transparency and debugging.

### Getting Detection Information

```python
from exonware.xwdata import XWData

data = await XWData.load('config.json')

# Get detected format
format_name = data.get_detected_format()
print(f"Format: {format_name}")  # JSON

# Get confidence score
confidence = data.get_detection_confidence()
print(f"Confidence: {confidence:.0%}")  # 95%

# Get complete detection info
info = data.get_detection_info()
print(info)
```

Output:
```python
{
    'detected_format': 'JSON',
    'detection_confidence': 0.95,
    'detection_method': 'extension',
    'format_candidates': {
        'JSON': 0.95,
        'YAML': 0.20,
        'XML': 0.05
    }
}
```

### Detection Methods

1. **Extension-based** - Most common and reliable
   ```python
   data = await XWData.load('config.json')  # .json extension
   assert data.get_detection_info()['detection_method'] == 'extension'
   ```

2. **Content-based** - When extension is ambiguous
   ```python
   data = await XWData.load('data.txt')  # No clear extension
   # Analyzes content to detect format
   ```

3. **Hint-based** - When format is explicitly specified
   ```python
   data = await XWData.load('data.txt', format_hint='json')
   assert data.get_detection_info()['detection_method'] == 'hint'
   assert data.get_detection_confidence() == 1.0  # Perfect confidence
   ```

### Verification and Validation

```python
from exonware.xwdata import XWData

# Verify expected format
data = await XWData.load('config.json')

if data.get_detected_format() != 'JSON':
    raise ValueError(f"Expected JSON, got {data.get_detected_format()}")

# Check confidence before proceeding
confidence = data.get_detection_confidence()
if confidence < 0.8:
    print(f"Warning: Low confidence ({confidence:.0%})")
    print("Consider providing format_hint parameter")
```

### Format Conversion Tracking

```python
from exonware.xwdata import XWData

# Load JSON
json_data = await XWData.load('config.json')
print(f"Original: {json_data.get_detected_format()}")  # JSON

# Convert to YAML
await json_data.save('config.yaml')

# Load YAML
yaml_data = await XWData.load('config.yaml')
print(f"Converted: {yaml_data.get_detected_format()}")  # YAML

# Verify data integrity
assert await yaml_data.get('key') == await json_data.get('key')
```

### Metadata Persistence

Detection metadata persists through Copy-on-Write operations:

```python
data = await XWData.load('users.json')
assert data.get_detected_format() == 'JSON'

# After set operation (COW)
new_data = await data.set('users[0].age', 31)
assert new_data.get_detected_format() == 'JSON'  # Still available!

# After merge operation
other = await XWData.load('settings.yaml')
merged = await data.merge(other)
assert merged.get_detected_format() is not None
```

### Native Data (No Detection)

Data created from native Python objects has no format detection:

```python
data = XWData.from_native({'key': 'value'})

assert data.get_detected_format() is None
assert data.get_detection_confidence() is None
assert data.get_detection_info()['format_candidates'] == {}
```

---

## Complete Workflows

### Workflow 1: Data Migration

Migrate configuration from JSON to YAML with validation:

```python
from exonware.xwdata import XWData

# Load old config
old_config = await XWData.load('config.json')

# Verify it's JSON
if old_config.get_detected_format() != 'JSON':
    raise ValueError("Expected JSON config file")

print(f"Loaded JSON with {old_config.get_detection_confidence():.0%} confidence")

# Migrate to YAML
await old_config.save('config.yaml')

# Verify new config
new_config = await XWData.load('config.yaml')
assert new_config.get_detected_format() == 'YAML'

# Verify data integrity
assert await new_config.get('database.host') == await old_config.get('database.host')
```

### Workflow 2: Data Analytics

Load, query, analyze, and export:

```python
from exonware.xwdata import XWData

# Load sales data
sales = await XWData.load('sales.json')

# Verify detection
info = sales.get_detection_info()
print(f"Loaded {info['detected_format']} (confidence: {info['detection_confidence']:.0%})")

# Query: Get North region sales (auto-detect SQL)
north_sales = await sales.query(
    "SELECT * FROM sales WHERE region = 'North' AND amount > 50000"
)

# Query: Get top performers (auto-detect SQL)
top_performers = await sales.query("""
    SELECT region, SUM(amount) as total
    FROM sales
    GROUP BY region
    ORDER BY total DESC
    LIMIT 3
""")

# Export to YAML for reporting
await sales.save('sales_report.yaml')
```

### Workflow 3: Multi-Source Data Merge

Merge data from different formats and query:

```python
from exonware.xwdata import XWData

# Load user profiles (JSON)
profiles = await XWData.load('profiles.json')
assert profiles.get_detected_format() == 'JSON'

# Load user settings (YAML)
settings = await XWData.load('settings.yaml')
assert settings.get_detected_format() == 'YAML'

# Load user permissions (XML)
permissions = await XWData.load('permissions.xml')
assert permissions.get_detected_format() == 'XML'

# Merge all sources
combined = await profiles.merge(settings)
combined = await combined.merge(permissions)

# Query combined data (auto-detect SQL)
active_admins = await combined.query("""
    SELECT * FROM users 
    WHERE role = 'admin' AND active = true
""")
```

### Workflow 4: Format-Aware Processing

Process data differently based on detected format:

```python
from exonware.xwdata import XWData

data = await XWData.load('data_file')  # Unknown format

format_name = data.get_detected_format()

if format_name == 'JSON':
    # JSON-specific processing
    result = await data.query("SELECT * FROM items")
    
elif format_name == 'XML':
    # XML-specific processing
    result = await data.query("//item[@active='true']", format='xpath')
    
elif format_name == 'YAML':
    # YAML-specific processing
    result = await data.get('items')
    
else:
    # Generic processing
    result = data.to_native()
```

---

## Best Practices

### 1. Always Check Detection Confidence for Critical Operations

```python
data = await XWData.load('important_config.json')

confidence = data.get_detection_confidence()
if confidence < 0.9:
    raise ValueError(f"Low confidence ({confidence:.0%}) - verify file format")
```

### 2. Use Explicit Format Hints for Ambiguous Files

```python
# File with no extension or ambiguous content
data = await XWData.load('data_file', format_hint='json')
```

### 3. Prefer Auto-Detection for Queries

```python
# Good: Auto-detect (works for most queries)
result = await data.query("SELECT * FROM users WHERE age > 25")

# Also good: Explicit format when you know it
result = await data.query("users[?age > `25`]", format='jmespath')
```

### 4. Log Detection Info for Debugging

```python
import logging

data = await XWData.load('config.json')
info = data.get_detection_info()

logging.info(
    f"Loaded {info['detected_format']} "
    f"(confidence: {info['detection_confidence']:.0%}, "
    f"method: {info['detection_method']})"
)
```

### 5. Validate After Format Conversions

```python
# Convert JSON to YAML
json_data = await XWData.load('config.json')
await json_data.save('config.yaml')

# Load and validate
yaml_data = await XWData.load('config.yaml')

# Verify format
assert yaml_data.get_detected_format() == 'YAML'

# Verify data integrity
assert await yaml_data.get('key') == await json_data.get('key')
```

### 6. Handle Missing Dependencies Gracefully

```python
try:
    from exonware.xwquery import XWQuery
    QUERY_SUPPORT = True
except ImportError:
    QUERY_SUPPORT = False

if QUERY_SUPPORT:
    result = await data.query("SELECT * FROM users")
else:
    print("XWQuery not installed - using native access instead")
    result = await data.get('users')
```

---

## Troubleshooting

### Issue: Low Confidence Detection

**Symptom:** `get_detection_confidence()` returns < 0.8

**Solutions:**
1. Provide explicit `format_hint`:
   ```python
   data = await XWData.load('file.dat', format_hint='json')
   ```

2. Check file content and extension:
   ```python
   # Rename file with proper extension
   # file.dat → file.json
   ```

3. Review format candidates:
   ```python
   info = data.get_detection_info()
   print("Candidates:", info['format_candidates'])
   ```

### Issue: Query Format Not Auto-Detected

**Symptom:** Query uses wrong format or fails

**Solutions:**
1. Use explicit format:
   ```python
   result = await data.query(query, format='sql')
   ```

2. Check query syntax:
   ```python
   from exonware.xwquery import detect_query_format
   
   format, confidence = detect_query_format(query)
   print(f"Detected: {format} ({confidence:.0%})")
   ```

3. View all candidates:
   ```python
   from exonware.xwquery.parsers.format_detector import QueryFormatDetector
   
   detector = QueryFormatDetector()
   candidates = detector.detect_format_with_candidates(query)
   print(candidates)
   ```

### Issue: XWQuery Not Found

**Symptom:** `ImportError: No module named 'exonware.xwquery'`

**Solution:**
```bash
pip install exonware-xwquery
```

### Issue: No XWNode Available

**Symptom:** `ValueError: No XWNode available`

**Solutions:**
1. Ensure data is properly loaded:
   ```python
   data = await XWData.load('file.json')  # Use load()
   # NOT: data = XWData('file.json')  # This may fail in async context
   ```

2. Use `from_native()` for native data:
   ```python
   data = XWData.from_native({'key': 'value'})
   node = data.as_xwnode()
   ```

### Issue: Detection Metadata Not Available

**Symptom:** All detection methods return `None`

**Cause:** Data created from native Python objects (not loaded from file)

**Expected behavior:**
```python
data = XWData.from_native({'key': 'value'})
assert data.get_detected_format() is None  # Expected!
```

**Solution:** Only files have detection metadata. For native data, there's nothing to detect.

---

## API Reference

### XWData Methods

```python
class XWData:
    # Query Integration (Plan 1)
    def as_xwnode(self) -> XWNode
    async def query(self, expression: str, format: str = 'sql', **opts) -> Any
    
    # Detection Metadata (Plan 3)
    def get_detected_format(self) -> Optional[str]
    def get_detection_confidence(self) -> Optional[float]
    def get_detection_info(self) -> Dict[str, Any]
```

### XWQuery Functions

```python
from exonware.xwquery import (
    XWQuery,
    detect_query_format,
    QueryFormatDetector
)

# Auto-detect and execute
result = XWQuery.execute(query, data, auto_detect=True)

# Detect format
format, confidence = detect_query_format(query)

# Advanced detection
detector = QueryFormatDetector(confidence_threshold=0.8)
format, confidence = detector.detect_format(query)
candidates = detector.detect_format_with_candidates(query)
is_confident = detector.is_confident(query)
```

---

## Additional Resources

- [XWData Documentation](../README.md)
- [XWQuery Documentation](../../xwquery/README.md)
- [XWNode Documentation](../../xwnode/README.md)
- [XWSystem Documentation](../../xwsystem/README.md)

---

## Version History

- **v0.0.1.3** (Oct 2025) - Complete implementation of all three enhancement plans
  - ✅ Plan 1: XWData + XWQuery integration
  - ✅ Plan 2: XWQuery format auto-detection
  - ✅ Plan 3: XWData detection metadata exposure

---

**Company:** eXonware.com  
**Author:** Eng. Muhammad AlShehri  
**Email:** connect@exonware.com  
**Date:** October 26, 2025

