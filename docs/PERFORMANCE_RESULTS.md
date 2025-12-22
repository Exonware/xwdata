# Performance Benchmark Results

**Date:** 2025-10-26 20:31:44
**Python:** 3.12.10 (tags/v3.12.10:0cc8128, Apr  8 2025, 12:21:36) [MSC v.1943 64 bit (AMD64)]

## Note

MIGRAT implementation has import issues and cannot be benchmarked directly.
Showing new implementation results only:

| Test | Duration (ms) | Status |
|------|---------------|--------|
| load_json | 37.49 | ✅ Success |
| from_native_small | 0.30 | ✅ Success |
| from_native_medium | 0.14 | ✅ Success |
| from_native_large | 0.11 | ✅ Success |
| navigation_1000x | 34.40 | ✅ Success |