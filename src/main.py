#!/usr/bin/env python3
"""
Main entry point for video integrity verification.
"""

import sys

from cli import CLI
from video_verifier import VideoVerifier
from file_scanner import FileScanner
from checkpoint_manager import CheckpointManager
from report_generator import ReportGenerator
from signal_handlers import InterruptHandler
from verification_runner import VerificationRunner


def main():
    """Main execution flow."""
    args = CLI.parse_arguments()
    paths = CLI.prepare_paths(args)

    validate_prerequisites()

    video_files = scan_for_videos(paths['directory'])
    video_files = filter_already_verified(video_files, paths)

    if not video_files:
        print("No files to verify.")
        return 0

    results = execute_verification(video_files, paths)
    ReportGenerator.generate_report(results, paths['directory'], paths['output'])

    return calculate_exit_code(results)


def validate_prerequisites():
    """Validate system requirements."""
    if not VideoVerifier.check_ffmpeg_available():
        print("Error: ffmpeg is not installed or not in PATH", file=sys.stderr)
        print("Please install ffmpeg: https://ffmpeg.org/download.html", file=sys.stderr)
        sys.exit(1)


def scan_for_videos(directory):
    """Scan directory for MP4 files."""
    print(f"Scanning for MP4 files in: {directory}")
    video_files = FileScanner.find_mp4_files(directory)

    if not video_files:
        print("No MP4 files found in the specified directory")
        sys.exit(0)

    print(f"Found {len(video_files)} MP4 file(s)")
    return video_files


def filter_already_verified(video_files, paths):
    """Filter out already verified files if resuming."""
    if not (paths['resume'] and paths['checkpoint']):
        return video_files

    results = CheckpointManager.load_checkpoint(paths['checkpoint'])
    if results:
        print(f"Resumed from checkpoint: {len(results)} files already verified")
        remaining = [f for f in video_files if f not in results]
        print(f"Remaining files to verify: {len(remaining)}")
        return remaining

    return video_files


def execute_verification(video_files, paths):
    """Execute parallel verification."""
    print(f"Using {paths['jobs']} parallel worker(s)")
    print("Starting parallel verification...\n")

    interrupt_handler = InterruptHandler()
    interrupt_handler.setup(paths['checkpoint'], {})

    return VerificationRunner.run_parallel_verification(
        video_files,
        paths['jobs'],
        paths['checkpoint'],
        interrupt_handler
    )


def calculate_exit_code(results):
    """Calculate exit code based on verification results."""
    corrupted_count = sum(1 for is_valid, _ in results.values() if not is_valid)
    return 0 if corrupted_count == 0 else 1


if __name__ == '__main__':
    sys.exit(main())

