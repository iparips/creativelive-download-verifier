"""Command-line interface argument parsing."""

import argparse
from pathlib import Path
from multiprocessing import cpu_count


class CLI:
    """Command-line interface handler."""

    @staticmethod
    def parse_arguments():
        """Parse command-line arguments."""
        parser = argparse.ArgumentParser(
            description='Verify integrity of MP4 files in CreativeLive directory structure'
        )

        parser.add_argument('directory', nargs='?', help='Path to CreativeLive home directory')
        parser.add_argument('-o', '--output', help='Output file for report', default=None)
        parser.add_argument('-j', '--jobs', type=int, default=cpu_count(),
                           help=f'Number of parallel jobs (default: {cpu_count()})')
        parser.add_argument('-c', '--checkpoint', help='Checkpoint file path', default=None)
        parser.add_argument('--resume', action='store_true',
                           help='Resume from checkpoint file')
        parser.add_argument('-t', '--timeout', type=int, default=300,
                           help='Verification timeout in seconds (default: 300)')
        parser.add_argument('--reverify', help='Re-verify files from report.json', default=None)

        return parser.parse_args()

    @staticmethod
    def validate_directory(directory: str) -> Path:
        """Validate that directory exists and is a directory."""
        path = Path(directory)

        if not path.exists():
            raise ValueError(f"Directory '{directory}' does not exist")

        if not path.is_dir():
            raise ValueError(f"'{directory}' is not a directory")

        return path

    @staticmethod
    def prepare_paths(args):
        """Convert argument strings to Path objects."""
        return {
            'directory': CLI.validate_directory(args.directory) if args.directory else None,
            'output': Path(args.output) if args.output else None,
            'checkpoint': Path(args.checkpoint) if args.checkpoint else None,
            'reverify': Path(args.reverify) if args.reverify else None,
            'jobs': args.jobs,
            'resume': args.resume,
            'timeout': args.timeout
        }

