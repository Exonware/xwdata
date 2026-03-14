#!/usr/bin/env python3
"""
#exonware/xwdata/src/exonware/xwdata/common/monitoring/metrics.py
Metrics Collection
Integration with xwsystem monitoring for performance metrics.
Company: eXonware.com
Author: eXonware Backend Team
Email: connect@exonware.com
Version: 0.9.0.3
Generation Date: 26-Oct-2025
"""

from typing import Any
from exonware.xwsystem.monitoring import create_component_metrics
# Create metrics for xwdata
_xwdata_metrics = create_component_metrics('xwdata')


def get_metrics() -> dict[str, Any]:
    """Get xwdata metrics."""
    return _xwdata_metrics


def reset_metrics() -> None:
    """Reset xwdata metrics."""
    if 'reset' in _xwdata_metrics:
        _xwdata_metrics['reset']()
__all__ = ['get_metrics', 'reset_metrics']
