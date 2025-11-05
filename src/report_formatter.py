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

    @staticmethod
    def build_removal_commands(files_to_remove: List[Path], json_report_path: Optional[Path]) -> List[str]:
        """Build section with rm commands for non-timeout failures."""
        if not files_to_remove:
            return []

        lines = [
            "=" * 80,
            "RECOMMENDED WORKFLOW FOR FAILED FILES",
            "=" * 80,
            f"Found {len(files_to_remove)} file(s) that failed for reasons other than timeout.",
            "These files are likely corrupted and should be removed and re-downloaded.",
            "",
            "STEP 1: Check files manually (Optional)",
            "Before removing, you can manually verify the corruption by trying to play the files.",
            "Copy and paste the following commands to open each file:",
            ""
        ]

        for file_path in files_to_remove:
            lines.append(f'open "{file_path}"')

        lines.extend([
            "",
            "STEP 2: Remove corrupted files",
            "After confirming corruption, copy and paste the following commands to remove the files:",
            ""
        ])

        for file_path in files_to_remove:
            lines.append(f'rm "{file_path}"')

        lines.extend([
            "",
            "STEP 3: Re-download files",
            "Run your CreativeLive downloader tool to re-download the missing files.",
            ""
        ])

        if json_report_path:
            lines.extend([
                "STEP 4: Re-verify the files",
                "After re-downloading, verify the files again using:",
                "",
                f'python src/main.py --reverify "{json_report_path}" -t 600 -o report-reverify.txt',
                ""
            ])

        lines.extend(["=" * 80, ""])

        return lines

    @staticmethod
    def build_dts_warning_section(dts_files: List[Tuple[Path, str]]) -> List[str]:
        """Build section explaining DTS warnings."""
        if not dts_files:
            return []

        lines = [
            "=" * 80,
            "DTS TIMESTAMP WARNINGS (Usually Playable)",
            "=" * 80,
            f"Found {len(dts_files)} file(s) with timestamp (DTS) warnings.",
            "",
            "⚠️  IMPORTANT: These files have encoding quality issues but usually play fine.",
            "",
            "What this means:",
            "- Files have non-monotonic timestamp issues (technical encoding problem)",
            "- Most video players (QuickTime, VLC, etc.) will play them without issues",
            "- NOT the same as file corruption - data is intact",
            "- Often happens with certain encoders or streaming sources",
            "",
            "Recommendation:",
            "1. Try playing these files - they likely work fine",
            "2. Only re-download if they actually won't play",
            "3. If you want perfect encoding, you can re-download them",
            "",
            "Files with DTS warnings:",
            ""
        ]

        for file_path, _ in dts_files:
            lines.append(f"  - {file_path}")

        lines.extend(["", "=" * 80, ""])

        return lines

