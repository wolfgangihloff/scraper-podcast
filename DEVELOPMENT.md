# Development Guide for Cursor

This guide complements the existing `CLAUDE.md` and `README.md` files with Cursor-specific development information.

## Quick Start for Cursor Development

### 1. Environment Setup
```bash
# Ensure virtual environment is active
source .venv/bin/activate

# Install dependencies (already done)
pip install -r requirements.txt

# Verify installation
python -c "import feedparser, requests, bs4, dotenv; print('All dependencies OK')"
```

### 2. Authentication Setup
The project uses a `.env` file for StackIT API authentication. Since `.env.template` may be blocked by gitignore, here's the template content:

```bash
# Copy to .env and fill in your credentials
STACKIT_ACCESS_TOKEN=your_actual_access_token_here
```

### 3. Testing the Setup

**Test scrapers:**
```bash
python scraper_politica_exterior.py    # Downloads latest Spanish podcast
python scraper_egovpodcast.py          # Downloads German podcast episodes
```

**Test transcription:**
```bash
python transcribe.py --list             # Show available files
python transcribe.py --file test        # Transcribe a specific file
```

**Full pipeline:**
```bash
python run_pipeline.py                  # Complete download + transcription
```

## Project Architecture

### Core Components

1. **Web Scrapers**
   - `scraper_politica_exterior.py` - Regex-based HTML parsing for Spanish podcasts
   - `scraper_egovpodcast.py` - Comprehensive German podcast downloader (220+ episodes)

2. **Transcription Service**
   - `transcribe.py` - StackIT AI Assistant API integration
   - Supports multiple authentication methods
   - Handles large files with timeout management

3. **Pipeline Orchestration**
   - `run_pipeline.py` - Automated workflow execution
   - Error handling and progress reporting

### File Organization
```
├── downloads/              # Política Exterior audio files
├── downloads_egov/        # eGovernment podcast audio files  
├── transcriptions/        # Transcripts from downloads/ 
├── transcriptions_egov/   # Transcripts from downloads_egov/
├── .env                   # API credentials (DO NOT commit)
└── .claude/              # Claude-specific configuration
```

## Current Status

✅ **Working Features:**
- Web scraping with multiple regex patterns
- Audio file downloading with resume capability
- StackIT API transcription with proper authentication
- 220 audio files available (mix of .m4a and .mp4 formats)
- Comprehensive error handling

✅ **Tested Components:**
- Virtual environment setup
- Dependency installation  
- Core module imports
- Pipeline execution
- File status tracking

## Development Tips for Cursor

### Debugging Commands
```bash
# List all available files with transcription status
python transcribe.py --list

# Check specific file details
ls -la downloads/ downloads_egov/

# Test API connectivity (requires .env setup)
python -c "from transcribe import main; print('API test')"
```

### Code Patterns
- **URL Extraction**: Multiple regex patterns for different hosting services
- **Error Handling**: Comprehensive try/except blocks with user-friendly messages
- **Progress Tracking**: Clear status updates for long-running operations
- **File Management**: Automatic directory creation and duplicate handling

### Common Issues & Solutions

1. **Authentication Errors**: Verify `.env` file exists and contains valid StackIT token
2. **Import Errors**: Ensure virtual environment is activated
3. **Download Failures**: Check network connectivity and URL validity
4. **Transcription Timeouts**: Increase timeout values in environment variables

## Next Steps for Development

The codebase is production-ready and well-structured. Potential enhancements:

- Add more podcast sources with new scrapers
- Implement batch processing optimizations
- Add transcription quality metrics
- Create web interface for easier management
- Add automated podcast discovery

## Claude Integration

The repository is optimized for Claude development with:
- Comprehensive `.claude/settings.local.json` configuration
- Detailed `CLAUDE.md` documentation  
- Proper permissions for Python execution and web fetching
- Clear project structure documentation 