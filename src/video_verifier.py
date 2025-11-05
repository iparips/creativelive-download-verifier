"""Video verification using ffmpeg."""

import subprocess
from pathlib import Path
from typing import Tuple, Optional


class VideoVerifier:
    """Handles video file verification using ffmpeg."""

    @staticmethod
    def verify_video(video_path: Path, timeout: int = 300) -> Tuple[Path, bool, Optional[str], int]:
        """
        Verify a single video file using ffmpeg.

        Args:
            video_path: Path to the video file
            timeout: Verification timeout in seconds (default: 300)

        Returns:
            Tuple of (video_path, is_valid, error_message, file_size)
        """
        if not video_path.exists():
            return (video_path, False, "File does not exist", 0)

        file_size = video_path.stat().st_size

        try:
            result = VideoVerifier._run_ffmpeg_verification(video_path, timeout)
            path, is_valid, error = VideoVerifier._parse_verification_result(video_path, result)
            return (path, is_valid, error, file_size)
        except subprocess.TimeoutExpired:
            timeout_msg = f"Verification timed out (>{timeout} seconds)"
            return (video_path, False, timeout_msg, file_size)
        except FileNotFoundError:
            return (video_path, False, "ffmpeg not found - please install ffmpeg", file_size)
        except Exception as e:
            return (video_path, False, f"Unexpected error: {str(e)}", file_size)

    @staticmethod
    def _run_ffmpeg_verification(video_path: Path, timeout: int) -> subprocess.CompletedProcess:
        """Run ffmpeg verification command."""
        return subprocess.run(
            ['ffmpeg', '-v', 'error', '-i', str(video_path), '-f', 'null', '-'],
            capture_output=True,
            text=True,
            timeout=timeout
        )

    @staticmethod
    def _parse_verification_result(
        video_path: Path,
        result: subprocess.CompletedProcess
    ) -> Tuple[Path, bool, Optional[str]]:
        """Parse ffmpeg result to determine if video is valid."""
        if result.stderr.strip():
            return (video_path, False, result.stderr.strip())
        return (video_path, True, None)

    @staticmethod
    def check_ffmpeg_available() -> bool:
        """Check if ffmpeg is installed and available."""
        try:
            subprocess.run(['ffmpeg', '-version'], capture_output=True, check=True)
            return True
        except (subprocess.CalledProcessError, FileNotFoundError):
            return False

