"""Progress tracking and display."""

import time
from typing import Dict


def format_time(seconds: float) -> str:
    """Format seconds into human-readable time."""
    if seconds < 60:
        return f"{seconds:.0f}s"
    elif seconds < 3600:
        return f"{seconds/60:.1f}m"
    else:
        return f"{seconds/3600:.1f}h"


class ProgressTracker:
    """Track and display verification progress."""

    def __init__(self, total_files: int):
        self.total_files = total_files
        self.completed = 0
        self.start_time = time.time()

    def increment(self) -> None:
        """Increment completed count."""
        self.completed += 1

    def display(self) -> None:
        """Display current progress."""
        stats = self.calculate_stats()
        print(self.format_progress(stats), end='\r')

    def calculate_stats(self) -> Dict[str, float]:
        """Calculate current statistics."""
        elapsed = time.time() - self.start_time
        rate = self.completed / elapsed if elapsed > 0 else 0
        remaining = self.total_files - self.completed
        eta = remaining / rate if rate > 0 else 0
        progress = self.completed / self.total_files * 100

        return {
            'progress': progress,
            'rate': rate,
            'eta': eta,
            'elapsed': elapsed
        }

    def format_progress(self, stats: Dict[str, float]) -> str:
        """Format progress string."""
        return (
            f"Progress: {self.completed}/{self.total_files} ({stats['progress']:.1f}%) | "
            f"Rate: {stats['rate']:.1f} files/s | "
            f"ETA: {format_time(stats['eta'])} | "
            f"Elapsed: {format_time(stats['elapsed'])}"
        )

    def display_final(self) -> None:
        """Display final completion message."""
        elapsed = time.time() - self.start_time
        rate = self.total_files / elapsed if elapsed > 0 else 0
        print(f"\n\nVerification complete in {format_time(elapsed)}!")
        print(f"Average rate: {rate:.1f} files/second\n")
