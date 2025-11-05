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
from json_report_generator import JsonReportGenerator
from signal_handlers import InterruptHandler
from verification_runner import VerificationRunner


def main():
    """Main execution flow."""
    args = CLI.parse_arguments()
    paths = CLI.prepare_paths(args)

    validate_prerequisites()

    if paths['reverify']:
        video_files = load_files_from_json(paths['reverify'])
        root_dir = determine_root_directory(video_files)
    else:
        if not paths['directory']:
            print("Error: directory argument is required when not using --reverify")
            return 1
        root_dir = paths['directory']
        video_files = scan_for_videos(root_dir)
        video_files = filter_already_verified(video_files, paths)

    if not video_files:
        print("No files to verify.")
        return 0

    results = execute_verification(video_files, paths)
    ReportGenerator.generate_report(results, root_dir, paths['output'])

    return calculate_exit_code(results)


def load_files_from_json(json_file):
    """Load file paths from JSON report."""
    print(f"Loading files from JSON report: {json_file}")
    files = JsonReportGenerator.load_corrupted_files_from_json(json_file)
    print(f"Loaded {len(files)} file(s) to re-verify")
    return files


def determine_root_directory(video_files):
    """Determine root directory from video files."""
    if not video_files:
        return None

    first_file = video_files[0]
    return first_file.parent.parent if len(first_file.parts) > 1 else first_file.parent


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
    actual_workers = min(paths['jobs'], len(video_files))
    print(f"Using {actual_workers} parallel worker(s)")
    print(f"Verification timeout: {paths['timeout']} seconds")
    print("Starting parallel verification...\n")

    interrupt_handler = InterruptHandler()
    interrupt_handler.setup(paths['checkpoint'], {})

    return VerificationRunner.run_parallel_verification(
        video_files,
        paths['jobs'],
        paths['checkpoint'],
        interrupt_handler,
        paths['timeout']
    )


def calculate_exit_code(results):
    """Calculate exit code based on verification results."""
    corrupted_count = sum(1 for is_valid, _, __ in results.values() if not is_valid)
    return 0 if corrupted_count == 0 else 1


if __name__ == '__main__':
    sys.exit(main())

