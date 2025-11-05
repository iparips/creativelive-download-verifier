"""JSON report generation for verification results."""

import json
from pathlib import Path
from typing import Dict, Tuple, Optional
from datetime import datetime


VerificationResults = Dict[Path, Tuple[bool, Optional[str], int]]


class JsonReportGenerator:
    """Generates JSON reports from verification results."""

    @staticmethod
    def generate_json_report(
        results: VerificationResults,
        root_dir: Path,
        output_file: Path
    ) -> None:
        """Generate and save JSON report."""
        report_data = JsonReportGenerator._build_json_data(results, root_dir)
        JsonReportGenerator._save_json_report(output_file, report_data)
        print(f"JSON report saved to: {output_file}")

    @staticmethod
    def _build_json_data(
        results: VerificationResults,
        root_dir: Path
    ) -> Dict:
        """Build JSON report data structure (only failed files)."""
        files = []
        total_size = 0
        corrupted_count = 0
        total_files = len(results)

        for video_path, (is_valid, error_msg, file_size) in results.items():
            total_size += file_size
            if not is_valid:
                corrupted_count += 1
                files.append({
                    'path': str(video_path),
                    'relative_path': str(JsonReportGenerator._get_relative_path(video_path, root_dir)),
                    'size': file_size,
                    'is_valid': is_valid,
                    'error': error_msg
                })

        return {
            'metadata': {
                'generated': datetime.now().isoformat(),
                'root_directory': str(root_dir),
                'total_files': total_files,
                'corrupted_files': corrupted_count,
                'valid_files': total_files - corrupted_count,
                'total_size': total_size
            },
            'files': sorted(files, key=lambda x: x['path'])
        }

    @staticmethod
    def _get_relative_path(video_path: Path, root_dir: Path) -> Path:
        """Get path relative to root, or return original if not possible."""
        try:
            return video_path.relative_to(root_dir)
        except ValueError:
            return video_path

    @staticmethod
    def _save_json_report(output_file: Path, report_data: Dict) -> None:
        """Save JSON report to file."""
        with open(output_file, 'w') as f:
            json.dump(report_data, f, indent=2)

    @staticmethod
    def load_files_from_json(json_file: Path) -> list[Path]:
        """Load file paths from JSON report."""
        with open(json_file, 'r') as f:
            data = json.load(f)

        return [Path(file_info['path']) for file_info in data['files']]

    @staticmethod
    def load_corrupted_files_from_json(json_file: Path) -> list[Path]:
        """Load only corrupted file paths from JSON report."""
        with open(json_file, 'r') as f:
            data = json.load(f)

        return [
            Path(file_info['path'])
            for file_info in data['files']
            if not file_info['is_valid']
        ]
