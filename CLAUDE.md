# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

# Scraper Podcast

This is a Python-based podcast scraper and transcription toolkit that supports two main targets:

1. **Política Exterior** website - Primary target for Spanish political podcasts
2. **RSS Feed Fallback** - Generic RSS feed parsing for compatible podcast sources

The project consists of multiple scripts that provide a complete pipeline:

1. **Podcast Scraping** (`scraper_politica_exterior.py`): Web scrapes Política Exterior podcast pages to extract audio URLs using regex patterns
2. **Audio Transcription** (`transcribe.py`): Uses StackIT AI Assistant API to transcribe downloaded audio files  
3. **Pipeline Automation** (`run_pipeline.py`): Runs the complete download → transcribe → save workflow
4. **Authentication**: Uses environment variables for secure API access

## Dependencies

The project requires these Python packages:
- `feedparser` - RSS feed parsing
- `requests` - HTTP requests for downloading and API calls
- `beautifulsoup4` - HTML parsing (imported for future use)
- `python-dotenv` - Environment variable management

Install dependencies:
```bash
pip install feedparser requests beautifulsoup4 python-dotenv
```

## Authentication Setup

For transcription functionality:
1. Copy `.env.template` to `.env`
2. Add StackIT authentication details to `.env`
3. The script supports multiple auth methods (Bearer token, API key, custom headers)

## Running the Scraper

### Complete Pipeline (Recommended)
```bash
python run_pipeline.py
```

### Individual Scripts
```bash
python scraper_politica_exterior.py  # Download Política Exterior podcast only
python scraper_egovpodcast.py        # Download eGovernment podcast episodes
python transcribe.py                  # Transcribe existing audio files
```

### Pipeline Flow
The complete pipeline will:
1. **Download**: Analyze podcast webpage HTML to find audio URLs using regex patterns
2. **Save**: Download audio file from discovered URL (typically Podbean hosting) to "downloads" folder
3. **Transcribe**: Upload audio to StackIT AI Assistant API for transcription
4. **Output**: Save transcription to "transcriptions" folder as text file
5. **Fallback**: Fall back to RSS feed analysis if no audio URLs found on main page

## Code Architecture

The project uses a modular approach with separate scripts for different functions:

### `scraper_politica_exterior.py`
- **Web Scraping**: Uses `requests` and regex patterns to extract audio URLs from HTML
- **URL Pattern Matching**: Multiple regex patterns to catch different audio hosting formats  
- **Audio Download**: Streams audio files using `requests` with chunked downloading
- **RSS Fallback**: Uses `feedparser` as backup to check RSS feed for podcast pages

### `transcribe.py`
- **API Integration**: Connects to StackIT AI Assistant API for transcription
- **Authentication**: Flexible auth system using environment variables
- **File Handling**: Processes most recent audio files automatically
- **Output Management**: Saves transcriptions with organized naming

### `run_pipeline.py`
- **Orchestration**: Runs complete download → transcribe workflow
- **Error Handling**: Comprehensive error handling with user-friendly messages
- **Status Reporting**: Clear progress updates and completion status

Key functions:
- `find_audio_urls_in_page(url)`: Extracts audio URLs from webpage using regex
- `upload_and_transcribe(file_path)`: Handles API upload and transcription
- `save_transcription(data, file_path)`: Saves transcription results to file

The project includes two specialized scrapers:
- `scraper_politica_exterior.py`: Targets the Política Exterior podcast website
- `scraper_egovpodcast.py`: Downloads episodes from egovernment-podcast.com

The transcription component works with any StackIT-compatible API endpoint.