"""Parallel verification execution."""

from pathlib import Path
from typing import List
from multiprocessing import Pool

from video_verifier import VideoVerifier
from checkpoint_manager import CheckpointManager, VerificationResults
from progress_tracker import ProgressTracker


class VerificationRunner:
    """Manages parallel execution of video verification."""

    @staticmethod
    def run_parallel_verification(
        video_files: List[Path],
        num_workers: int,
        checkpoint_file: Path,
        interrupt_handler
    ) -> VerificationResults:
        """Run parallel verification of video files."""
        tracker = ProgressTracker(len(video_files))
        results = {}

        with Pool(processes=num_workers) as pool:
            interrupt_handler.set_pool(pool)
            results = VerificationRunner._process_videos(
                pool, video_files, tracker, checkpoint_file, interrupt_handler
            )
            interrupt_handler.set_pool(None)

        VerificationRunner._save_final_checkpoint(checkpoint_file, results)
        tracker.display_final()

        return results

    @staticmethod
    def _process_videos(
        pool: Pool,
        video_files: List[Path],
        tracker: ProgressTracker,
        checkpoint_file: Path,
        interrupt_handler
    ) -> VerificationResults:
        """Process all videos and track progress."""
        results = {}

        for video_path, is_valid, error_msg in pool.imap_unordered(
            VideoVerifier.verify_video, video_files
        ):
            results[video_path] = (is_valid, error_msg)
            interrupt_handler.results = results

            tracker.increment()
            tracker.display()

            VerificationRunner._save_periodic_checkpoint(
                checkpoint_file, results, tracker.completed
            )

        return results

    @staticmethod
    def _save_periodic_checkpoint(
        checkpoint_file: Path,
        results: VerificationResults,
        completed: int
    ) -> None:
        """Save checkpoint every 10 files."""
        if checkpoint_file and completed % 10 == 0:
            CheckpointManager.save_checkpoint(checkpoint_file, results)

    @staticmethod
    def _save_final_checkpoint(checkpoint_file: Path, results: VerificationResults) -> None:
        """Save final checkpoint."""
        if checkpoint_file:
            CheckpointManager.save_checkpoint(checkpoint_file, results)

