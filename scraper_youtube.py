#!/usr/bin/env python3
"""
YouTube Video Scraper

Downloads individual YouTube videos to the downloads_youtube folder.
Supports various YouTube URL formats including playlists and direct video links.

Usage:
    python scraper_youtube.py <YouTube URL>
    python scraper_youtube.py https://www.youtube.com/watch?v=WOQbDOrI_5c
"""

import os
import sys
import re
from urllib.parse import urlparse, parse_qs
import yt_dlp

def validate_youtube_url(url):
    """Validate if the URL is a valid YouTube URL"""
    youtube_patterns = [
        r'(?:https?://)?(?:www\.)?youtube\.com/watch\?v=[\w-]+',
        r'(?:https?://)?(?:www\.)?youtube\.com/playlist\?list=[\w-]+',
        r'(?:https?://)?(?:www\.)?youtu\.be/[\w-]+',
        r'(?:https?://)?(?:www\.)?youtube\.com/shorts/[\w-]+'
    ]
    
    for pattern in youtube_patterns:
        if re.match(pattern, url):
            return True
    return False

def extract_video_id(url):
    """Extract video ID from various YouTube URL formats"""
    # Handle youtu.be format
    if 'youtu.be' in url:
        return url.split('/')[-1].split('?')[0]
    
    # Handle youtube.com format
    parsed_url = urlparse(url)
    if parsed_url.hostname in ['www.youtube.com', 'youtube.com']:
        if parsed_url.path == '/watch':
            query_params = parse_qs(parsed_url.query)
            return query_params.get('v', [None])[0]
        elif parsed_url.path == '/shorts':
            return parsed_url.path.split('/')[-1]
    
    return None

def download_youtube_video(url, output_folder="downloads_youtube"):
    """Download a YouTube video to the specified folder"""
    
    # Validate URL
    if not validate_youtube_url(url):
        print(f"ERROR: Invalid YouTube URL: {url}")
        print("Supported formats:")
        print("  - https://www.youtube.com/watch?v=VIDEO_ID")
        print("  - https://youtu.be/VIDEO_ID")
        print("  - https://www.youtube.com/shorts/VIDEO_ID")
        return False
    
    # Create output folder
    try:
        os.makedirs(output_folder, exist_ok=True)
        print(f"Output folder: {output_folder}")
    except OSError as e:
        print(f"ERROR creating output folder {output_folder}: {e}")
        return False
    
    # Configure yt-dlp options
    ydl_opts = {
        'outtmpl': os.path.join(output_folder, '%(title)s.%(ext)s'),
        'format': 'best[ext=mp4]/best[ext=webm]/best',  # Prefer MP4, fallback to WebM, then best available
        'writeinfojson': True,  # Save video metadata
        'writesubtitles': False,  # Disable subtitle download to avoid rate limits
        'writeautomaticsub': False,  # Disable auto-generated subtitles
        'ignoreerrors': False,  # Don't ignore errors
        'no_warnings': False,  # Show warnings
        'progress_hooks': [progress_hook],  # Progress callback
    }
    
    try:
        print(f"Downloading: {url}")
        print("This may take a while depending on video size and your internet connection...")
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            # Get video info first
            info = ydl.extract_info(url, download=False)
            video_title = info.get('title', 'Unknown Title')
            duration = info.get('duration', 0)
            
            print(f"Video: {video_title}")
            if duration:
                minutes = duration // 60
                seconds = duration % 60
                print(f"Duration: {minutes}:{seconds:02d}")
            
            # Download the video
            ydl.download([url])
            
        print(f"✅ Successfully downloaded to {output_folder}/")
        return True
        
    except yt_dlp.DownloadError as e:
        print(f"ERROR downloading video: {e}")
        return False
    except Exception as e:
        print(f"ERROR: Unexpected error during download: {e}")
        return False

def progress_hook(d):
    """Progress callback for yt-dlp"""
    if d['status'] == 'downloading':
        # Calculate progress percentage
        total = d.get('total_bytes') or d.get('total_bytes_estimate', 0)
        downloaded = d.get('downloaded_bytes', 0)
        
        if total > 0:
            percentage = (downloaded / total) * 100
            speed = d.get('speed', 0)
            if speed:
                speed_mb = speed / 1024 / 1024
                print(f"\rDownloading... {percentage:.1f}% ({speed_mb:.1f} MB/s)", end='', flush=True)
        else:
            print(f"\rDownloading... {downloaded} bytes", end='', flush=True)
    
    elif d['status'] == 'finished':
        print(f"\n✅ Download completed: {d.get('filename', 'Unknown file')}")

def main():
    """Main function to handle command line arguments and execute download"""
    
    if len(sys.argv) < 2:
        print("YouTube Video Scraper")
        print("=" * 50)
        print("Downloads individual YouTube videos to downloads_youtube folder")
        print()
        print("Usage:")
        print("  python scraper_youtube.py <YouTube URL>")
        print()
        print("Examples:")
        print("  python scraper_youtube.py https://www.youtube.com/watch?v=WOQbDOrI_5c")
        print("  python scraper_youtube.py https://youtu.be/WOQbDOrI_5c")
        print("  python scraper_youtube.py https://www.youtube.com/shorts/WOQbDOrI_5c")
        print()
        print("Features:")
        print("  - Downloads to downloads_youtube/ folder")
        print("  - Saves video metadata (JSON)")
        print("  - Downloads subtitles if available")
        print("  - Progress reporting")
        print("  - Error handling")
        sys.exit(1)
    
    url = sys.argv[1].strip()
    
    # Remove any trailing arguments that might be part of the URL
    if '&list=' in url:
        # Extract just the video part from playlist URLs
        base_url = url.split('&list=')[0]
        print(f"Note: Extracting video from playlist URL")
        print(f"Original: {url}")
        print(f"Using: {base_url}")
        url = base_url
    
    print("YouTube Video Scraper")
    print("=" * 50)
    
    success = download_youtube_video(url)
    
    if success:
        print("\n🎉 Download completed successfully!")
        print(f"Check the downloads_youtube/ folder for your video.")
    else:
        print("\n❌ Download failed. Please check the error messages above.")
        sys.exit(1)

if __name__ == "__main__":
    main() 