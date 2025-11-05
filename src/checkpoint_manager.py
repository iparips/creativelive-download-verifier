"""Checkpoint save and load functionality."""

import json
from pathlib import Path
from typing import Dict, Tuple, Optional


VerificationResults = Dict[Path, Tuple[bool, Optional[str]]]


class CheckpointManager:
    """Manages checkpoint persistence for verification state."""

    @staticmethod
    def save_checkpoint(checkpoint_file: Path, results: VerificationResults) -> None:
        """Save current results to checkpoint file."""
        checkpoint_data = {
            str(path): (is_valid, error_msg)
            for path, (is_valid, error_msg) in results.items()
        }
        with open(checkpoint_file, 'w') as f:
            json.dump(checkpoint_data, f)

    @staticmethod
    def load_checkpoint(checkpoint_file: Path) -> VerificationResults:
        """Load results from checkpoint file."""
        if not checkpoint_file.exists():
            return {}

        with open(checkpoint_file, 'r') as f:
            checkpoint_data = json.load(f)

        return {
            Path(path): (is_valid, error_msg)
            for path, (is_valid, error_msg) in checkpoint_data.items()
        }

