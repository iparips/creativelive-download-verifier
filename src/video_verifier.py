"""Video verification using ffmpeg."""

import subprocess
from pathlib import Path
from typing import Tuple, Optional


class VideoVerifier:
    """Handles video file verification using ffmpeg."""

    @staticmethod
    def verify_video(video_path: Path) -> Tuple[Path, bool, Optional[str]]:
        """
        Verify a single video file using ffmpeg.

        Returns:
            Tuple of (video_path, is_valid, error_message)
        """
        try:
            result = VideoVerifier._run_ffmpeg_verification(video_path)
            return VideoVerifier._parse_verification_result(video_path, result)
        except subprocess.TimeoutExpired:
            return (video_path, False, "Verification timed out (>5 minutes)")
        except FileNotFoundError:
            return (video_path, False, "ffmpeg not found - please install ffmpeg")
        except Exception as e:
            return (video_path, False, f"Unexpected error: {str(e)}")

    @staticmethod
    def _run_ffmpeg_verification(video_path: Path) -> subprocess.CompletedProcess:
        """Run ffmpeg verification command."""
        return subprocess.run(
            ['ffmpeg', '-v', 'error', '-i', str(video_path), '-f', 'null', '-'],
            capture_output=True,
            text=True,
            timeout=300
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

