"""Report formatting and output."""

from pathlib import Path
from typing import Dict, List, Tuple, Optional
from datetime import datetime

from report_stats import ReportStats


class ReportFormatter:
    """Handles report formatting and text generation."""

    @staticmethod
    def build_header(root_dir: Path, stats: Dict[str, int]) -> List[str]:
        """Build report header."""
        return [
            "=" * 80,
            "VIDEO INTEGRITY VERIFICATION REPORT",
            "=" * 80,
            f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            f"Root Directory: {root_dir}",
            f"Total Files Scanned: {stats['total']}",
            f"Corrupted Files: {stats['corrupted']}",
            f"Valid Files: {stats['valid']}",
            "=" * 80,
            ""
        ]

    @staticmethod
    def build_summary(
        stats: Dict[str, int],
        corrupted_by_course: Dict[str, List[Tuple[Path, str]]]
    ) -> List[str]:
        """Build summary section."""
        if stats['corrupted'] == 0:
            return ["✓ All video files passed integrity verification!", ""]

        return [
            f"✗ Found {stats['corrupted']} corrupted file(s) in {len(corrupted_by_course)} course(s)",
            ""
        ]

    @staticmethod
    def build_course_details(
        corrupted_by_course: Dict[str, List[Tuple[Path, str]]],
        root_dir: Path
    ) -> List[str]:
        """Build detailed course breakdown."""
        lines = []
        for course in sorted(corrupted_by_course.keys()):
            files = corrupted_by_course[course]
            lines.extend(ReportFormatter._build_course_section(course, files, root_dir))
        return lines

    @staticmethod
    def _build_course_section(
        course: str,
        files: List[Tuple[Path, str]],
        root_dir: Path
    ) -> List[str]:
        """Build section for a single course."""
        lines = [
            "-" * 80,
            f"COURSE: {course}",
            f"Corrupted files: {len(files)}",
            "-" * 80
        ]

        for video_path, error_msg in files:
            rel_path = ReportStats.get_relative_path(video_path, root_dir)
            lines.extend([
                f"\n  File: {rel_path}",
                f"  Error: {error_msg}"
            ])

        lines.append("")
        return lines

