# MP4 Video Library Integrity Verifier

## Purpose

This tool verifies the integrity of MP4 files. For example, ones downloaded using CreativeLive downloader tool. It checks that:
- Video files have no encoding errors
- Files are not corrupted or incomplete

Use this after downloading large collections (e.g., 1972 files, 500GB+) where manual verification is impractical.

The way I use this tool is
1. Download my courses from CreativeLive using their downloader tool
2. Run this verification script over the downloaded CreativeLive directory
3. Re-verify timed out files from report.json using a larger timeout
4. Remove files that failed re-verification and re-start CreativeLive downloader to re-download them
5. Re-verify those files using report.json as input again

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

# Save detailed report to file (creates both .txt and .json)
python src/main.py /path/to/creativelive/directory -o report.txt

# With checkpoint for resume capability
python src/main.py /path/to/creativelive/directory -c checkpoint.json

# Resume after interruption
python src/main.py /path/to/creativelive/directory -c checkpoint.json --resume

# Specify number of parallel workers (default: CPU count)
python src/main.py /path/to/creativelive/directory -j 8

# Custom timeout per file (default: 300 seconds)
python src/main.py /path/to/creativelive/directory -t 600 -o report.txt

# Re-verify only corrupted files from previous report with longer timeout 
# mp4 files larger than 600Mb may need a larger timeout to verify
python src/main.py --reverify report.json -t 1200 -o report-retry.txt

# RECOMMENDED for Mac: Prevent sleep during long verification
caffeinate -i python src/main.py /path/to/creativelive/directory -o report.txt -c checkpoint.json
```

### Command Options

```bash
python src/main.py --help
```

Options:
- `-o, --output` - Save report to file (generates both .txt and .json)
- `-j, --jobs` - Number of parallel workers (default: CPU count)
- `-c, --checkpoint` - Checkpoint file for resume capability
- `--resume` - Resume from checkpoint file
- `-t, --timeout` - Verification timeout in seconds per file (default: 300)
- `--reverify` - Re-verify files from a previous report.json

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
- **JSON Report**: When using `-o`, both `.txt` and `.json` reports are generated
  - JSON includes file paths, sizes, validation status, and errors
  - Useful for automation and re-verification workflows

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
- Configurable timeout per file (default: 5 minutes)
- JSON report output with file metadata (paths, sizes, errors)
- Re-verification mode to retry only corrupted files with different timeout

### Re-verification Workflow

For files that timed out during initial verification, you can re-verify them with a longer timeout:

```bash
# Initial verification with standard 5-minute timeout
python src/main.py /path/to/videos -o report.txt

# This creates report.txt and report.json
# If some files timed out, re-verify only those with 20-minute timeout
python src/main.py --reverify report.json -t 1200 -o report-retry.txt

# This will:
# 1. Load only corrupted files from report.json
# 2. Verify them with the new 1200-second (20-minute) timeout
# 3. Generate new report-retry.txt and report-retry.json
```

**Use cases:**
- Very large video files that need more processing time
- Files with complex encoding that take longer to verify
- Network-mounted drives with slower I/O
- Distinguishing between truly corrupted files and slow-to-process files

### Exit Codes

- `0` - All files verified successfully
- `1` - One or more corrupted files found or error occurred

### Code Architecture

The codebase follows strict maintainability guidelines (see CLAUDE.md):

```
src/
├── main.py                   # Entry point, orchestrates workflow
├── cli.py                    # Command-line argument parsing
├── video_verifier.py         # ffmpeg verification logic
├── file_scanner.py           # MP4 file discovery
├── checkpoint_manager.py     # State persistence
├── report_generator.py       # Report orchestration
├── json_report_generator.py  # JSON report generation and loading
├── report_stats.py           # Statistics calculation
├── report_formatter.py       # Output formatting
├── progress_tracker.py       # Progress display
├── signal_handlers.py        # Interrupt handling
└── verification_runner.py    # Parallel execution
```
# Credits

This tool was vibe coded with Claude.