"""Report statistics and data processing."""

from pathlib import Path
from typing import Dict, Tuple, Optional, List
from collections import defaultdict

from file_scanner import FileScanner


VerificationResults = Dict[Path, Tuple[bool, Optional[str], int]]


class ReportStats:
    """Handles statistical calculations for reports."""

    @staticmethod
    def group_corrupted_by_course(
        results: VerificationResults,
        root_dir: Path
    ) -> Dict[str, List[Tuple[Path, str]]]:
        """Group corrupted files by course."""
        corrupted_by_course = defaultdict(list)
        for video_path, (is_valid, error_msg, _) in results.items():
            if not is_valid:
                course = FileScanner.get_course_name(video_path, root_dir)
                corrupted_by_course[course].append((video_path, error_msg))

        return corrupted_by_course

    @staticmethod
    def calculate_stats(results: VerificationResults) -> Dict[str, int]:
        """Calculate verification statistics."""
        total = len(results)
        corrupted = sum(1 for is_valid, _, __ in results.values() if not is_valid)
        return {
            'total': total,
            'corrupted': corrupted,
            'valid': total - corrupted
        }

    @staticmethod
    def get_relative_path(video_path: Path, root_dir: Path) -> Path:
        """Get path relative to root, or return original if not possible."""
        try:
            return video_path.relative_to(root_dir)
        except ValueError:
            return video_path

    @staticmethod
    def get_non_timeout_failures(results: VerificationResults) -> List[Path]:
        """Get files that failed for reasons other than timeout."""
        non_timeout_failures = []
        for video_path, (is_valid, error_msg, _) in results.items():
            if not is_valid and error_msg:
                is_timeout = "timed out" in error_msg.lower() or "timeout" in error_msg.lower()
                if not is_timeout:
                    non_timeout_failures.append(video_path)
        return sorted(non_timeout_failures)

    @staticmethod
    def categorize_errors(results: VerificationResults) -> Dict[str, List[Tuple[Path, str]]]:
        """Categorize errors by type."""
        categories = {
            'dts_warnings': [],
            'severe_corruption': [],
            'timeout': []
        }

        for video_path, (is_valid, error_msg, _) in results.items():
            if not is_valid and error_msg:
                error_lower = error_msg.lower()
                if "timed out" in error_lower or "timeout" in error_lower:
                    categories['timeout'].append((video_path, error_msg))
                elif "non monotonically increasing dts" in error_lower:
                    categories['dts_warnings'].append((video_path, error_msg))
                else:
                    categories['severe_corruption'].append((video_path, error_msg))

        return categories

