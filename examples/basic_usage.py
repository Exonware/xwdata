#!/usr/bin/env python3
"""
#exonware/xwdata/examples/basic_usage.py

Basic xwdata usage examples.

Company: eXonware.com
Author: Eng. Muhammad AlShehri
Email: connect@exonware.com
Version: 0.0.1.3
Generation Date: 26-Oct-2025
"""

import asyncio
from exonware.xwdata import XWData


async def example_basic_operations():
    """Basic load, modify, save operations."""
    print("=" * 80)
    print("Example 1: Basic Operations")
    print("=" * 80)
    
    # Create from native data
    data = XWData({
        'app': {
            'name': 'MyApp',
            'version': '1.0.0'
        },
        'config': {
            'timeout': 30,
            'retries': 3
        }
    })
    
    # Get values
    app_name = await data.get('app.name')
    print(f"App name: {app_name}")
    
    # Set values (copy-on-write)
    data = await data.set('config.timeout', 60)
    
    # Get updated value
    timeout = await data.get('config.timeout')
    print(f"Updated timeout: {timeout}")
    
    print("✅ Basic operations complete\n")


async def example_format_conversion():
    """Format conversion example."""
    print("=" * 80)
    print("Example 2: Format Conversion")
    print("=" * 80)
    
    # Create data
    data = XWData({
        'database': {
            'host': 'localhost',
            'port': 5432,
            'name': 'mydb'
        }
    })
    
    # Save to multiple formats
    await data.save('/tmp/config.json', format='json')
    print("✅ Saved as JSON")
    
    await data.save('/tmp/config.yaml', format='yaml')
    print("✅ Saved as YAML")
    
    await data.save('/tmp/config.xml', format='xml')
    print("✅ Saved as XML")
    
    print("✅ Format conversion complete\n")


async def example_copy_on_write():
    """Copy-on-write semantics example."""
    print("=" * 80)
    print("Example 3: Copy-on-Write Semantics")
    print("=" * 80)
    
    # Original data
    original = XWData({'counter': 0})
    
    # Create modifications (each returns new instance)
    version1 = await original.set('counter', 1)
    version2 = await original.set('counter', 2)
    version3 = await version1.set('counter', 10)
    
    # All versions coexist
    print(f"Original: {await original.get('counter')}")  # 0
    print(f"Version 1: {await version1.get('counter')}")  # 1
    print(f"Version 2: {await version2.get('counter')}")  # 2
    print(f"Version 3: {await version3.get('counter')}")  # 10
    
    print("✅ Copy-on-write complete\n")


async def example_merging():
    """Merging multiple sources example."""
    print("=" * 80)
    print("Example 4: Merging Multiple Sources")
    print("=" * 80)
    
    # Merge multiple data sources
    merged = XWData([
        {'base': 'config', 'timeout': 30},
        {'environment': 'production', 'timeout': 60},
        {'debug': False}
    ], merge_strategy='deep')
    
    native = merged.to_native()
    print(f"Merged data: {native}")
    
    print("✅ Merging complete\n")


async def main():
    """Run all examples."""
    print("\n🚀 XWData Examples\n")
    
    await example_basic_operations()
    await example_format_conversion()
    await example_copy_on_write()
    await example_merging()
    
    print("=" * 80)
    print("✅ All examples completed successfully!")
    print("=" * 80)


if __name__ == "__main__":
    asyncio.run(main())

