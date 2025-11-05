"""Signal handling for graceful shutdown."""

import signal
import sys
import atexit
from pathlib import Path
from typing import Optional
from multiprocessing import Pool

from checkpoint_manager import CheckpointManager, VerificationResults


class InterruptHandler:
    """Handle interruption signals and cleanup."""

    def __init__(self):
        self.checkpoint_file: Optional[Path] = None
        self.results: Optional[VerificationResults] = None
        self.pool: Optional[Pool] = None

    def setup(
        self,
        checkpoint_file: Optional[Path],
        results: VerificationResults
    ) -> None:
        """Setup signal handlers."""
        self.checkpoint_file = checkpoint_file
        self.results = results

        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
        atexit.register(self._cleanup)

    def set_pool(self, pool: Optional[Pool]) -> None:
        """Set the multiprocessing pool reference."""
        self.pool = pool

    def _signal_handler(self, signum, frame) -> None:
        """Handle interrupt signals."""
        print("\n\nInterrupted! Saving checkpoint before exit...")
        self._save_checkpoint()
        self._terminate_pool()
        sys.exit(130)

    def _cleanup(self) -> None:
        """Cleanup handler for atexit."""
        self._save_checkpoint()

    def _save_checkpoint(self) -> None:
        """Save checkpoint if configured."""
        if self.checkpoint_file and self.results:
            CheckpointManager.save_checkpoint(self.checkpoint_file, self.results)
            print(f"Checkpoint saved to: {self.checkpoint_file}")
            print("You can resume with: --resume -c <checkpoint_file>")

    def _terminate_pool(self) -> None:
        """Terminate multiprocessing pool."""
        if self.pool:
            self.pool.terminate()
            self.pool.join()
