"""Progress indicator with spinning animation and percentage.
Company: eXonware.com
Author: eXonware Backend Team
Email: connect@exonware.com
Version: 0.0.1.0
Generation Date: 2025-01-XX
"""

import sys
import threading
import time
from typing import Optional
# Disable buffering for stderr to ensure real-time updates
if hasattr(sys.stderr, 'reconfigure'):
    try:
        sys.stderr.reconfigure(line_buffering=True)
    except:
        pass


class ProgressIndicator:
    """
    Progress indicator with spinning animation and percentage.
    Features:
    - Spinning animation: | / - \
    - Percentage display
    - Custom message
    - Thread-safe
    - Context manager support
    """
    SPINNER_FRAMES = ['|', '/', '-', '\\']

    def __init__(self, message: str = "Processing...", total: Optional[int] = None):
        """
        Initialize progress indicator.
        Args:
            message: Message to display
            total: Total items (for percentage calculation)
        """
        self.message = message
        self.total = total
        self.current = 0
        self._running = False
        self._thread: Optional[threading.Thread] = None
        self._frame_index = 0
        self._lock = threading.Lock()
        self._last_update = time.time()

    def start(self) -> 'ProgressIndicator':
        """Start the progress indicator."""
        with self._lock:
            if not self._running:
                self._running = True
                self._thread = threading.Thread(target=self._animate, daemon=True)
                self._thread.start()
        return self

    def stop(self):
        """Stop the progress indicator."""
        with self._lock:
            if self._running:
                self._running = False
                if self._thread:
                    self._thread.join(timeout=0.5)
                # Clear line (overwrite with spaces then return to start)
                clear_line = '\r' + ' ' * 100 + '\r'
                try:
                    sys.stderr.buffer.write(clear_line.encode('utf-8', errors='replace'))
                    sys.stderr.buffer.flush()
                except:
                    try:
                        sys.stderr.write(clear_line)
                        sys.stderr.flush()
                    except:
                        try:
                            sys.stdout.write(clear_line)
                            sys.stdout.flush()
                        except:
                            pass

    def update(self, current: int, total: Optional[int] = None):
        """
        Update progress.
        Args:
            current: Current progress value
            total: Total value (if different from initial)
        """
        with self._lock:
            self.current = current
            if total is not None:
                self.total = total
            self._last_update = time.time()

    def _animate(self):
        """Animation loop."""
        last_percentage = -1
        while self._running:
            with self._lock:
                if not self._running:
                    break
                # Calculate percentage
                if self.total and self.total > 0:
                    percentage = min(100.0, (self.current / self.total) * 100.0)
                    percentage_str = f"{percentage:.2f}%"
                else:
                    percentage_str = "---"
                    percentage = 0
                # Only update display if percentage changed (reduces output when piped)
                # Always show first update (percentage == 0) and when percentage changes
                if int(percentage) != int(last_percentage) or (last_percentage == -1 and percentage == 0):
                    # Get spinner frame
                    spinner = self.SPINNER_FRAMES[self._frame_index]
                    self._frame_index = (self._frame_index + 1) % len(self.SPINNER_FRAMES)
                    # Format message - use \r to overwrite same line
                    # Pad with spaces to clear any remaining characters from previous updates
                    line = f"\r{self.message} {percentage_str} {spinner}"
                    # Pad to 120 chars to ensure we clear the line completely
                    line_padded = (line + ' ' * 120)[:120]
                    try:
                        # Write directly to terminal (unbuffered)
                        # Use stderr which is typically unbuffered and works better when piped
                        sys.stderr.write(line_padded)
                        sys.stderr.flush()
                    except (UnicodeEncodeError, OSError):
                        # Fallback to stdout
                        try:
                            sys.stdout.write(line_padded)
                            sys.stdout.flush()
                        except:
                            pass  # Ignore if both fail
                    last_percentage = percentage
                else:
                    # Still advance spinner even if percentage hasn't changed
                    self._frame_index = (self._frame_index + 1) % len(self.SPINNER_FRAMES)
            time.sleep(0.1)  # Update every 100ms

    def __enter__(self):
        """Context manager entry."""
        self.start()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.stop()
        return False


def show_progress(message: str, total: Optional[int] = None):
    """
    Context manager for progress indicator.
    Usage:
        with show_progress("Converting...", total=1000):
            for i in range(1000):
                # do work
                progress.update(i + 1)
    """
    return ProgressIndicator(message, total)
