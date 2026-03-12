#!/usr/bin/env python3
"""Diagnose navigation performance issue on large datasets."""

import sys
import time
from pathlib import Path
# Add paths
benchmarks_dir = Path(__file__).parent
xwdata_root = benchmarks_dir.parent
sys.path.insert(0, str(xwdata_root / "src"))
from exonware.xwdata import XWData


def create_large_data():
    """Create large test data."""
    return {
        'records': [
            {
                'id': i,
                'data': {
                    'field1': f'value_{i}',
                    'nested': {
                        'level1': {
                            'level2': {
                                'value': i
                            }
                        }
                    }
                }
            }
            for i in range(1000)
        ]
    }


def test_navigation_performance():
    """Test different navigation approaches."""
    print("Creating large dataset...")
    data = create_large_data()
    print("Creating XWData instance...")
    start = time.perf_counter()
    xw = XWData.from_native(data)
    creation_time = (time.perf_counter() - start) * 1000
    print(f"  Creation time: {creation_time:.4f}ms")
    # Test 1: Simple top-level access
    print("\nTest 1: Simple access (records.0.id)")
    start = time.perf_counter()
    for _ in range(100):
        value = xw.get('records.0.id')
    end = time.perf_counter()
    per_op = ((end - start) * 1000) / 100
    print(f"  Per operation: {per_op:.4f}ms")
    # Test 2: Shallow nested access
    print("\nTest 2: Shallow nested (records.0.data.field1)")
    start = time.perf_counter()
    for _ in range(100):
        value = xw.get('records.0.data.field1')
    end = time.perf_counter()
    per_op = ((end - start) * 1000) / 100
    print(f"  Per operation: {per_op:.4f}ms")
    # Test 3: Deep nested access
    print("\nTest 3: Deep nested (records.0.data.nested.level1.level2.value)")
    start = time.perf_counter()
    for _ in range(100):
        value = xw.get('records.0.data.nested.level1.level2.value')
    end = time.perf_counter()
    per_op = ((end - start) * 1000) / 100
    print(f"  Per operation: {per_op:.4f}ms")
    # Test 4: Direct native access for comparison
    print("\nTest 4: Direct native access (baseline)")
    native = data
    start = time.perf_counter()
    for _ in range(100):
        value = native['records'][0]['data']['nested']['level1']['level2']['value']
    end = time.perf_counter()
    per_op = ((end - start) * 1000) / 100
    print(f"  Per operation: {per_op:.4f}ms")
    # Test 5: Using XWDataNode directly
    print("\nTest 5: XWDataNode navigation")
    node = xw._node
    start = time.perf_counter()
    for _ in range(100):
        value = node.get_value_at_path('records.0.data.nested.level1.level2.value')
    end = time.perf_counter()
    per_op = ((end - start) * 1000) / 100
    print(f"  Per operation: {per_op:.4f}ms")
    # Test 6: Check if XWNode is being used
    print("\nDiagnostics:")
    print(f"  Has _xwnode: {node._xwnode is not None}")
    if node._xwnode:
        print(f"  XWNode type: {type(node._xwnode)}")
        print(f"  XWNode immutable: {getattr(node._xwnode, '_immutable', 'unknown')}")
if __name__ == "__main__":
    test_navigation_performance()
