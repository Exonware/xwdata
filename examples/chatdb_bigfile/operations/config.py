"""Configuration for performance optimizations.

This module provides configuration options to enable/disable optimizations
and fallback to original implementations.
"""

from dataclasses import dataclass
from pathlib import Path


@dataclass
class PerformanceConfig:
    """Configuration for performance optimizations."""
    
    # Parallel index building
    enable_parallel_index: bool = True  # Auto-enabled for large files
    parallel_index_workers: int | None = None  # None = auto (CPU count)
    parallel_index_chunk_size_mb: int = 100  # 100MB chunks
    
    # Append-only log for atomic updates
    enable_append_log: bool = True  # Auto-enabled for large files
    append_log_compaction_threshold_mb: int = 100  # Compact when log > 100MB
    
    # Fallback behavior
    fallback_on_error: bool = True  # Fall back to original if optimization fails
    
    @classmethod
    def from_env(cls) -> "PerformanceConfig":
        """Create config from environment variables."""
        import os
        
        return cls(
            enable_parallel_index=os.getenv("XWDATA_PARALLEL_INDEX", "true").lower() == "true",
            parallel_index_workers=int(os.getenv("XWDATA_PARALLEL_WORKERS", "0")) or None,
            enable_append_log=os.getenv("XWDATA_APPEND_LOG", "true").lower() == "true",
            append_log_compaction_threshold_mb=int(os.getenv("XWDATA_LOG_THRESHOLD_MB", "100")),
            fallback_on_error=os.getenv("XWDATA_FALLBACK", "true").lower() == "true",
        )
    
    @classmethod
    def conservative(cls) -> "PerformanceConfig":
        """Conservative config (disable optimizations, use originals)."""
        return cls(
            enable_parallel_index=False,
            enable_append_log=False,
            fallback_on_error=True,
        )
    
    @classmethod
    def aggressive(cls) -> "PerformanceConfig":
        """Aggressive config (enable all optimizations, no fallback)."""
        return cls(
            enable_parallel_index=True,
            enable_append_log=True,
            fallback_on_error=False,
        )


# Global config instance
_config: PerformanceConfig | None = None


def get_config() -> PerformanceConfig:
    """Get global performance config."""
    global _config
    if _config is None:
        _config = PerformanceConfig.from_env()
    return _config


def set_config(config: PerformanceConfig) -> None:
    """Set global performance config."""
    global _config
    _config = config
