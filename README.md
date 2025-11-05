# CreativeLive Video Integrity Verifier

## Purpose

This tool verifies the integrity of MP4 files downloaded from CreativeLive. It checks that:
- Video files have no encoding errors
- Files are not corrupted or incomplete

Use this after downloading large collections (e.g., 1972 files, 500GB+) where manual verification is impractical.

## How to Run It

### Prerequisites

1. **Python 3.x**
2. **ffmpeg** - Must be installed and in your PATH
   - macOS: `brew install ffmpeg`
   - Linux: `sudo apt install ffmpeg` or `sudo yum install ffmpeg`
   - Windows: Download from https://ffmpeg.org/download.html

### Basic Usage

```bash
# Verify all MP4 files in directory (uses all CPU cores)
python src/main.py /path/to/creativelive/directory

# Save detailed report to file
python src/main.py /path/to/creativelive/directory -o report.txt

# With checkpoint for resume capability
python src/main.py /path/to/creativelive/directory -c checkpoint.json

# Resume after interruption
python src/main.py /path/to/creativelive/directory -c checkpoint.json --resume

# Specify number of parallel workers (default: CPU count)
python src/main.py /path/to/creativelive/directory -j 8

# RECOMMENDED for Mac: Prevent sleep during long verification
caffeinate -i python src/main.py /path/to/creativelive/directory -o report.txt -c checkpoint.json
```

### Command Options

```bash
python src/main.py --help
```

Options:
- `-o, --output` - Save report to file
- `-j, --jobs` - Number of parallel workers (default: CPU count)
- `-c, --checkpoint` - Checkpoint file for resume capability
- `--resume` - Resume from checkpoint file

## What It Checks

The tool performs comprehensive integrity verification:

✓ **Corrupted frames** - Video frames that can't be decoded
✓ **Missing/corrupted headers** - Invalid MP4 container structure (moov atom, etc.)
✓ **Truncated files** - Incomplete downloads that end prematurely
✓ **Codec errors** - Invalid H.264/AAC data streams
✓ **Incomplete data** - Missing video/audio packets
✓ **File structure errors** - Broken MP4 file structure

### What Happens After Verification

- **Valid files**: Can be played without issues
- **Corrupted files**: Should be re-downloaded from CreativeLive
- **Report**: Shows all corrupted files grouped by course with specific error messages

### Example Report

```
================================================================================
VIDEO INTEGRITY VERIFICATION REPORT
================================================================================
Generated: 2025-11-05 14:30:22
Root Directory: /Users/ilya/CreativeLive
Total Files Scanned: 247
Corrupted Files: 3
Valid Files: 244
================================================================================

✗ Found 3 corrupted file(s) in 2 course(s)

--------------------------------------------------------------------------------
COURSE: Photography-Fundamentals
Corrupted files: 2
--------------------------------------------------------------------------------

  File: Photography-Fundamentals/lesson-01.mp4
  Error: [h264 @ 0x7f9d8c000000] concealing 1234 DC, 1234 AC, 1234 MV errors

  File: Photography-Fundamentals/lesson-05.mp4
  Error: moov atom not found

--------------------------------------------------------------------------------
COURSE: Advanced-Lighting
Corrupted files: 1
--------------------------------------------------------------------------------

  File: Advanced-Lighting/module-3/video-02.mp4
  Error: Verification timed out (>5 minutes)

================================================================================
```

## How It Works

### The Verification Process

The tool uses ffmpeg to verify integrity by **fully decoding each file**:

```bash
ffmpeg -v error -i "video.mp4" -f null -
```

**Command breakdown:**
- `-v error` - Only show errors (suppresses normal output)
- `-i "video.mp4"` - Input file to verify
- `-f null` - Output to null (don't write anywhere, just decode)
- `-` - Output to stdout (discarded by null format)

**Why this works:**
- Forces ffmpeg to decode the entire video from start to finish
- Any corruption or incomplete data will trigger errors
- More thorough than just checking file headers or metadata

### Performance

**Parallel Processing:**
- Uses all CPU cores simultaneously (configurable with `-j`)
- Each worker verifies one file at a time
- Results collected and aggregated into final report

**For 1972 files on 8-core machine:**
- Expected time: 2-4 hours (depends on file sizes)
- Speed: 4-8x faster than sequential processing
- Factors: File sizes, CPU cores, disk I/O speed

**Features:**
- Real-time progress tracking with ETA
- Checkpoint every 10 files (auto-saves progress)
- Graceful shutdown on Ctrl+C (saves checkpoint)
- Resume from checkpoint after interruption
- 5-minute timeout per file (prevents hanging on severely corrupted files)

### Exit Codes

- `0` - All files verified successfully
- `1` - One or more corrupted files found or error occurred

### Code Architecture

The codebase follows strict maintainability guidelines (see CLAUDE.md):

```
src/
├── main.py                  # Entry point, orchestrates workflow
├── cli.py                   # Command-line argument parsing
├── video_verifier.py        # ffmpeg verification logic
├── file_scanner.py          # MP4 file discovery
├── checkpoint_manager.py    # State persistence
├── report_generator.py      # Report orchestration
├── report_stats.py          # Statistics calculation
├── report_formatter.py      # Output formatting
├── progress_tracker.py      # Progress display
├── signal_handlers.py       # Interrupt handling
└── verification_runner.py   # Parallel execution
```
# Credits

This tool was vibe coded with Claude.