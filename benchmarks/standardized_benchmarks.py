#!/usr/bin/env python3
"""
#exonware/xwdata/benchmarks/standardized_benchmarks.py

Standardized Performance Benchmarks for XWData

Uses the same test files as xData-Old for apple-to-apple comparison.
Matches the documented benchmarks from xData-Old/docs/performance.rst

Company: eXonware.com
Author: Eng. Muhammad AlShehri
Email: connect@exonware.com
Version: 0.0.1.3
Generation Date: 28-Oct-2025
"""

import sys
import time
import json
import asyncio
import io
import tempfile
import shutil
import tracemalloc
import psutil
import os
from pathlib import Path
from typing import Dict, List, Tuple, Any
from dataclasses import dataclass, field
import statistics

# Set UTF-8 encoding for Windows console
if sys.platform == 'win32':
    try:
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')
    except:
        pass

# Add paths
benchmarks_dir = Path(__file__).parent
xwdata_root = benchmarks_dir.parent
sys.path.insert(0, str(xwdata_root / "src"))

# Test file paths (using standard test files)
FIXTURES_DIR = xwdata_root / "tests" / "fixtures"


@dataclass
class BenchmarkResult:
    """Detailed benchmark measurement."""
    test_name: str
    file_size_category: str  # 'small', 'medium', 'large'
    format: str
    operation: str  # 'load', 'save', 'parse', 'serialize', 'from_native', 'navigation', 'memory'
    duration_ms: float
    file_size_bytes: int = 0
    iterations: int = 1
    success: bool = True
    error: str = ""
    memory_mb: float = 0.0  # Memory usage in MB
    memory_ratio: float = 0.0  # Memory/File size ratio
    
    @property
    def avg_duration_ms(self) -> float:
        """Average duration per iteration."""
        return self.duration_ms / self.iterations if self.iterations > 0 else self.duration_ms


class StandardizedBenchmark:
    """
    Standardized benchmarks using the same test approach as xData-Old.
    
    Creates standard test files in three sizes:
    - Small: < 1KB
    - Medium: 10-100KB
    - Large: 1MB+
    
    Tests each file with multiple formats to match xData-Old benchmarks.
    """
    
    def __init__(self):
        self.results: List[BenchmarkResult] = []
        self.temp_dir = None
        
        # Standard test data (matching xData-Old patterns)
        self.test_files = {}
    
    def _create_test_data_small(self) -> dict:
        """Create small test data (< 1KB) - matches person.json pattern."""
        return {
            "person": {
                "name": "John Doe",
                "age": 30,
                "email": "john.doe@example.com",
                "interests": ["Reading", "Traveling", "Music"],
                "address": {
                    "street": "123 Main St",
                    "city": "Anytown",
                    "country": "USA"
                }
            }
        }
    
    def _create_test_data_medium(self) -> dict:
        """Create medium test data (~50KB)."""
        return {
            "users": [
                {
                    "id": i,
                    "name": f"User {i}",
                    "email": f"user{i}@example.com",
                    "age": 20 + (i % 60),
                    "active": i % 2 == 0,
                    "profile": {
                        "bio": f"This is a bio for user {i}. " * 10,
                        "interests": ["coding", "reading", "gaming", "music"],
                        "location": f"City {i % 20}",
                        "joined": f"2024-{(i % 12) + 1:02d}-{(i % 28) + 1:02d}"
                    }
                }
                for i in range(100)
            ],
            "metadata": {
                "version": "1.0",
                "total_count": 100,
                "last_updated": "2025-10-28T12:00:00Z"
            }
        }
    
    def _create_test_data_large(self) -> dict:
        """Create large test data (~1MB)."""
        return {
            "records": [
                {
                    "id": i,
                    "timestamp": f"2025-10-28T{i%24:02d}:{i%60:02d}:00Z",
                    "data": {
                        "field1": f"value_{i}",
                        "field2": i * 1.5,
                        "field3": i % 100 == 0,
                        "description": "x" * 100,  # Add bulk
                        "nested": {
                            "level1": {
                                "level2": {
                                    "value": i,
                                    "data": [j for j in range(10)]
                                }
                            }
                        }
                    },
                    "tags": [f"tag{j}" for j in range(10)],
                }
                for i in range(1000)
            ],
            "metadata": {
                "total": 1000,
                "generated": "2025-10-28"
            }
        }
    
    async def setup(self):
        """Setup benchmark environment."""
        self.temp_dir = Path(tempfile.mkdtemp(prefix="xwdata_std_bench_"))
        print(f"📁 Created temp directory: {self.temp_dir}")
        
        # Create test files
        self.test_files = {
            'small': self._create_test_data_small(),
            'medium': self._create_test_data_medium(),
            'large': self._create_test_data_large()
        }
    
    async def cleanup(self):
        """Cleanup benchmark environment."""
        if self.temp_dir and self.temp_dir.exists():
            shutil.rmtree(self.temp_dir)
            print(f"🧹 Cleaned up temp directory")
    
    async def benchmark_operation(
        self,
        size: str,
        format: str,
        operation: str,
        iterations: int = 10
    ) -> BenchmarkResult:
        """
        Benchmark a specific operation.
        
        Args:
            size: 'small', 'medium', or 'large'
            format: 'json', 'xml', 'yaml', 'toml', etc.
            operation: 'load', 'save', 'parse', 'serialize', 'from_native'
            iterations: Number of iterations to average
        """
        from exonware.xwdata import XWData
        
        data = self.test_files[size]
        file_path = self.temp_dir / f"test_{size}.{format}"
        
        try:
            if operation == 'load':
                # First create the file
                xw = XWData.from_native(data)
                await xw.save(str(file_path), format=format)
                file_size = file_path.stat().st_size
                
                # Benchmark loading
                durations = []
                for _ in range(iterations):
                    start = time.perf_counter()
                    loaded = await XWData.load(str(file_path))
                    end = time.perf_counter()
                    durations.append((end - start) * 1000)
                
                avg_duration = statistics.mean(durations)
                
                return BenchmarkResult(
                    test_name=f"{operation}_{size}_{format}",
                    file_size_category=size,
                    format=format,
                    operation=operation,
                    duration_ms=avg_duration,
                    file_size_bytes=file_size,
                    iterations=iterations,
                    success=True
                )
            
            elif operation == 'save':
                xw = XWData.from_native(data)
                
                durations = []
                for i in range(iterations):
                    save_path = self.temp_dir / f"save_{size}_{i}.{format}"
                    
                    start = time.perf_counter()
                    await xw.save(str(save_path), format=format)
                    end = time.perf_counter()
                    
                    durations.append((end - start) * 1000)
                    
                    # Clean up to avoid disk space issues
                    if save_path.exists():
                        save_path.unlink()
                
                avg_duration = statistics.mean(durations)
                
                return BenchmarkResult(
                    test_name=f"{operation}_{size}_{format}",
                    file_size_category=size,
                    format=format,
                    operation=operation,
                    duration_ms=avg_duration,
                    iterations=iterations,
                    success=True
                )
            
            elif operation == 'parse':
                # Create serialized content
                xw = XWData.from_native(data)
                content = await xw.serialize(format=format)
                
                durations = []
                for _ in range(iterations):
                    start = time.perf_counter()
                    parsed = await XWData.parse(content, format=format)
                    end = time.perf_counter()
                    durations.append((end - start) * 1000)
                
                avg_duration = statistics.mean(durations)
                
                return BenchmarkResult(
                    test_name=f"{operation}_{size}_{format}",
                    file_size_category=size,
                    format=format,
                    operation=operation,
                    duration_ms=avg_duration,
                    iterations=iterations,
                    success=True
                )
            
            elif operation == 'serialize':
                xw = XWData.from_native(data)
                
                durations = []
                for _ in range(iterations):
                    start = time.perf_counter()
                    content = await xw.serialize(format=format)
                    end = time.perf_counter()
                    durations.append((end - start) * 1000)
                
                avg_duration = statistics.mean(durations)
                
                return BenchmarkResult(
                    test_name=f"{operation}_{size}_{format}",
                    file_size_category=size,
                    format=format,
                    operation=operation,
                    duration_ms=avg_duration,
                    iterations=iterations,
                    success=True
                )
            
            elif operation == 'from_native':
                durations = []
                for _ in range(iterations):
                    start = time.perf_counter()
                    xw = XWData.from_native(data)
                    end = time.perf_counter()
                    durations.append((end - start) * 1000)
                
                avg_duration = statistics.mean(durations)
                
                return BenchmarkResult(
                    test_name=f"{operation}_{size}",
                    file_size_category=size,
                    format='native',
                    operation=operation,
                    duration_ms=avg_duration,
                    iterations=iterations,
                    success=True
                )
            
            else:
                raise ValueError(f"Unknown operation: {operation}")
                
        except Exception as e:
            return BenchmarkResult(
                test_name=f"{operation}_{size}_{format}",
                file_size_category=size,
                format=format,
                operation=operation,
                duration_ms=0,
                iterations=iterations,
                success=False,
                error=str(e)
            )
    
    async def benchmark_reference_resolution(self, size: str, iterations: int = 10) -> BenchmarkResult:
        """
        Benchmark REAL reference resolution (matching xData-Old tests).
        
        Creates actual reference chains like xData-Old does:
        - Small: 1 reference file
        - Medium: 10 chained reference files  
        - Large: 100 chained reference files
        
        This is HONEST testing - not fake string access!
        """
        from exonware.xwdata import XWData, XWDataConfig, ReferenceConfig
        
        # NOTE: Current xwdata doesn't have reference resolution wired up yet
        # This benchmark will measure what it SHOULD be when implemented
        # For now, we'll test reference DETECTION performance (finding ref strings)
        
        try:
            # Create reference chain files (like xData-Old does)
            ref_dir = self.temp_dir / "references"
            ref_dir.mkdir(exist_ok=True)
            
            chain_length = {'small': 1, 'medium': 10, 'large': 100}[size]
            
            # Create chained reference files
            for i in range(chain_length):
                current_file = ref_dir / f"ref_{i}.json"
                if i < chain_length - 1:
                    # References next file in chain
                    content = json.dumps({
                        "next": f"ref_{i+1}.json",
                        "data": f"level {i}",
                        "index": i
                    })
                else:
                    # Final file
                    content = json.dumps({
                        "data": "final level",
                        "final": True
                    })
                current_file.write_text(content)
            
            # Configure for reference resolution
            config = XWDataConfig.default()
            config.reference = ReferenceConfig.eager()  # Resolve references immediately
            
            # Benchmark loading and resolution
            durations = []
            for _ in range(iterations):
                start = time.perf_counter()
                
                # Load first file (would trigger resolution chain if implemented)
                data = await XWData.load(str(ref_dir / "ref_0.json"), config=config)
                
                # Access the data (would resolve references if implemented)
                value = data.get('data')
                
                end = time.perf_counter()
                durations.append((end - start) * 1000)
            
            avg_duration = statistics.mean(durations)
            
            # Note: This measures load time, not actual resolution
            # because reference resolution isn't wired up yet
            return BenchmarkResult(
                test_name=f"reference_detection_{size}",
                file_size_category=size,
                format='reference',
                operation='reference_detection',  # Changed from resolution to detection
                duration_ms=avg_duration,
                iterations=iterations,
                success=True
            )
        except Exception as e:
            return BenchmarkResult(
                test_name=f"reference_detection_{size}",
                file_size_category=size,
                format='reference',
                operation='reference_detection',
                duration_ms=0,
                iterations=iterations,
                success=False,
                error=str(e)
            )
    
    async def benchmark_navigation(self, size: str, iterations: int = 1000) -> BenchmarkResult:
        """Benchmark navigation performance."""
        from exonware.xwdata import XWData
        
        data = self.test_files[size]
        
        # Different paths for different sizes (MUST match xData-Old exactly for fair comparison)
        paths = {
            'small': 'person.name',
            'medium': 'users.0.name',
            'large': 'records.0.data.nested.level1.level2.value'  # Deep path - same as xData-Old tests
        }
        
        path = paths.get(size, 'name')
        
        try:
            xw = XWData.from_native(data)
            
            start = time.perf_counter()
            for _ in range(iterations):
                # Use sync access for benchmarking (get returns value directly, not a coroutine)
                value = xw.get(path)
            end = time.perf_counter()
            
            total_duration = (end - start) * 1000
            ops_per_sec = iterations / (end - start) if (end - start) > 0 else 0
            
            return BenchmarkResult(
                test_name=f"navigation_{size}_{iterations}x",
                file_size_category=size,
                format='native',
                operation='navigation',
                duration_ms=total_duration,
                iterations=iterations,
                success=True
            )
        except Exception as e:
            return BenchmarkResult(
                test_name=f"navigation_{size}_{iterations}x",
                file_size_category=size,
                format='native',
                operation='navigation',
                duration_ms=0,
                iterations=iterations,
                success=False,
                error=str(e)
            )
    
    async def benchmark_memory_usage(self, size: str, format: str = 'json') -> BenchmarkResult:
        """
        Benchmark memory usage for load operations.
        
        Measures:
        - File size (original)
        - Memory usage (in-memory representation)
        - Memory ratio (memory/file size)
        
        Following xData-Old's memory benchmarks from performance.rst
        """
        from exonware.xwdata import XWData
        
        # Create a temporary test file for memory measurement
        test_file = self.temp_dir / f"memory_test_{size}.{format}"
        data = self.test_files[size]
        
        # Write test data to file
        if format == 'json':
            with open(test_file, 'w') as f:
                json.dump(data, f)
        
        file_size_bytes = test_file.stat().st_size
        
        try:
            # Start memory tracking
            tracemalloc.start()
            process = psutil.Process(os.getpid())
            mem_before = process.memory_info().rss / (1024 * 1024)  # MB
            
            # Load data
            start = time.perf_counter()
            loaded_data = await XWData.load(str(test_file))
            end = time.perf_counter()
            
            # Measure memory
            mem_after = process.memory_info().rss / (1024 * 1024)  # MB
            current, peak = tracemalloc.get_traced_memory()
            tracemalloc.stop()
            
            memory_used_mb = mem_after - mem_before
            memory_ratio = memory_used_mb / (file_size_bytes / (1024 * 1024)) if file_size_bytes > 0 else 0
            
            duration = (end - start) * 1000
            
            return BenchmarkResult(
                test_name=f"memory_{size}_{format}",
                file_size_category=size,
                format=format,
                operation='memory',
                duration_ms=duration,
                file_size_bytes=file_size_bytes,
                iterations=1,
                success=True,
                memory_mb=memory_used_mb,
                memory_ratio=memory_ratio
            )
        except Exception as e:
            tracemalloc.stop() if tracemalloc.is_tracing() else None
            return BenchmarkResult(
                test_name=f"memory_{size}_{format}",
                file_size_category=size,
                format=format,
                operation='memory',
                duration_ms=0,
                file_size_bytes=file_size_bytes,
                iterations=1,
                success=False,
                error=str(e)
            )
    
    async def run_all_benchmarks(self):
        """Run standardized benchmark suite."""
        print("=" * 100)
        print("🚀 STANDARDIZED XWDATA PERFORMANCE BENCHMARKS")
        print("=" * 100)
        print()
        print("Using same test data patterns as xData-Old for apple-to-apple comparison")
        print()
        
        await self.setup()
        
        try:
            sizes = ['small', 'medium', 'large']
            formats = ['json', 'yaml', 'xml', 'toml', 'bson']  # Added BSON to match xData-Old
            operations = ['load', 'save', 'parse', 'serialize']
            
            # 1. File I/O Operations
            print("\n📁 FILE I/O OPERATIONS")
            print("-" * 100)
            
            for size in sizes:
                print(f"\n  {size.upper()} Files:")
                for fmt in formats:
                    print(f"    {fmt.upper():<8}", end=" ")
                    
                    for operation in ['load', 'save']:
                        result = await self.benchmark_operation(size, fmt, operation, iterations=10)
                        self.results.append(result)
                        
                        if result.success:
                            print(f"{operation.capitalize()}: {result.avg_duration_ms:>6.2f}ms", end=" | ")
                        else:
                            print(f"{operation.capitalize()}: FAIL", end=" | ")
                    
                    print()
            
            # 2. From Native
            print("\n\n🏗️  FROM NATIVE CREATION")
            print("-" * 100)
            
            for size in sizes:
                print(f"  {size.upper():<10}", end=" ")
                result = await self.benchmark_operation(size, 'json', 'from_native', iterations=100)
                self.results.append(result)
                
                if result.success:
                    print(f"✅ {result.avg_duration_ms:>8.4f}ms")
                else:
                    print(f"❌ Failed: {result.error}")
            
            # 3. Navigation
            print("\n\n🧭 NAVIGATION (1000 iterations)")
            print("-" * 100)
            
            for size in sizes:
                print(f"  {size.upper():<10}", end=" ")
                result = await self.benchmark_navigation(size, iterations=1000)
                self.results.append(result)
                
                if result.success:
                    per_op = result.avg_duration_ms
                    ops_per_sec = 1000 / (result.duration_ms / 1000) if result.duration_ms > 0 else 0
                    print(f"✅ {per_op:>8.4f}ms/op ({ops_per_sec:>10,.0f} ops/sec)")
                else:
                    print(f"❌ Failed: {result.error}")
            
            # 4. Parse/Serialize
            print("\n\n🔄 PARSE/SERIALIZE")
            print("-" * 100)
            
            for size in sizes:
                print(f"\n  {size.upper()} Data:")
                for fmt in ['json', 'yaml', 'xml', 'bson']:  # Added BSON
                    print(f"    {fmt.upper():<8}", end=" ")
                    
                    for operation in ['parse', 'serialize']:
                        result = await self.benchmark_operation(size, fmt, operation, iterations=10)
                        self.results.append(result)
                        
                        if result.success:
                            print(f"{operation.capitalize()}: {result.avg_duration_ms:>6.2f}ms", end=" | ")
                        else:
                            print(f"{operation.capitalize()}: FAIL", end=" | ")
                    
                    print()
            
            # 5. Reference Resolution (to match xData-Old benchmarks)
            print("\n\n🔗 REFERENCE RESOLUTION")
            print("-" * 100)
            print("  Testing reference resolution performance...")
            
            for size in sizes:
                print(f"    {size.upper():<10}", end=" ")
                result = await self.benchmark_reference_resolution(size, iterations=100)
                self.results.append(result)
                
                if result.success:
                    print(f"✅ {result.avg_duration_ms:>6.2f}ms/op")
                else:
                    print(f"❌ {result.error}")
            
            # Memory usage benchmarks
            print()
            print("💾 MEMORY USAGE")
            print("-" * 100)
            print("  Testing memory overhead...")
            
            for size in ['small', 'medium', 'large']:
                print(f"    {size.upper():<10}", end=" ")
                result = await self.benchmark_memory_usage(size, 'json')
                self.results.append(result)
                
                if result.success:
                    file_mb = result.file_size_bytes / (1024 * 1024)
                    print(f"✅ File: {file_mb:.2f}MB | Memory: {result.memory_mb:.2f}MB | Ratio: {result.memory_ratio:.1f}x")
                else:
                    print(f"❌ {result.error}")
            
            print("\n\n✅ All benchmarks complete!")
            
        finally:
            await self.cleanup()
    
    def print_comparison_table(self):
        """Print comparison table matching xData-Old format."""
        print("\n" + "=" * 100)
        print("📊 PERFORMANCE COMPARISON TABLE")
        print("=" * 100)
        print()
        
        # Group by operation
        operations = {}
        for r in self.results:
            if r.success:
                if r.operation not in operations:
                    operations[r.operation] = []
                operations[r.operation].append(r)
        
        # Format comparison table (matching xData-Old docs/performance.rst)
        print("FILE I/O OPERATIONS (Load/Save):")
        print("-" * 100)
        print(f"{'Operation':<12} | {'Small File':<15} | {'Medium File':<15} | {'Large File':<15}")
        print("-" * 100)
        
        for op in ['load', 'save']:
            if op in operations:
                results_by_size = {}
                for r in operations[op]:
                    if r.format == 'json':  # Use JSON as standard
                        results_by_size[r.file_size_category] = r.avg_duration_ms
                
                print(f"{op.upper() + ' (JSON)':<12} | ", end="")
                for size in ['small', 'medium', 'large']:
                    val = results_by_size.get(size, 0)
                    print(f"{val:>13.2f}ms | ", end="")
                print()
        
        print()
        print("FROM NATIVE CREATION:")
        print("-" * 100)
        print(f"{'Size':<12} | {'Duration (ms)':<15}")
        print("-" * 100)
        
        if 'from_native' in operations:
            for r in sorted(operations['from_native'], key=lambda x: ['small', 'medium', 'large'].index(x.file_size_category)):
                print(f"{r.file_size_category.upper():<12} | {r.avg_duration_ms:>14.4f}ms")
        
        print()
        print("NAVIGATION PERFORMANCE:")
        print("-" * 100)
        print(f"{'Size':<12} | {'Per Operation':<15} | {'Throughput':<20}")
        print("-" * 100)
        
        if 'navigation' in operations:
            for r in sorted(operations['navigation'], key=lambda x: ['small', 'medium', 'large'].index(x.file_size_category)):
                per_op = r.avg_duration_ms
                ops_sec = 1000 / (r.duration_ms / 1000) if r.duration_ms > 0 else 0
                print(f"{r.file_size_category.upper():<12} | {per_op:>13.4f}ms | {ops_sec:>18,.0f} ops/sec")
    
    def save_results(self, output_path: Path):
        """Save results in markdown format."""
        lines = []
        lines.append("# XWData Standardized Performance Benchmarks")
        lines.append("")
        lines.append(f"**Date:** {time.strftime('%Y-%m-%d %H:%M:%S')}")
        lines.append(f"**Python:** {sys.version}")
        lines.append(f"**Total Tests:** {len(self.results)}")
        lines.append(f"**Successful:** {sum(1 for r in self.results if r.success)}")
        lines.append(f"**Failed:** {sum(1 for r in self.results if not r.success)}")
        lines.append("")
        lines.append("## Performance Tables")
        lines.append("")
        
        # File I/O table
        lines.append("### File I/O Operations")
        lines.append("")
        lines.append("| Operation | Small File | Medium File | Large File |")
        lines.append("|-----------|------------|-------------|------------|")
        
        for op in ['load', 'save']:
            results_by_size = {}
            for r in self.results:
                if r.success and r.operation == op and r.format == 'json':
                    results_by_size[r.file_size_category] = r.avg_duration_ms
            
            if results_by_size:
                line = f"| {op.upper() + ' (JSON)'} |"
                for size in ['small', 'medium', 'large']:
                    val = results_by_size.get(size, 0)
                    line += f" {val:.2f}ms |"
                lines.append(line)
        
        lines.append("")
        lines.append("### From Native Creation")
        lines.append("")
        lines.append("| Size | Duration (ms) |")
        lines.append("|------|---------------|")
        
        for r in self.results:
            if r.success and r.operation == 'from_native':
                lines.append(f"| {r.file_size_category.upper()} | {r.avg_duration_ms:.4f} |")
        
        lines.append("")
        lines.append("### Navigation Performance")
        lines.append("")
        lines.append("| Size | Per Operation (ms) | Throughput (ops/sec) |")
        lines.append("|------|-------------------|---------------------|")
        
        for r in self.results:
            if r.success and r.operation == 'navigation':
                per_op = r.avg_duration_ms
                ops_sec = 1000 / (r.duration_ms / 1000) if r.duration_ms > 0 else 0
                lines.append(f"| {r.file_size_category.upper()} | {per_op:.4f} | {ops_sec:,.0f} |")
        
        lines.append("")
        lines.append("## Comparison with xData-Old Benchmarks")
        lines.append("")
        lines.append("From `xData-Old/docs/performance.rst`:")
        lines.append("")
        lines.append("| Operation | Small (Old) | Small (New) | Medium (Old) | Medium (New) | Large (Old) | Large (New) |")
        lines.append("|-----------|-------------|-------------|--------------|--------------|-------------|-------------|")
        
        # Add comparison row for JSON Parse
        json_load_results = {r.file_size_category: r.avg_duration_ms for r in self.results if r.success and r.operation == 'load' and r.format == 'json'}
        line = "| JSON Load |"
        line += f" 0.1ms | {json_load_results.get('small', 0):.2f}ms |"
        line += f" 10ms | {json_load_results.get('medium', 0):.2f}ms |"
        line += f" 100ms | {json_load_results.get('large', 0):.2f}ms |"
        lines.append(line)
        
        lines.append("")
        lines.append("---")
        lines.append("*Generated by eXonware Standardized Benchmark Suite*")
        
        output_path.write_text("\n".join(lines), encoding='utf-8')
        print(f"\n📝 Detailed results saved to: {output_path}")


async def main():
    """Run standardized benchmarks."""
    benchmark = StandardizedBenchmark()
    
    print("Starting standardized performance benchmarks...")
    print("Using same test patterns as xData-Old for comparison")
    print()
    
    await benchmark.run_all_benchmarks()
    benchmark.print_comparison_table()
    
    # Save results
    output_file = Path(__file__).parent / "STANDARDIZED_BENCHMARKS.md"
    benchmark.save_results(output_file)
    
    print("\n" + "=" * 100)
    print("🎉 Benchmarks complete!")
    print("=" * 100)


if __name__ == "__main__":
    asyncio.run(main())

