"""Check library sizes for all JSON parsers."""

import sys
import os
from pathlib import Path

def get_package_size(package_name: str) -> dict:
    """Get package size information."""
    try:
        import importlib.util
        # Try to find the package
        try:
            spec = importlib.util.find_spec(package_name)
            if spec is None or spec.origin is None:
                return {"found": False, "error": "Package not found"}
            # Get the package location
            if spec.submodule_search_locations:
                # It's a package (directory)
                package_path = Path(spec.submodule_search_locations[0])
            else:
                # It's a module (file) - get the file itself
                package_path = Path(spec.origin)
                if package_path.is_file():
                    # Single file module - just get the file size
                    return {
                        "found": True,
                        "path": str(package_path),
                        "size_bytes": package_path.stat().st_size,
                        "size_kb": package_path.stat().st_size / 1024,
                        "size_mb": package_path.stat().st_size / 1024 / 1024,
                        "file_count": 1,
                    }
                else:
                    package_path = package_path.parent
            # Calculate total size - only count files in the package directory
            total_size = 0
            file_count = 0
            if package_path.exists():
                # Get the package root (the directory containing the package)
                package_root = package_path.parent
                package_dir_name = package_path.name
                # Walk only the package directory
                for root, dirs, files in os.walk(package_path):
                    # Skip __pycache__ and .pyc files
                    dirs[:] = [d for d in dirs if d != "__pycache__"]
                    for file in files:
                        if not file.endswith(".pyc") and not file.endswith(".pyo"):
                            file_path = Path(root) / file
                            try:
                                size = file_path.stat().st_size
                                total_size += size
                                file_count += 1
                            except:
                                pass
            return {
                "found": True,
                "path": str(package_path),
                "size_bytes": total_size,
                "size_kb": total_size / 1024,
                "size_mb": total_size / 1024 / 1024,
                "file_count": file_count,
            }
        except Exception as e:
            return {"found": False, "error": str(e)}
    except ImportError:
        return {"found": False, "error": "importlib not available"}


def main():
    """Check sizes of all JSON parser libraries."""
    print("=" * 70)
    print("LIBRARY SIZE CHECK: JSON Parsers")
    print("=" * 70)
    print()
    packages = [
        ("orjson", "orjson"),
        ("msgspec", "msgspec"),
        ("ujson", "ujson"),
        ("pysimdjson", "simdjson"),  # Package name vs import name
        ("python-rapidjson", "rapidjson"),
        ("stdlib json", None),  # Built-in, no package
    ]
    results = []
    for package_name, import_name in packages:
        if import_name is None:
            # stdlib json is built-in
            print(f"{package_name}:")
            print("  Built-in (part of Python standard library)")
            print("  Size: ~0 KB (included in Python)")
            print()
            results.append({
                "package": package_name,
                "size_kb": 0,
                "note": "Built-in"
            })
        else:
            print(f"{package_name} (import: {import_name}):")
            try:
                __import__(import_name)
                info = get_package_size(import_name)
                if info.get("found"):
                    print(f"  Path: {info['path']}")
                    print(f"  Size: {info['size_kb']:.2f} KB ({info['size_mb']:.2f} MB)")
                    print(f"  Files: {info['file_count']}")
                    results.append({
                        "package": package_name,
                        "size_kb": info["size_kb"],
                        "size_mb": info["size_mb"],
                        "file_count": info["file_count"],
                    })
                else:
                    print(f"  [ERROR] {info.get('error', 'Not found')}")
                    results.append({
                        "package": package_name,
                        "size_kb": None,
                        "error": info.get("error"),
                    })
            except ImportError:
                print(f"  [NOT INSTALLED]")
                results.append({
                    "package": package_name,
                    "size_kb": None,
                    "error": "Not installed",
                })
            print()
    # Summary table
    print("=" * 70)
    print("SUMMARY TABLE")
    print("=" * 70)
    print()
    print(f"{'Package':<25} {'Size (KB)':<15} {'Size (MB)':<15} {'Files':<10}")
    print("-" * 65)
    for result in results:
        package = result["package"]
        if result.get("size_kb") is not None:
            size_kb = result["size_kb"]
            size_mb = result.get("size_mb", size_kb / 1024)
            file_count = result.get("file_count", "N/A")
            print(f"{package:<25} {size_kb:<15.2f} {size_mb:<15.2f} {file_count}")
        else:
            error = result.get("error", "N/A")
            print(f"{package:<25} {'N/A':<15} {'N/A':<15} {error}")
    print()
if __name__ == "__main__":
    import importlib.util
    main()
