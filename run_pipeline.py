#!/usr/bin/env python3
"""
Complete pipeline to scrape podcast and transcribe audio
"""

import os
import sys
from pathlib import Path

# Import our modules
from scraper_politica_exterior import main as scrape_main
from scraper_youtube import download_youtube_video
from transcribe import main as transcribe_main

def main():
    """
    Run the complete pipeline: scrape podcast -> transcribe audio
    """
    print("=== Podcast & YouTube Pipeline ===")
    print()
    
    # Check if YouTube URL is provided
    if len(sys.argv) > 1 and ('youtube.com' in sys.argv[1] or 'youtu.be' in sys.argv[1]):
        print("=== YouTube Video Pipeline ===")
        print()
        
        # Step 1: Download YouTube video
        print("Step 1: Downloading YouTube video...")
        try:
            success = download_youtube_video(sys.argv[1])
            if success:
                print("✅ YouTube video download completed")
            else:
                print("❌ YouTube video download failed")
                return 1
        except Exception as e:
            print(f"❌ YouTube video download failed: {e}")
            return 1
        
        # Update transcription folder for YouTube videos
        transcription_folder = "transcriptions_youtube"
        
    else:
        print("=== Política Exterior Podcast Pipeline ===")
        print()
        
        # Step 1: Scrape podcast
        print("Step 1: Downloading latest podcast episode...")
        try:
            scrape_main()
            print("✅ Podcast download completed")
        except Exception as e:
            print(f"❌ Podcast download failed: {e}")
            return 1
        
        # Use default transcription folder for podcasts
        transcription_folder = "transcriptions"
    
    print()
    
    # Step 2: Check if .env file exists
    if not Path(".env").exists():
        print("⚠️  Warning: .env file not found")
        print("To enable transcription:")
        print("1. Copy .env.template to .env")
        print("2. Add your StackIT authentication details")
        print("3. Run this script again")
        print()
        print("For now, only podcast download was completed.")
        return 0
    
    # Step 3: Transcribe audio
    print("Step 3: Transcribing audio...")
    try:
        # Save original sys.argv and set arguments for transcribe.py
        original_argv = sys.argv.copy()
        sys.argv = ['transcribe.py']  # Default behavior: process smallest file
        transcribe_main()
        sys.argv = original_argv  # Restore original argv
        print("✅ Transcription completed")
    except Exception as e:
        print(f"❌ Transcription failed: {e}")
        print("Check your .env file authentication details")
        # Restore original argv in case of error
        sys.argv = original_argv if 'original_argv' in locals() else sys.argv
        return 1
    
    print()
    print("🎉 Pipeline completed successfully!")
    if 'transcription_folder' in locals() and transcription_folder == "transcriptions_youtube":
        print("Check the 'downloads_youtube' folder for video files")
        print("Check the 'transcriptions_youtube' folder for transcripts")
    else:
        print("Check the 'downloads' folder for audio files")
        print("Check the 'transcriptions' folder for transcripts")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())