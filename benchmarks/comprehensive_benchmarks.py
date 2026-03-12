#!/usr/bin/env python3
"""
#exonware/xwdata/benchmarks/comprehensive_benchmarks.py
Comprehensive Performance Benchmarks for XWData
Tests all aspects of performance to create a complete benchmark
report similar to xData-Old's documented performance metrics.
Company: eXonware.com
Author: eXonware Backend Team
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
from pathlib import Path
from typing import Any
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
@dataclass

class BenchmarkResult:
    """Detailed benchmark measurement."""
    test_name: str
    operation: str
    file_size: str  # 'small', 'medium', 'large', 'huge'
    format: str
    duration_ms: float
    memory_mb: float
    throughput_ops_sec: float = 0.0
    success: bool = True
    error: str = ""
    iterations: int = 1
    @property

    def avg_duration_ms(self) -> float:
        """Average duration per iteration."""
        return self.duration_ms / self.iterations if self.iterations > 0 else self.duration_ms


class ComprehensiveBenchmark:
    """
    Comprehensive benchmark suite covering all performance aspects.
    Benchmark Categories:
    1. File I/O Operations (load/save)
    2. Parse/Serialize Operations
    3. From Native Creation
    4. Navigation Performance
    5. Modification Performance (COW)
    6. Memory Efficiency
    7. Scalability (different data sizes)
    8. Format Comparison (JSON, XML, YAML, TOML, CSV)
    """

    def __init__(self):
        self.results: list[BenchmarkResult] = []
        self.temp_dir = None
        # Test data of different sizes
        self.test_data = {
            'small': self._generate_small_data(),
            'medium': self._generate_medium_data(),
            'large': self._generate_large_data(),
            'huge': self._generate_huge_data()
        }

    def _generate_small_data(self) -> dict:
        """Generate small test data (< 1KB)."""
        return {
            'name': 'Test User',
            'age': 30,
            'email': 'test@example.com',
            'active': True,
            'metadata': {
                'created': '2025-10-28',
                'updated': '2025-10-28'
            }
        }

    def _generate_medium_data(self) -> dict:
        """Generate medium test data (~10-100KB)."""
        return {
            'users': [
                {
                    'id': i,
                    'name': f'User {i}',
                    'email': f'user{i}@example.com',
                    'age': 20 + (i % 50),
                    'active': i % 2 == 0,
                    'profile': {
                        'bio': f'This is user {i}' * 10,
                        'interests': ['coding', 'reading', 'gaming'],
                        'stats': {
                            'posts': i * 10,
                            'followers': i * 5,
                            'following': i * 3
                        }
                    }
                }
                for i in range(100)
            ],
            'metadata': {
                'version': '1.0.0',
                'timestamp': '2025-10-28T12:00:00Z',
                'total_users': 100
            }
        }

    def _generate_large_data(self) -> dict:
        """Generate large test data (~1MB)."""
        return {
            'records': [
                {
                    'id': i,
                    'timestamp': f'2025-10-28T{i%24:02d}:{i%60:02d}:00Z',
                    'data': {
                        'field1': f'value_{i}',
                        'field2': i * 1.5,
                        'field3': i % 100 == 0,
                        'nested': {
                            'level1': {
                                'level2': {
                                    'level3': {
                                        'value': i,
                                        'description': 'x' * 100
                                    }
                                }
                            }
                        }
                    },
                    'tags': [f'tag{j}' for j in range(10)],
                    'metadata': {
                        'source': 'benchmark',
                        'category': f'cat_{i % 20}'
                    }
                }
                for i in range(1000)
            ],
            'summary': {
                'total_records': 1000,
                'date_range': '2025-10-28',
                'categories': 20
            }
        }

    def _generate_huge_data(self) -> dict:
        """Generate huge test data (~10MB)."""
        return {
            'dataset': [
                {
                    'id': i,
                    'data': 'x' * 1000,  # 1KB per item
                    'nested': {
                        'values': list(range(100)),
                        'metadata': {
                            'created_at': f'2025-10-28T{i%24:02d}:00:00Z',
                            'tags': [f't{j}' for j in range(20)]
                        }
                    }
                }
                for i in range(10000)  # 10,000 records
            ],
            'info': {
                'size': 10000,
                'version': '1.0'
            }
        }

    async def setup(self):
        """Setup benchmark environment."""
        self.temp_dir = Path(tempfile.mkdtemp(prefix="xwdata_bench_"))
        print(f"📁 Created temp directory: {self.temp_dir}")

    async def cleanup(self):
        """Cleanup benchmark environment."""
        if self.temp_dir and self.temp_dir.exists():
            import shutil
            shutil.rmtree(self.temp_dir)
            print(f"🧹 Cleaned up temp directory")
    # =========================================================================
    # FILE I/O BENCHMARKS
    # =========================================================================

    async def benchmark_load(self, size: str, format: str, iterations: int = 10) -> BenchmarkResult:
        """Benchmark file loading."""
        from exonware.xwdata import XWData
        data = self.test_data[size]
        file_path = self.temp_dir / f"test_{size}.{format}"
        # Create file first
        try:
            xw = XWData.from_native(data)
            await xw.save(str(file_path), format=format)
        except Exception as e:
            return BenchmarkResult(
                test_name=f"load_{size}_{format}",
                operation="load",
                file_size=size,
                format=format,
                duration_ms=0,
                memory_mb=0,
                success=False,
                error=str(e)
            )
        # Benchmark loading
        try:
            durations = []
            for _ in range(iterations):
                start = time.perf_counter()
                data_loaded = await XWData.load(str(file_path))
                end = time.perf_counter()
                durations.append((end - start) * 1000)
            avg_duration = statistics.mean(durations)
            return BenchmarkResult(
                test_name=f"load_{size}_{format}",
                operation="load",
                file_size=size,
                format=format,
                duration_ms=avg_duration,
                memory_mb=file_path.stat().st_size / (1024 * 1024),
                success=True,
                iterations=iterations
            )
        except Exception as e:
            return BenchmarkResult(
                test_name=f"load_{size}_{format}",
                operation="load",
                file_size=size,
                format=format,
                duration_ms=0,
                memory_mb=0,
                success=False,
                error=str(e),
                iterations=iterations
            )

    async def benchmark_save(self, size: str, format: str, iterations: int = 10) -> BenchmarkResult:
        """Benchmark file saving."""
        from exonware.xwdata import XWData
        data = self.test_data[size]
        try:
            xw = XWData.from_native(data)
            durations = []
            for i in range(iterations):
                file_path = self.temp_dir / f"save_{size}_{i}.{format}"
                start = time.perf_counter()
                await xw.save(str(file_path), format=format)
                end = time.perf_counter()
                durations.append((end - start) * 1000)
            avg_duration = statistics.mean(durations)
            return BenchmarkResult(
                test_name=f"save_{size}_{format}",
                operation="save",
                file_size=size,
                format=format,
                duration_ms=avg_duration,
                memory_mb=0,
                success=True,
                iterations=iterations
            )
        except Exception as e:
            return BenchmarkResult(
                test_name=f"save_{size}_{format}",
                operation="save",
                file_size=size,
                format=format,
                duration_ms=0,
                memory_mb=0,
                success=False,
                error=str(e),
                iterations=iterations
            )
    # =========================================================================
    # FROM NATIVE BENCHMARKS
    # =========================================================================

    async def benchmark_from_native(self, size: str, iterations: int = 100) -> BenchmarkResult:
        """Benchmark creating XWData from native data."""
        from exonware.xwdata import XWData
        data = self.test_data[size]
        try:
            durations = []
            for _ in range(iterations):
                start = time.perf_counter()
                xw = XWData.from_native(data)
                end = time.perf_counter()
                durations.append((end - start) * 1000)
            avg_duration = statistics.mean(durations)
            return BenchmarkResult(
                test_name=f"from_native_{size}",
                operation="from_native",
                file_size=size,
                format="native",
                duration_ms=avg_duration,
                memory_mb=0,
                success=True,
                iterations=iterations
            )
        except Exception as e:
            return BenchmarkResult(
                test_name=f"from_native_{size}",
                operation="from_native",
                file_size=size,
                format="native",
                duration_ms=0,
                memory_mb=0,
                success=False,
                error=str(e),
                iterations=iterations
            )
    # =========================================================================
    # NAVIGATION BENCHMARKS
    # =========================================================================

    async def benchmark_navigation(self, size: str, iterations: int = 1000) -> BenchmarkResult:
        """Benchmark path navigation."""
        from exonware.xwdata import XWData
        data = self.test_data[size]
        # Different paths for different data sizes
        paths = {
            'small': 'name',
            'medium': 'users.0.name',
            'large': 'records.0.data.nested.level1.level2.level3.value',
            'huge': 'dataset.0.nested.metadata.created_at'
        }
        path = paths.get(size, 'name')
        try:
            xw = XWData.from_native(data)
            start = time.perf_counter()
            for _ in range(iterations):
                value = await xw.get(path)
            end = time.perf_counter()
            total_duration = (end - start) * 1000
            ops_per_sec = iterations / ((end - start) if (end - start) > 0 else 0.001)
            return BenchmarkResult(
                test_name=f"navigation_{size}_{iterations}x",
                operation="navigation",
                file_size=size,
                format="native",
                duration_ms=total_duration,
                memory_mb=0,
                throughput_ops_sec=ops_per_sec,
                success=True,
                iterations=iterations
            )
        except Exception as e:
            return BenchmarkResult(
                test_name=f"navigation_{size}_{iterations}x",
                operation="navigation",
                file_size=size,
                format="native",
                duration_ms=0,
                memory_mb=0,
                success=False,
                error=str(e),
                iterations=iterations
            )
    # =========================================================================
    # MODIFICATION BENCHMARKS (COW)
    # =========================================================================

    async def benchmark_modification(self, size: str, iterations: int = 100) -> BenchmarkResult:
        """Benchmark COW modifications."""
        from exonware.xwdata import XWData
        data = self.test_data[size]
        # Different paths for different data sizes
        paths = {
            'small': 'age',
            'medium': 'users.0.age',
            'large': 'records.0.data.field2',
            'huge': 'dataset.0.nested.values.0'
        }
        path = paths.get(size, 'age')
        try:
            xw = XWData.from_native(data)
            durations = []
            for i in range(iterations):
                start = time.perf_counter()
                new_xw = await xw.set(path, i)
                end = time.perf_counter()
                durations.append((end - start) * 1000)
            avg_duration = statistics.mean(durations)
            return BenchmarkResult(
                test_name=f"modification_{size}",
                operation="modification_cow",
                file_size=size,
                format="native",
                duration_ms=avg_duration,
                memory_mb=0,
                success=True,
                iterations=iterations
            )
        except Exception as e:
            return BenchmarkResult(
                test_name=f"modification_{size}",
                operation="modification_cow",
                file_size=size,
                format="native",
                duration_ms=0,
                memory_mb=0,
                success=False,
                error=str(e),
                iterations=iterations
            )
    # =========================================================================
    # PARSE/SERIALIZE BENCHMARKS
    # =========================================================================

    async def benchmark_parse(self, size: str, format: str, iterations: int = 10) -> BenchmarkResult:
        """Benchmark parsing from string."""
        from exonware.xwdata import XWData
        data = self.test_data[size]
        try:
            # Create serialized content first
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
                test_name=f"parse_{size}_{format}",
                operation="parse",
                file_size=size,
                format=format,
                duration_ms=avg_duration,
                memory_mb=len(content) / (1024 * 1024) if isinstance(content, (str, bytes)) else 0,
                success=True,
                iterations=iterations
            )
        except Exception as e:
            return BenchmarkResult(
                test_name=f"parse_{size}_{format}",
                operation="parse",
                file_size=size,
                format=format,
                duration_ms=0,
                memory_mb=0,
                success=False,
                error=str(e),
                iterations=iterations
            )

    async def benchmark_serialize(self, size: str, format: str, iterations: int = 10) -> BenchmarkResult:
        """Benchmark serialization to string."""
        from exonware.xwdata import XWData
        data = self.test_data[size]
        try:
            xw = XWData.from_native(data)
            durations = []
            for _ in range(iterations):
                start = time.perf_counter()
                content = await xw.serialize(format=format)
                end = time.perf_counter()
                durations.append((end - start) * 1000)
            avg_duration = statistics.mean(durations)
            return BenchmarkResult(
                test_name=f"serialize_{size}_{format}",
                operation="serialize",
                file_size=size,
                format=format,
                duration_ms=avg_duration,
                memory_mb=0,
                success=True,
                iterations=iterations
            )
        except Exception as e:
            return BenchmarkResult(
                test_name=f"serialize_{size}_{format}",
                operation="serialize",
                file_size=size,
                format=format,
                duration_ms=0,
                memory_mb=0,
                success=False,
                error=str(e),
                iterations=iterations
            )
    # =========================================================================
    # RUN ALL BENCHMARKS
    # =========================================================================

    async def run_all_benchmarks(self):
        """Run comprehensive benchmark suite."""
        print("=" * 100)
        print("🚀 COMPREHENSIVE XWDATA PERFORMANCE BENCHMARKS")
        print("=" * 100)
        print()
        await self.setup()
        try:
            # 1. File I/O Benchmarks
            print("\n📁 1. FILE I/O BENCHMARKS")
            print("-" * 100)
            sizes = ['small', 'medium', 'large']
            formats = ['json', 'yaml', 'xml', 'toml']
            for size in sizes:
                print(f"\n  Testing {size.upper()} data...")
                for fmt in formats:
                    print(f"    - {fmt.upper()}...", end=" ", flush=True)
                    # Load benchmark
                    result = await self.benchmark_load(size, fmt, iterations=10)
                    self.results.append(result)
                    if result.success:
                        print(f"✅ Load: {result.avg_duration_ms:.2f}ms", end=" | ")
                    else:
                        print(f"❌ Load failed", end=" | ")
                    # Save benchmark
                    result = await self.benchmark_save(size, fmt, iterations=10)
                    self.results.append(result)
                    if result.success:
                        print(f"Save: {result.avg_duration_ms:.2f}ms ✅")
                    else:
                        print(f"Save failed ❌")
            # 2. From Native Benchmarks
            print("\n\n🏗️  2. FROM NATIVE BENCHMARKS")
            print("-" * 100)
            for size in ['small', 'medium', 'large', 'huge']:
                print(f"  - {size.upper()}...", end=" ", flush=True)
                result = await self.benchmark_from_native(size, iterations=100)
                self.results.append(result)
                if result.success:
                    print(f"✅ {result.avg_duration_ms:.4f}ms")
                else:
                    print(f"❌ Failed: {result.error}")
            # 3. Navigation Benchmarks
            print("\n\n🧭 3. NAVIGATION BENCHMARKS")
            print("-" * 100)
            for size in ['small', 'medium', 'large', 'huge']:
                print(f"  - {size.upper()} (1000x)...", end=" ", flush=True)
                result = await self.benchmark_navigation(size, iterations=1000)
                self.results.append(result)
                if result.success:
                    print(f"✅ {result.avg_duration_ms:.4f}ms/op ({result.throughput_ops_sec:,.0f} ops/sec)")
                else:
                    print(f"❌ Failed: {result.error}")
            # 4. Modification Benchmarks (COW)
            print("\n\n✏️  4. MODIFICATION (COW) BENCHMARKS")
            print("-" * 100)
            for size in ['small', 'medium', 'large']:
                print(f"  - {size.upper()} (100x)...", end=" ", flush=True)
                result = await self.benchmark_modification(size, iterations=100)
                self.results.append(result)
                if result.success:
                    print(f"✅ {result.avg_duration_ms:.4f}ms/op")
                else:
                    print(f"❌ Failed: {result.error}")
            # 5. Parse/Serialize Benchmarks
            print("\n\n🔄 5. PARSE/SERIALIZE BENCHMARKS")
            print("-" * 100)
            for size in ['small', 'medium', 'large']:
                print(f"\n  {size.upper()} data:")
                for fmt in ['json', 'yaml', 'xml']:
                    print(f"    - {fmt.upper()}...", end=" ", flush=True)
                    # Parse
                    result = await self.benchmark_parse(size, fmt, iterations=10)
                    self.results.append(result)
                    if result.success:
                        print(f"Parse: {result.avg_duration_ms:.2f}ms", end=" | ")
                    else:
                        print(f"Parse failed", end=" | ")
                    # Serialize
                    result = await self.benchmark_serialize(size, fmt, iterations=10)
                    self.results.append(result)
                    if result.success:
                        print(f"Serialize: {result.avg_duration_ms:.2f}ms ✅")
                    else:
                        print(f"Serialize failed ❌")
            print("\n\n✅ All benchmarks complete!")
        finally:
            await self.cleanup()
    # =========================================================================
    # REPORTING
    # =========================================================================

    def print_summary(self):
        """Print benchmark summary."""
        print("\n" + "=" * 100)
        print("📊 BENCHMARK SUMMARY")
        print("=" * 100)
        print()
        # Group results by operation
        operations = {}
        for result in self.results:
            if result.success:
                if result.operation not in operations:
                    operations[result.operation] = []
                operations[result.operation].append(result)
        for operation, results in operations.items():
            print(f"\n{operation.upper().replace('_', ' ')}:")
            print("-" * 100)
            # Create comparison table
            if operation in ['load', 'save', 'parse', 'serialize']:
                # Group by size and format
                size_format_results = {}
                for r in results:
                    key = (r.file_size, r.format)
                    size_format_results[key] = r
                print(f"{'Size':<10} | {'Format':<8} | {'Duration (ms)':<15} | {'Status':<10}")
                print("-" * 60)
                for (size, fmt), r in sorted(size_format_results.items()):
                    status = "✅ OK" if r.success else "❌ FAIL"
                    print(f"{size:<10} | {fmt:<8} | {r.avg_duration_ms:>14.2f} | {status:<10}")
            elif operation in ['from_native', 'navigation', 'modification_cow']:
                print(f"{'Size':<10} | {'Duration (ms)':<15} | {'Throughput':<20} | {'Status':<10}")
                print("-" * 70)
                for r in sorted(results, key=lambda x: x.file_size):
                    status = "✅ OK" if r.success else "❌ FAIL"
                    throughput = f"{r.throughput_ops_sec:,.0f} ops/sec" if r.throughput_ops_sec > 0 else "N/A"
                    print(f"{r.file_size:<10} | {r.avg_duration_ms:>14.4f} | {throughput:<20} | {status:<10}")

    def save_results(self, output_path: Path):
        """Save results to markdown file."""
        lines = []
        lines.append("# Comprehensive XWData Performance Benchmarks")
        lines.append("")
        lines.append(f"**Date:** {time.strftime('%Y-%m-%d %H:%M:%S')}")
        lines.append(f"**Python:** {sys.version}")
        lines.append(f"**Total Tests:** {len(self.results)}")
        lines.append(f"**Successful:** {sum(1 for r in self.results if r.success)}")
        lines.append(f"**Failed:** {sum(1 for r in self.results if not r.success)}")
        lines.append("")
        # Group by operation
        operations = {}
        for result in self.results:
            if result.operation not in operations:
                operations[result.operation] = []
            operations[result.operation].append(result)
        for operation, results in sorted(operations.items()):
            lines.append(f"## {operation.upper().replace('_', ' ')}")
            lines.append("")
            if operation in ['load', 'save']:
                lines.append("| Size | Format | Avg Duration (ms) | Status |")
                lines.append("|------|--------|-------------------|--------|")
                for r in sorted(results, key=lambda x: (x.file_size, x.format)):
                    status = "✅" if r.success else f"❌ {r.error}"
                    lines.append(f"| {r.file_size} | {r.format} | {r.avg_duration_ms:.2f} | {status} |")
            elif operation in ['from_native', 'navigation', 'modification_cow']:
                lines.append("| Size | Avg Duration (ms) | Throughput | Status |")
                lines.append("|------|-------------------|------------|--------|")
                for r in sorted(results, key=lambda x: x.file_size):
                    status = "✅" if r.success else f"❌ {r.error}"
                    throughput = f"{r.throughput_ops_sec:,.0f} ops/sec" if r.throughput_ops_sec > 0 else "N/A"
                    lines.append(f"| {r.file_size} | {r.avg_duration_ms:.4f} | {throughput} | {status} |")
            elif operation in ['parse', 'serialize']:
                lines.append("| Size | Format | Avg Duration (ms) | Status |")
                lines.append("|------|--------|-------------------|--------|")
                for r in sorted(results, key=lambda x: (x.file_size, x.format)):
                    status = "✅" if r.success else f"❌ {r.error}"
                    lines.append(f"| {r.file_size} | {r.format} | {r.avg_duration_ms:.2f} | {status} |")
            lines.append("")
        # Summary statistics
        lines.append("## Summary Statistics")
        lines.append("")
        successful = [r for r in self.results if r.success]
        if successful:
            lines.append(f"- **Fastest Operation:** {min(successful, key=lambda x: x.avg_duration_ms).test_name} ({min(successful, key=lambda x: x.avg_duration_ms).avg_duration_ms:.4f}ms)")
            lines.append(f"- **Slowest Operation:** {max(successful, key=lambda x: x.avg_duration_ms).test_name} ({max(successful, key=lambda x: x.avg_duration_ms).avg_duration_ms:.2f}ms)")
            nav_results = [r for r in successful if r.operation == 'navigation']
            if nav_results:
                best_nav = max(nav_results, key=lambda x: x.throughput_ops_sec)
                lines.append(f"- **Best Navigation Throughput:** {best_nav.throughput_ops_sec:,.0f} ops/sec ({best_nav.file_size})")
        lines.append("")
        lines.append("---")
        lines.append("*Generated by eXonware Comprehensive Benchmark Suite*")
        output_path.write_text("\n".join(lines), encoding='utf-8')
        print(f"\n📝 Detailed results saved to: {output_path}")
async def main():
    """Run comprehensive benchmarks."""
    benchmark = ComprehensiveBenchmark()
    print("Starting comprehensive performance benchmarks...")
    print("This may take a few minutes...")
    print()
    await benchmark.run_all_benchmarks()
    benchmark.print_summary()
    # Save results
    output_file = Path(__file__).parent / "COMPREHENSIVE_BENCHMARKS.md"
    benchmark.save_results(output_file)
    print("\n" + "=" * 100)
    print("🎉 All benchmarks complete!")
    print("=" * 100)
if __name__ == "__main__":
    asyncio.run(main())
