"""Report generation for verification results."""

from pathlib import Path
from typing import Dict, Tuple, Optional

from report_stats import ReportStats
from report_formatter import ReportFormatter


VerificationResults = Dict[Path, Tuple[bool, Optional[str]]]


class ReportGenerator:
    """Orchestrates report generation and output."""

    @staticmethod
    def generate_report(
        results: VerificationResults,
        root_dir: Path,
        output_file: Optional[Path] = None
    ) -> None:
        """Generate and display formatted report of verification results."""
        report = ReportGenerator._build_report(results, root_dir)
        print(report)

        if output_file:
            ReportGenerator._save_report(output_file, report)

    @staticmethod
    def _build_report(results: VerificationResults, root_dir: Path) -> str:
        """Build the report content."""
        corrupted_by_course = ReportStats.group_corrupted_by_course(results, root_dir)
        stats = ReportStats.calculate_stats(results)

        report_lines = []
        report_lines.extend(ReportFormatter.build_header(root_dir, stats))
        report_lines.extend(ReportFormatter.build_summary(stats, corrupted_by_course))
        report_lines.extend(ReportFormatter.build_course_details(corrupted_by_course, root_dir))
        report_lines.append("=" * 80)

        return "\n".join(report_lines)

    @staticmethod
    def _save_report(output_file: Path, report: str) -> None:
        """Save report to file."""
        with open(output_file, 'w') as f:
            f.write(report)
        print(f"\nReport saved to: {output_file}")

