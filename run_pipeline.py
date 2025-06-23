#!/usr/bin/env python3
"""
Complete pipeline to scrape podcast and transcribe audio
"""

import os
import sys
from pathlib import Path

# Import our modules
from scraper_politica_exterior import main as scrape_main
from transcribe import main as transcribe_main

def main():
    """
    Run the complete pipeline: scrape podcast -> transcribe audio
    """
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
    print("Check the 'downloads' folder for audio files")
    print("Check the 'transcriptions' folder for transcripts")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())