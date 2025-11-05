"""Checkpoint save and load functionality."""

import json
from pathlib import Path
from typing import Dict, Tuple, Optional


VerificationResults = Dict[Path, Tuple[bool, Optional[str], int]]


class CheckpointManager:
    """Manages checkpoint persistence for verification state."""

    @staticmethod
    def save_checkpoint(checkpoint_file: Path, results: VerificationResults) -> None:
        """Save current results to checkpoint file."""
        checkpoint_data = {
            str(path): (is_valid, error_msg, file_size)
            for path, (is_valid, error_msg, file_size) in results.items()
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

        # Handle both old format (2-tuple) and new format (3-tuple)
        result = {}
        for path, data in checkpoint_data.items():
            if len(data) == 2:
                # Old format: (is_valid, error_msg)
                is_valid, error_msg = data
                file_size = 0  # Default size for old checkpoints
            else:
                # New format: (is_valid, error_msg, file_size)
                is_valid, error_msg, file_size = data

            result[Path(path)] = (is_valid, error_msg, file_size)

        return result

