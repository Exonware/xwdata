# Index Cache 5GB Test Plan

**Purpose:** Test index caching performance with a 5GB XWJSON file to measure full benefits

---

## Current Test Results (21MB file)

### Baseline Results:
- **File:** `chatdb.xwjson` (21.65 MB)
- **Format:** Dual-file (`.xwjson` + `.meta.xwjson`, 662 KB)

### Performance Improvements:
- `read_header_and_index()`: **7.76-12.15x faster** (87-91% reduction) ✅
- `load_file()`: **1.03-1.11x faster** (3-7% reduction)
- `_load_index_file()`: **1.02-1.32x faster** (2-24% reduction)

---

## Expected 5GB Test Results

For a **5GB file**, the index caching should show **much more dramatic improvements** because:

1. **Index loading time increases** with file size (more metadata to read)
2. **Cache benefit is proportional** to the cost of loading from disk
3. **For 5GB files**, index loading can take **10-100ms**, so cache should provide **100-1000x speedup**

### Expected Improvements (5GB file):

| Metric | Cold (First Call) | Warm (Cached) | Expected Improvement |
|--------|-------------------|---------------|---------------------|
| `read_header_and_index()` | ~10-50ms | ~0.1ms | **100-500x faster** ✅ |
| `_load_index_file()` | ~5-20ms | ~0.1ms | **50-200x faster** ✅ |
| `load_file()` | ~25-50s | ~24-49s | **1.02-2x faster** |

---

## Test Procedure

### Step 1: Generate 5GB Test File

```bash
# Generate 5GB XWJSON file with dual-file format
python xwdata/examples/chatdb_bigfile/operations/generate_5gb_xwjson.py \
    --output xwdata/examples/chatdb_bigfile/data/chatdb_5gb.xwjson \
    --size-gb 5.0 \
    --create-index-file
```

**Expected time:** 5-15 minutes (depends on disk speed)

**Expected output:**
- `chatdb_5gb.xwjson` (~5GB)
- `chatdb_5gb.data.xwjson` (~5GB, pure MessagePack)
- `chatdb_5gb.meta.xwjson` (~10-50KB, metadata/index)

### Step 2: Run Benchmark

```bash
# Run benchmark on 5GB file
python xwdata/examples/chatdb_bigfile/operations/benchmark_index_cache.py \
    --file xwdata/examples/chatdb_bigfile/data/chatdb_5gb.xwjson
```

### Step 3: Compare Results

Compare with baseline (21MB file) to show:
- **Absolute improvements** (time saved)
- **Relative improvements** (speedup ratio)
- **Cache effectiveness** (cache hit rate)

---

## Test Scripts

### generate_5gb_xwjson.py

**Purpose:** Generate large XWJSON files for performance testing

**Usage:**
```bash
python generate_5gb_xwjson.py --output <path> --size-gb <size> [--create-index-file]
```

**Features:**
- Generates synthetic data (messages/records)
- Supports dual-file format (`.data.xwjson` + `.meta.xwjson`)
- Progress indicator
- Size targeting

### benchmark_index_cache.py

**Purpose:** Benchmark index caching performance

**Usage:**
```bash
python benchmark_index_cache.py [--file <path>]
```

**Measures:**
- `load_file()` - Cold vs Warm
- `read_header_and_index()` - Cold vs Warm
- `_load_index_file()` - Cold vs Warm

---

## Notes

1. **5GB file generation** will take time (5-15 minutes)
2. **Memory usage** during generation may be high (consider generating in chunks)
3. **Disk space** required: ~10GB (5GB data + 5GB during generation)
4. **Test file location:** `xwdata/examples/chatdb_bigfile/data/chatdb_5gb.xwjson`

---

## Current Status

✅ **Implementation Complete:**
- Index cache infrastructure
- Shared cache strategy
- Cache invalidation
- Benchmark scripts

✅ **Testing Complete (21MB):**
- Baseline results documented
- Cache working correctly
- Performance improvements verified

⏳ **Pending (5GB Test):**
- Generate 5GB test file
- Run benchmark on 5GB file
- Document full-scale performance improvements

---

## Quick Test (1GB File)

For a quicker test while 5GB generates, use the 1GB file:

```bash
# Already generated
python benchmark_index_cache.py --file xwdata/examples/chatdb_bigfile/data/chatdb_1gb.xwjson
```

**1GB file should show intermediate improvements** between 21MB and 5GB.

