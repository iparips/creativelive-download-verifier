"""Report generation for verification results."""

from pathlib import Path
from typing import Dict, Tuple, Optional

from report_stats import ReportStats
from report_formatter import ReportFormatter
from json_report_generator import JsonReportGenerator


VerificationResults = Dict[Path, Tuple[bool, Optional[str], int]]


class ReportGenerator:
    """Orchestrates report generation and output."""

    @staticmethod
    def generate_report(
        results: VerificationResults,
        root_dir: Path,
        output_file: Optional[Path] = None
    ) -> None:
        """Generate and display formatted report of verification results."""
        json_report_path = output_file.with_suffix('.json') if output_file else None
        report = ReportGenerator._build_report(results, root_dir, json_report_path)
        print(report)

        if output_file:
            ReportGenerator._save_report(output_file, report)
            ReportGenerator._save_json_report(output_file, results, root_dir)

    @staticmethod
    def _build_report(
        results: VerificationResults,
        root_dir: Path,
        json_report_path: Optional[Path] = None
    ) -> str:
        """Build the report content."""
        corrupted_by_course = ReportStats.group_corrupted_by_course(results, root_dir)
        stats = ReportStats.calculate_stats(results)
        error_categories = ReportStats.categorize_errors(results)

        # Only show removal workflow for severe corruption, not DTS warnings
        severe_failures = [path for path, _ in error_categories['severe_corruption']]

        report_lines = []
        report_lines.extend(ReportFormatter.build_header(root_dir, stats))
        report_lines.extend(ReportFormatter.build_summary(stats, corrupted_by_course))
        report_lines.extend(ReportFormatter.build_course_details(corrupted_by_course, root_dir))
        report_lines.append("=" * 80)

        # Add DTS warning section first (usually playable)
        report_lines.extend(ReportFormatter.build_dts_warning_section(error_categories['dts_warnings']))

        # Add removal commands only for severe corruption
        report_lines.extend(ReportFormatter.build_removal_commands(severe_failures, json_report_path))

        return "\n".join(report_lines)

    @staticmethod
    def _save_report(output_file: Path, report: str) -> None:
        """Save report to file."""
        with open(output_file, 'w') as f:
            f.write(report)
        print(f"\nReport saved to: {output_file}")

    @staticmethod
    def _save_json_report(
        output_file: Path,
        results: VerificationResults,
        root_dir: Path
    ) -> None:
        """Save JSON report alongside text report."""
        json_output = output_file.with_suffix('.json')
        JsonReportGenerator.generate_json_report(results, root_dir, json_output)

