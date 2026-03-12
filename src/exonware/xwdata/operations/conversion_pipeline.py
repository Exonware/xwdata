#!/usr/bin/env python3
"""
#exonware/xwdata/src/exonware/xwdata/operations/conversion_pipeline.py
Conversion Pipeline (Optional BaaS Feature)
Provides multi-step conversion pipelines for complex conversion workflows.
Company: eXonware.com
Author: eXonware Backend Team
Email: connect@exonware.com
Version: 0.9.0.1
Generation Date: 26-Jan-2025
"""

from typing import Any, Optional
from pathlib import Path
from exonware.xwsystem import get_logger
from ..contracts import IConversionPipeline, IFormatConverter
from ..defs import DataFormat
from ..errors import XWDataError
from .format_conversion import FormatConverter
logger = get_logger(__name__)


class ConversionPipeline(IConversionPipeline):
    """
    Multi-step conversion pipeline.
    Provides support for complex conversion workflows with multiple steps.
    This is an optional BaaS feature.
    """

    def __init__(self, converter: Optional[IFormatConverter] = None):
        """
        Initialize conversion pipeline.
        Args:
            converter: Optional format converter (creates default if not provided)
        """
        self._converter = converter or FormatConverter()

    async def execute(
        self,
        data: Any,
        steps: list[tuple[str | DataFormat, dict[str, Any]]],
        **opts
    ) -> Any:
        """
        Execute multi-step conversion pipeline.
        Args:
            data: Initial data
            steps: List of (format, options) tuples for each step
            **opts: Global pipeline options
        Returns:
            Final converted data
        """
        if not steps:
            raise XWDataError("Conversion pipeline requires at least one step")
        current_data = data
        current_format = None
        for i, (format, step_opts) in enumerate(steps):
            # Merge global options with step-specific options
            merged_opts = {**opts, **step_opts}
            if i == 0:
                # First step: convert from initial data to first format
                # If data is already in native format, we need to know the source format
                # For now, assume it's already in the target format if it's a dict/list
                if isinstance(current_data, (dict, list)):
                    # Data is already native, just serialize to first format
                    from exonware.xwsystem.io.serialization.registry import get_serialization_registry
                    registry = get_serialization_registry()
                    serializer = registry.get_by_format(self._normalize_format(format))
                    if serializer:
                        current_data = serializer.dumps(current_data, **merged_opts)
                        current_format = format
                    else:
                        raise XWDataError(f"Serializer not found for format: {format}")
                else:
                    # Data is already serialized, assume it's in the first format
                    current_format = format
            else:
                # Subsequent steps: convert from previous format to current format
                if not current_format:
                    raise XWDataError("Cannot determine source format for conversion step")
                current_data = await self._converter.convert(
                    current_data,
                    current_format,
                    format,
                    **merged_opts
                )
                current_format = format
            logger.debug(f"Pipeline step {i+1}/{len(steps)}: converted to {format}")
        return current_data

    async def execute_file(
        self,
        source_path: str | Path,
        steps: list[tuple[str | DataFormat, dict[str, Any]]],
        target_path: Optional[str | Path] = None,
        **opts
    ) -> Path:
        """
        Execute multi-step conversion pipeline on file.
        Args:
            source_path: Source file path
            steps: List of (format, options) tuples for each step
            target_path: Optional target path (auto-generated if not provided)
            **opts: Global pipeline options
        Returns:
            Path to final converted file
        """
        source_path_obj = Path(source_path)
        if not source_path_obj.exists():
            raise XWDataError(f"Source file not found: {source_path_obj}")
        # Generate target path if not provided
        if target_path:
            target_path_obj = Path(target_path)
        else:
            # Use last format in pipeline for extension
            last_format = steps[-1][0]
            target_path_obj = source_path_obj.with_suffix(f'.{self._normalize_format(last_format)}')
        # Read source file
        source_format = source_path_obj.suffix.lstrip('.').lower()
        if source_path_obj.suffix.lower() in ['.json', '.yaml', '.yml', '.toml', '.xml', '.csv']:
            data = source_path_obj.read_text(encoding='utf-8')
        else:
            data = source_path_obj.read_bytes()
        # Execute pipeline
        # Prepend source format as first step if not already in steps
        if not steps or self._normalize_format(steps[0][0]) != source_format:
            steps = [(source_format, {})] + steps
        result = await self.execute(data, steps, **opts)
        # Write result
        if isinstance(result, bytes):
            target_path_obj.write_bytes(result)
        else:
            target_path_obj.write_text(result, encoding='utf-8')
        logger.debug(f"Pipeline executed: {source_path_obj} → {target_path_obj}")
        return target_path_obj

    def _normalize_format(self, format: str | DataFormat) -> str:
        """Normalize format name to lowercase string."""
        if isinstance(format, DataFormat):
            return format.name.lower()
        return str(format).lower()
__all__ = ['ConversionPipeline']
