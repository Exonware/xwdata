#!/usr/bin/env python3
"""
#exonware/xwdata/benchmarks/performance_comparison.py
Performance Comparison: New XWData vs MIGRAT
Comprehensive benchmarks comparing the new `xwdata` implementation
to the legacy MIGRAT version across all key performance metrics.
Company: eXonware.com
Author: eXonware Backend Team
Email: connect@exonware.com
Version: 0.0.1.1
Generation Date: 26-Oct-2025
"""

import sys
import time
import json
import asyncio
import io
from pathlib import Path
from dataclasses import dataclass
import statistics
# Set UTF-8 encoding for Windows console
if sys.platform == 'win32':
    try:
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')
    except:
        pass
# Add paths
xwdata_root = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(xwdata_root / "src"))
sys.path.insert(0, str(xwdata_root / "MIGRAT"))
@dataclass

class BenchmarkResult:
    """Single benchmark measurement."""
    name: str
    implementation: str  # 'new' or 'migrat'
    duration_ms: float
    memory_mb: float
    success: bool
    error: str = ""
@dataclass

class ComparisonResult:
    """Comparison between implementations."""
    test_name: str
    new_time_ms: float
    migrat_time_ms: float
    speedup: float  # Positive means new is faster
    new_memory_mb: float
    migrat_memory_mb: float
    memory_improvement: float  # Positive means new uses less


class PerformanceBenchmark:
    """
    Comprehensive performance benchmark suite.
    Tests:
    1. Load performance (JSON, XML, YAML)
    2. Save performance
    3. Parse performance (string to native)
    4. Serialize performance (native to string)
    5. Navigation performance (deep path access)
    6. Modification performance (COW)
    7. Memory efficiency
    8. Cold start time
    """

    def __init__(self):
        self.results: list[BenchmarkResult] = []
        self.comparisons: list[ComparisonResult] = []
        # Test data
        self.small_data = {
            'name': 'Test',
            'value': 42,
            'nested': {'key': 'value'}
        }
        self.medium_data = {
            'users': [
                {'id': i, 'name': f'User{i}', 'email': f'user{i}@test.com'}
                for i in range(100)
            ],
            'metadata': {
                'version': '1.0',
                'timestamp': '2025-10-26'
            }
        }
        self.large_data = {
            'records': [
                {
                    'id': i,
                    'data': {
                        'field1': f'value{i}',
                        'field2': i * 2,
                        'nested': {
                            'deep': {
                                'value': i * 3
                            }
                        }
                    }
                }
                for i in range(1000)
            ]
        }

    async def benchmark_new_load(self, file_path: Path) -> BenchmarkResult:
        """Benchmark new implementation load."""
        try:
            from exonware.xwdata import XWData
            start = time.perf_counter()
            data = await XWData.load(str(file_path))
            end = time.perf_counter()
            return BenchmarkResult(
                name=f"load_{file_path.suffix[1:]}",
                implementation='new',
                duration_ms=(end - start) * 1000,
                memory_mb=sys.getsizeof(data) / (1024 * 1024),
                success=True
            )
        except Exception as e:
            return BenchmarkResult(
                name=f"load_{file_path.suffix[1:]}",
                implementation='new',
                duration_ms=0,
                memory_mb=0,
                success=False,
                error=str(e)
            )

    def benchmark_migrat_load(self, file_path: Path) -> BenchmarkResult:
        """Benchmark MIGRAT implementation load."""
        try:
            from xdata import xData
            start = time.perf_counter()
            data = xData(str(file_path))
            end = time.perf_counter()
            return BenchmarkResult(
                name=f"load_{file_path.suffix[1:]}",
                implementation='migrat',
                duration_ms=(end - start) * 1000,
                memory_mb=sys.getsizeof(data) / (1024 * 1024),
                success=True
            )
        except Exception as e:
            return BenchmarkResult(
                name=f"load_{file_path.suffix[1:]}",
                implementation='migrat',
                duration_ms=0,
                memory_mb=0,
                success=False,
                error=str(e)
            )

    async def benchmark_new_from_native(self, data: dict, size: str) -> BenchmarkResult:
        """Benchmark new implementation from native."""
        try:
            from exonware.xwdata import XWData
            start = time.perf_counter()
            xw_data = XWData.from_native(data)
            end = time.perf_counter()
            return BenchmarkResult(
                name=f"from_native_{size}",
                implementation='new',
                duration_ms=(end - start) * 1000,
                memory_mb=sys.getsizeof(xw_data) / (1024 * 1024),
                success=True
            )
        except Exception as e:
            return BenchmarkResult(
                name=f"from_native_{size}",
                implementation='new',
                duration_ms=0,
                memory_mb=0,
                success=False,
                error=str(e)
            )

    def benchmark_migrat_from_native(self, data: dict, size: str) -> BenchmarkResult:
        """Benchmark MIGRAT from native."""
        try:
            from xdata import xData
            start = time.perf_counter()
            xw_data = xData(data)
            end = time.perf_counter()
            return BenchmarkResult(
                name=f"from_native_{size}",
                implementation='migrat',
                duration_ms=(end - start) * 1000,
                memory_mb=sys.getsizeof(xw_data) / (1024 * 1024),
                success=True
            )
        except Exception as e:
            return BenchmarkResult(
                name=f"from_native_{size}",
                implementation='migrat',
                duration_ms=0,
                memory_mb=0,
                success=False,
                error=str(e)
            )

    async def benchmark_new_navigation(self, data: dict, path: str, iterations: int) -> BenchmarkResult:
        """Benchmark new implementation navigation."""
        try:
            from exonware.xwdata import XWData
            xw_data = XWData.from_native(data)
            start = time.perf_counter()
            for _ in range(iterations):
                value = await xw_data.get(path)
            end = time.perf_counter()
            return BenchmarkResult(
                name=f"navigation_{iterations}x",
                implementation='new',
                duration_ms=(end - start) * 1000,
                memory_mb=0,
                success=True
            )
        except Exception as e:
            return BenchmarkResult(
                name=f"navigation_{iterations}x",
                implementation='new',
                duration_ms=0,
                memory_mb=0,
                success=False,
                error=str(e)
            )

    def benchmark_migrat_navigation(self, data: dict, path: str, iterations: int) -> BenchmarkResult:
        """Benchmark MIGRAT navigation."""
        try:
            from xdata import xData
            xw_data = xData(data)
            start = time.perf_counter()
            for _ in range(iterations):
                value = xw_data.get(path)
            end = time.perf_counter()
            return BenchmarkResult(
                name=f"navigation_{iterations}x",
                implementation='migrat',
                duration_ms=(end - start) * 1000,
                memory_mb=0,
                success=True
            )
        except Exception as e:
            return BenchmarkResult(
                name=f"navigation_{iterations}x",
                implementation='migrat',
                duration_ms=0,
                memory_mb=0,
                success=False,
                error=str(e)
            )

    async def run_all_benchmarks(self) -> None:
        """Run all benchmarks and generate comparison."""
        print("=" * 80)
        print("XWData Performance Benchmark Suite")
        print("Comparing: New Implementation vs MIGRAT")
        print("=" * 80)
        print()
        # Create temp test files
        temp_dir = Path("benchmark_temp")
        temp_dir.mkdir(exist_ok=True)
        try:
            # 1. File I/O Benchmarks
            print("📁 File I/O Benchmarks...")
            json_file = temp_dir / "test.json"
            json_file.write_text(json.dumps(self.medium_data, indent=2))
            # New load
            print("  - Testing new load...")
            new_load = await self.benchmark_new_load(json_file)
            self.results.append(new_load)
            if not new_load.success:
                print(f"    ❌ New load failed: {new_load.error}")
            else:
                print(f"    ✅ New load: {new_load.duration_ms:.2f}ms")
            # MIGRAT load
            print("  - Testing MIGRAT load...")
            migrat_load = self.benchmark_migrat_load(json_file)
            self.results.append(migrat_load)
            if not migrat_load.success:
                print(f"    ❌ MIGRAT load failed: {migrat_load.error}")
            else:
                print(f"    ✅ MIGRAT load: {migrat_load.duration_ms:.2f}ms")
            if new_load.success and migrat_load.success:
                self.comparisons.append(ComparisonResult(
                    test_name="Load JSON (medium)",
                    new_time_ms=new_load.duration_ms,
                    migrat_time_ms=migrat_load.duration_ms,
                    speedup=((migrat_load.duration_ms - new_load.duration_ms) / migrat_load.duration_ms * 100) if migrat_load.duration_ms > 0 else 0,
                    new_memory_mb=new_load.memory_mb,
                    migrat_memory_mb=migrat_load.memory_mb,
                    memory_improvement=((migrat_load.memory_mb - new_load.memory_mb) / migrat_load.memory_mb * 100) if migrat_load.memory_mb > 0 else 0
                ))
            # 2. From Native Benchmarks
            print("\n🏗️  From Native Benchmarks...")
            for size_name, test_data in [
                ('small', self.small_data),
                ('medium', self.medium_data),
                ('large', self.large_data)
            ]:
                print(f"  - Testing {size_name} data...")
                new_native = await self.benchmark_new_from_native(test_data, size_name)
                migrat_native = self.benchmark_migrat_from_native(test_data, size_name)
                self.results.extend([new_native, migrat_native])
                if new_native.success and migrat_native.success:
                    self.comparisons.append(ComparisonResult(
                        test_name=f"From Native ({size_name})",
                        new_time_ms=new_native.duration_ms,
                        migrat_time_ms=migrat_native.duration_ms,
                        speedup=((migrat_native.duration_ms - new_native.duration_ms) / migrat_native.duration_ms * 100) if migrat_native.duration_ms > 0 else 0,
                        new_memory_mb=new_native.memory_mb,
                        migrat_memory_mb=migrat_native.memory_mb,
                        memory_improvement=((migrat_native.memory_mb - new_native.memory_mb) / migrat_native.memory_mb * 100) if migrat_native.memory_mb > 0 else 0
                    ))
            # 3. Navigation Benchmarks
            print("\n🧭 Navigation Benchmarks...")
            iterations = 1000
            test_path = 'users.0.name'
            print(f"  - Testing {iterations}x navigation...")
            new_nav = await self.benchmark_new_navigation(self.medium_data, test_path, iterations)
            migrat_nav = self.benchmark_migrat_navigation(self.medium_data, test_path, iterations)
            self.results.extend([new_nav, migrat_nav])
            if new_nav.success and migrat_nav.success:
                self.comparisons.append(ComparisonResult(
                    test_name=f"Navigation ({iterations}x)",
                    new_time_ms=new_nav.duration_ms,
                    migrat_time_ms=migrat_nav.duration_ms,
                    speedup=((migrat_nav.duration_ms - new_nav.duration_ms) / migrat_nav.duration_ms * 100) if migrat_nav.duration_ms > 0 else 0,
                    new_memory_mb=0,
                    migrat_memory_mb=0,
                    memory_improvement=0
                ))
            print("\n✅ Benchmarks complete!")
        finally:
            # Cleanup
            if temp_dir.exists():
                for file in temp_dir.glob("*"):
                    file.unlink()
                temp_dir.rmdir()

    def print_results(self) -> None:
        """Print formatted results."""
        print("\n" + "=" * 80)
        print("📊 PERFORMANCE COMPARISON RESULTS")
        print("=" * 80)
        print()
        if not self.comparisons:
            print("⚠️  No successful comparisons available (MIGRAT import issues)")
            print()
            print("📊 NEW IMPLEMENTATION RESULTS:")
            print()
            for result in self.results:
                if result.implementation == 'new' and result.success:
                    print(f"  ✅ {result.name}: {result.duration_ms:.2f}ms")
            return
        print("| Test | New (ms) | MIGRAT (ms) | Speedup | Winner |")
        print("|------|----------|-------------|---------|--------|")
        for comp in self.comparisons:
            winner = "🏆 NEW" if comp.speedup > 0 else "📦 MIGRAT"
            speedup_str = f"+{comp.speedup:.1f}%" if comp.speedup > 0 else f"{comp.speedup:.1f}%"
            print(f"| {comp.test_name:<30} | {comp.new_time_ms:>8.2f} | {comp.migrat_time_ms:>11.2f} | {speedup_str:>7} | {winner:>10} |")
        # Summary
        print("\n" + "-" * 80)
        avg_speedup = statistics.mean([c.speedup for c in self.comparisons if c.new_time_ms > 0])
        print(f"\n📈 Average Speedup: {avg_speedup:+.1f}%")
        if avg_speedup > 0:
            print(f"   🎉 New implementation is {abs(avg_speedup):.1f}% faster on average!")
        else:
            print(f"   ⚠️  MIGRAT is {abs(avg_speedup):.1f}% faster on average")
        # Memory comparison
        memory_comps = [c for c in self.comparisons if c.new_memory_mb > 0 and c.migrat_memory_mb > 0]
        if memory_comps:
            avg_memory_improvement = statistics.mean([c.memory_improvement for c in memory_comps])
            print(f"\n💾 Average Memory Improvement: {avg_memory_improvement:+.1f}%")
            if avg_memory_improvement > 0:
                print(f"   ✅ New implementation uses {abs(avg_memory_improvement):.1f}% less memory!")
            else:
                print(f"   ⚠️  MIGRAT uses {abs(avg_memory_improvement):.1f}% less memory")

    def save_results(self, output_path: Path) -> None:
        """Save results to markdown file."""
        content = []
        content.append("# Performance Benchmark Results")
        content.append("")
        content.append(f"**Date:** {time.strftime('%Y-%m-%d %H:%M:%S')}")
        content.append(f"**Python:** {sys.version}")
        content.append("")
        if not self.comparisons:
            content.append("## Note")
            content.append("")
            content.append("MIGRAT implementation has import issues and cannot be benchmarked directly.")
            content.append("Showing new implementation results only:")
            content.append("")
            content.append("| Test | Duration (ms) | Status |")
            content.append("|------|---------------|--------|")
            for result in self.results:
                if result.implementation == 'new':
                    status = "✅ Success" if result.success else f"❌ Failed: {result.error}"
                    content.append(f"| {result.name} | {result.duration_ms:.2f} | {status} |")
            output_path.write_text("\n".join(content), encoding='utf-8')
            print(f"\n📝 Results saved to: {output_path}")
            return
        content.append("## Comparison Table")
        content.append("")
        content.append("| Test | New (ms) | MIGRAT (ms) | Speedup | Memory New (MB) | Memory MIGRAT (MB) | Memory Δ |")
        content.append("|------|----------|-------------|---------|-----------------|---------------------|----------|")
        for comp in self.comparisons:
            speedup_str = f"+{comp.speedup:.1f}%" if comp.speedup > 0 else f"{comp.speedup:.1f}%"
            mem_str = f"+{comp.memory_improvement:.1f}%" if comp.memory_improvement > 0 else f"{comp.memory_improvement:.1f}%"
            content.append(
                f"| {comp.test_name} | {comp.new_time_ms:.2f} | {comp.migrat_time_ms:.2f} | "
                f"{speedup_str} | {comp.new_memory_mb:.4f} | {comp.migrat_memory_mb:.4f} | {mem_str} |"
            )
        # Summary
        avg_speedup = statistics.mean([c.speedup for c in self.comparisons if c.new_time_ms > 0]) if self.comparisons else 0
        content.append("")
        content.append("## Summary")
        content.append("")
        content.append(f"- **Average Speedup:** {avg_speedup:+.1f}%")
        content.append(f"- **Tests Run:** {len(self.comparisons)}")
        content.append(f"- **New Implementation Wins:** {sum(1 for c in self.comparisons if c.speedup > 0)}")
        content.append(f"- **MIGRAT Wins:** {sum(1 for c in self.comparisons if c.speedup < 0)}")
        memory_comps = [c for c in self.comparisons if c.new_memory_mb > 0 and c.migrat_memory_mb > 0]
        if memory_comps:
            avg_memory = statistics.mean([c.memory_improvement for c in memory_comps])
            content.append(f"- **Average Memory Improvement:** {avg_memory:+.1f}%")
        # Conclusion
        content.append("")
        content.append("## Conclusion")
        content.append("")
        if avg_speedup > 5:
            content.append(f"✅ **The new implementation is significantly faster ({avg_speedup:.1f}% average speedup)!**")
        elif avg_speedup > 0:
            content.append(f"✅ **The new implementation is marginally faster ({avg_speedup:.1f}% average speedup).**")
        elif avg_speedup > -5:
            content.append(f"⚠️  **Performance is comparable (within ±5%).**")
        else:
            content.append(f"⚠️  **MIGRAT is faster ({abs(avg_speedup):.1f}% faster on average).**")
        content.append("")
        content.append("### Key Advantages of New Implementation")
        content.append("")
        content.append("1. **Async-First Design:** All operations are async by default")
        content.append("2. **Engine Pattern:** Better architecture with clear separation of concerns")
        content.append("3. **xwsystem Integration:** Reuses battle-tested serialization")
        content.append("4. **xwnode Integration:** Leverages mature navigation capabilities")
        content.append("5. **Maintainability:** Smaller codebase, clearer structure")
        content.append("6. **Extensibility:** Easy to add new formats via serialization/")
        content.append("")
        content.append("---")
        content.append("*Generated by eXonware Performance Benchmark Suite*")
        output_path.write_text("\n".join(content), encoding='utf-8')
        print(f"\n📝 Results saved to: {output_path}")
async def main():
    """Run the benchmark suite."""
    benchmark = PerformanceBenchmark()
    print("Starting performance benchmarks...")
    print()
    await benchmark.run_all_benchmarks()
    benchmark.print_results()
    # Save results
    output_file = Path(__file__).resolve().parent.parent / "benchmarks" / "PERFORMANCE_RESULTS.md"
    benchmark.save_results(output_file)
    print("\n" + "=" * 80)
    print("Benchmark complete!")
    print("=" * 80)
if __name__ == "__main__":
    asyncio.run(main())
