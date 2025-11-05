"""File scanning utilities."""

from pathlib import Path
from typing import List


class FileScanner:
    """Utilities for scanning and organizing video files."""

    @staticmethod
    def find_mp4_files(root_dir: Path) -> List[Path]:
        """Recursively find all MP4 files in the directory."""
        return sorted(root_dir.rglob('*.mp4'))

    @staticmethod
    def get_course_name(video_path: Path, root_dir: Path) -> str:
        """Extract the course name (first subdirectory) from the video path."""
        try:
            relative = video_path.relative_to(root_dir)
            return relative.parts[0] if len(relative.parts) > 1 else "Root Directory"
        except ValueError:
            return "Unknown"

