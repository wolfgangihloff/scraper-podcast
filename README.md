# Podcast Scraper and Transcriber

A Python toolkit to download podcast episodes from multiple sources and transcribe them using the StackIT AI Assistant API.

**Supported Sources:**
- 🇪🇸 **Política Exterior** - Spanish foreign policy podcast
- 🇩🇪 **eGovernment Podcast** - German digitalization and government tech podcast (220+ episodes)
- 🎥 **YouTube Videos** - Individual YouTube video downloads

## ✅ Current Status

**Fully Working!** The complete pipeline successfully:
- ✅ Extracts and downloads podcast episodes from Política Exterior  
- ✅ Transcribes audio using StackIT AI Assistant API with proper authentication
- ✅ Saves detailed transcriptions with timestamps and speaker identification
- ✅ Handles the complete 4-step API workflow: get upload URL → upload file → start transcription → poll for completion

## Features

### Content Scraping
- **`scraper_politica_exterior.py`** - Política Exterior podcast scraper
- **`scraper_egovpodcast.py`** - eGovernment podcast scraper (all 220+ episodes)
- **`scraper_youtube.py`** - YouTube video scraper for individual videos
- Web scraping to extract audio URLs from podcast pages
- Downloads audio files from CDN sources (Podbean, Podseed)
- Downloads YouTube videos using yt-dlp
- Saves audio files with original filenames
- Multiple extraction methods: direct CDN, RSS feeds, static HTML parsing
- Optional headless browser support for JavaScript-generated URLs
- Error handling for network issues and missing audio files
- Support for common audio formats (MP3, MP4, M4A, WAV, OGG, WebM)
- Progress reporting and metadata extraction

### Audio Transcription (`transcribe.py`)
- Integration with StackIT AI Assistant API
- Command-line interface with flexible options
- Flexible authentication system using environment variables
- Automatic transcription of downloaded audio files
- Saves transcriptions to `transcriptions` folder
- Support for large audio files with extended timeouts
- Detailed output with timestamps and speaker identification
- JSON and text output formats

**Transcription Commands:**
```bash
python transcribe.py                    # Process smallest file (for testing)
python transcribe.py --file "episode"  # Process specific file (partial name match)
python transcribe.py --all             # Process all files in downloads folder
python transcribe.py --list            # List available files
```

### Pipeline Automation (`run_pipeline.py`)
- Complete end-to-end automation
- Download → Transcribe → Save workflow
- Graceful error handling and status reporting

## Installation

1. Clone this repository:
```bash
git clone https://github.com/yourusername/scraper-podcast-politica-exterior.git
cd scraper-podcast-politica-exterior
```

2. Create and activate a virtual environment (recommended):
```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

3. Install required dependencies:
```bash
pip install -r requirements.txt
```

4. Set up authentication for transcription:
```bash
cp .env.template .env
# Edit .env with your StackIT authentication details
```

## Usage

**⚠️ Important:** Always activate your virtual environment first:
```bash
source .venv/bin/activate
```

### Quick Start

**Download eGovernment Podcast (all 220+ episodes):**
```bash
python scraper_egovpodcast.py
```

**Download Política Exterior Podcast:**
```bash
python scraper_politica_exterior.py
```

**Download YouTube Video:**
```bash
python scraper_youtube.py https://www.youtube.com/watch?v=WOQbDOrI_5c
```

**Transcribe downloaded files:**
```bash
python transcribe.py --all
```

### Detailed Usage

#### 1. Download Podcasts

**eGovernment Podcast (German):**
```bash
python scraper_egovpodcast.py
# Downloads all 220+ episodes to downloads_egov/
```

**Política Exterior Podcast (Spanish):**
```bash
python scraper_politica_exterior.py
# Downloads latest episode to downloads/
```

**YouTube Videos:**
```bash
python scraper_youtube.py https://www.youtube.com/watch?v=WOQbDOrI_5c
# Downloads video to downloads_youtube/
```

**Supported YouTube URL formats:**
- `https://www.youtube.com/watch?v=VIDEO_ID`
- `https://youtu.be/VIDEO_ID`
- `https://www.youtube.com/shorts/VIDEO_ID`
- Playlist URLs (extracts individual video)

**YouTube Features:**
- Downloads in best available quality (MP4/WebM)
- Saves video metadata (JSON)
- Downloads subtitles if available (EN, DE, ES)
- Progress reporting with download speed
- Automatic playlist URL handling

#### 2. Transcribe Audio Files

**Process all files:**
```bash
python transcribe.py --all
```

**Process specific file:**
```bash
python transcribe.py --file "episode_name"
```

**List available files:**
```bash
python transcribe.py --list
```

#### 3. Complete Pipeline
```bash
# For Política Exterior podcast
python run_pipeline.py

# For YouTube videos
python run_pipeline.py https://www.youtube.com/watch?v=WOQbDOrI_5c
```

### Moving Files Between Folders

To transcribe eGovernment episodes, move them to the main downloads folder:
```bash
mv downloads_egov/*.mp4 downloads/
python transcribe.py --all
```

## Configuration

### Podcast Source
To scrape a different podcast page, edit the `PODCAST_PAGE` variable in `scraper_politica_exterior.py`:

```python
PODCAST_PAGE = "https://your-podcast-website.com/podcast-page"
```

### Transcription Authentication

**⚠️ Security Notice:** Never commit your `.env` file with real credentials to version control.

1. Copy the template:
```bash
cp .env.template .env
```

2. Get your StackIT access token:
   - Open https://assistant.demo.pre-prod.stackit.run in your browser
   - Log in with your credentials
   - Open Developer Tools (F12) → Application/Storage tab
   - Look for 'access_token' in localStorage or sessionStorage

3. Edit `.env` with your authentication details:
```bash
# Replace with your actual access token
STACKIT_ACCESS_TOKEN=your_actual_access_token_here
```

## Example Output

Successful podcast download:
```
Searching for podcast audio files...
Found 2 potential audio URLs:
1. https://mcdn.podbean.com/mf/web/jktucxjfwc2sjy4k/-_PE_Episodio_8_editadob3q8l.mp3
2. mp3

Using: https://mcdn.podbean.com/mf/web/jktucxjfwc2sjy4k/-_PE_Episodio_8_editadob3q8l.mp3
Downloading audio file...
Successfully saved: downloads/-_PE_Episodio_8_editadob3q8l.mp3
```

If no audio is found on the main page, the scraper will check the RSS feed for additional podcast pages.

## Requirements

- Python 3.7+
- Dependencies listed in `requirements.txt`:
  - `feedparser` - RSS feed parsing
  - `requests` - HTTP requests and downloads
  - `beautifulsoup4` - HTML parsing
  - `python-dotenv` - Environment variable management
  - `yt-dlp` - YouTube video downloading

## Project Structure

```
├── scraper_politica_exterior.py  # Política Exterior podcast scraper
├── scraper_egovpodcast.py        # eGovernment podcast scraper
├── scraper_youtube.py            # YouTube video scraper
├── transcribe.py                 # Audio transcription script
├── run_pipeline.py               # Complete pipeline automation
├── requirements.txt              # Python dependencies
├── .env.template                 # Authentication template
├── .env                         # Your authentication details (create from template)
├── .gitignore                   # Git ignore file
├── downloads/                   # Política Exterior downloads
├── downloads_egov/              # eGovernment podcast downloads
├── downloads_youtube/           # YouTube video downloads
├── transcriptions/              # Política Exterior transcriptions
├── transcriptions_egov/         # eGovernment transcriptions
├── transcriptions_youtube/      # YouTube transcriptions
├── README.md                    # This file  
├── LICENSE                      # Project license
└── CLAUDE.md                    # Claude Code guidance file
```

## How It Works

### Política Exterior Scraper (`scraper_politica_exterior.py`)
1. **Web Scraping**: Analyzes the podcast webpage HTML to find audio URLs using regex patterns
2. **RSS Fallback**: If no audio is found on the main page, checks the RSS feed for additional podcast pages
3. **Pattern Matching**: Looks for direct MP3 URLs from Podbean hosting

### eGovernment Scraper (`scraper_egovpodcast.py`)
1. **RSS Feed Analysis**: Parses the complete RSS feed to get all 220+ episodes
2. **Direct CDN Construction**: Builds CDN URLs using pattern: `https://cdn.podseed.org/egovernment/egov{number}.mp4`
3. **URL Testing**: Validates each constructed URL before download
4. **Fallback Methods**: Optional headless browser support for JavaScript-generated URLs

### YouTube Scraper (`scraper_youtube.py`)
1. **URL Validation**: Validates various YouTube URL formats (watch, youtu.be, shorts, playlists)
2. **Video Extraction**: Uses yt-dlp to extract video information and download URLs
3. **Quality Selection**: Downloads in best available quality (MP4/WebM)
4. **Metadata & Subtitles**: Saves video metadata and downloads available subtitles
5. **Progress Reporting**: Real-time download progress with speed and percentage

### Transcription Process (`transcribe.py`)
1. **File Upload**: Gets secure upload URL from StackIT API
2. **Audio Processing**: Uploads audio file to staging area
3. **Transcription Job**: Starts transcription task with metadata
4. **Polling**: Monitors job status until completion
5. **Result Retrieval**: Downloads transcription with timestamps and speaker info

## Extending to Other Podcasts

To adapt this scraper for other podcast websites:

1. Change the `PODCAST_PAGE` URL in the `main()` function
2. Adjust the regex patterns if the hosting service uses different URL structures
3. The RSS fallback will work with most standard podcast feeds

## Error Handling

The script includes error handling for:
- Network connection issues
- Missing RSS feed entries
- Feeds without audio content
- Download failures
- File system errors

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## Security

**⚠️ Important Security Notes:**
- Never commit `.env` files with real credentials
- The `.env` file is automatically ignored by Git
- Always use the `.env.template` as a reference
- Keep your StackIT access tokens secure and private

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Disclaimer

This tool is for educational and personal use. Ensure you have permission to download and transcribe podcast content. Respect copyright and terms of use of the websites you scrape.