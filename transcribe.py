import os
import requests
import json
import time
import sys
import argparse
from dotenv import load_dotenv
from pathlib import Path

# Load environment variables
load_dotenv()

def upload_and_transcribe(audio_file_path):
    """
    Upload audio file and transcribe using StackIT AI Assistant
    Following the actual API workflow discovered from HAR analysis
    """
    # API endpoints discovered from HAR analysis
    usecase_id = "a2d5214b-9a3b-42d3-96db-3c4986e9eeae"
    app_base_url = f"https://pharia-os-applications.demo.pre-prod.stackit.run/{usecase_id}"
    
    # Set up session with headers from environment and HAR analysis
    session = requests.Session()
    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
        'Accept': '*/*',
        'Accept-Language': 'en-US,en;q=0.9',
        'Accept-Encoding': 'gzip, deflate, br, zstd',
    })
    
    # Add headers from environment variables
    for key, value in os.environ.items():
        if key.startswith('STACKIT_HEADER_'):
            header_name = key.replace('STACKIT_HEADER_', '').replace('_', '-').lower()
            session.headers[header_name] = value
    
    # Check for access token authentication
    access_token = os.getenv('STACKIT_ACCESS_TOKEN')
    cookie_token = os.getenv('STACKIT_HEADER_COOKIE')
    
    if access_token:
        print("🔑 Found access token, using as Authorization Bearer...")
        session.headers['Authorization'] = f'Bearer {access_token}'
        print(f"Auth headers: ['Authorization']")
    elif cookie_token:
        # Try as Authorization Bearer token if it looks like a JWT
        if cookie_token.startswith('eyJ'):
            print("🔑 Found JWT token, trying as Authorization Bearer...")
            session.headers['Authorization'] = f'Bearer {cookie_token}'
        else:
            print("🍪 Found cookie token, using as Cookie header...")
            session.headers['Cookie'] = cookie_token
        
        print(f"Auth headers: {[k for k in session.headers.keys() if k.lower() in ['authorization', 'cookie']]}")
    else:
        print("⚠️  WARNING: No authentication found!")
        print("The API requires authentication. To get your access token:")
        print("1. Open https://assistant.demo.pre-prod.stackit.run in your browser")
        print("2. Log in with your credentials")
        print("3. Open Developer Tools (F12) → Application/Storage tab")
        print("4. Look for 'access_token' in localStorage or sessionStorage")
        print("5. Add it to .env as: STACKIT_ACCESS_TOKEN=your_access_token")
        print("\nTrying anyway in case authentication isn't required...")
        print()
    
    try:
        # Check if file exists
        if not os.path.exists(audio_file_path):
            print(f"ERROR: Audio file not found: {audio_file_path}")
            return None
        
        file_size = os.path.getsize(audio_file_path)
        file_size_mb = file_size / (1024 * 1024)
        filename = os.path.basename(audio_file_path)
        
        print(f"Starting transcription workflow for: {filename} ({file_size_mb:.1f} MB)")
        
        # STEP 1: Get upload URL
        print("\n🔗 Step 1: Getting upload URL...")
        upload_url_endpoint = f"{app_base_url}/transcription/file/data-stage-url"
        
        response = session.get(upload_url_endpoint)
        if response.status_code != 200:
            print(f"❌ Failed to get upload URL: {response.status_code}")
            print(f"Response: {response.text}")
            return None
        
        upload_info = response.json()
        upload_url = upload_info.get('url')
        if not upload_url:
            print(f"❌ No upload URL in response: {upload_info}")
            return None
        
        print(f"✅ Got upload URL: {upload_url}")
        
        # STEP 2: Upload file
        print("\n📁 Step 2: Uploading file...")
        upload_endpoint = f"{upload_url}/files"
        
        # Upload file using the correct field name from HAR analysis
        mime_type = 'audio/mp4' if filename.lower().endswith('.mp4') else 'audio/mpeg'
        with open(audio_file_path, 'rb') as audio_file:
            files = {
                'sourceData': (filename, audio_file, mime_type)
            }
            
            response = session.post(upload_endpoint, files=files, timeout=300)
        
        if response.status_code != 201:
            print(f"❌ File upload failed: {response.status_code}")
            print(f"Response: {response.text}")
            return None
        
        file_info = response.json()
        file_id = file_info.get('id') or file_info.get('fileId')  # Try both possible field names
        if not file_id:
            print(f"❌ No file ID in response: {file_info}")
            return None
        
        print(f"✅ File uploaded with ID: {file_id}")
        
        # Get audio duration - use a better estimate based on MP3 structure
        # For test_short.mp3 (629275 bytes), the actual duration was 30.027755 seconds
        # This suggests bitrate ≈ 167 kbps (629275 * 8 / 30.027755 / 1000)
        estimated_duration = file_size * 8 / (167 * 1000)  # Estimate based on observed data
        print(f"   Estimated duration: {estimated_duration:.2f} seconds")
        
        # Detect language based on source
        source_language = "de"  # Default to German
        if "egov" in filename.lower() or "downloads_egov" in str(audio_file_path):
            source_language = "de"  # eGovernment podcast is German
        elif "politica" in filename.lower() or "PE_" in filename:
            source_language = "es"  # Política Exterior is Spanish
        
        print(f"   Detected language: {source_language}")
        
        # STEP 3: Start transcription
        print("\n🎯 Step 3: Starting transcription...")
        transcription_endpoint = f"{app_base_url}/transcription"
        
        transcription_data = {
            "file_id": file_id,
            "file_name": filename,
            "file_size": file_size,
            "mime_type": "audio/mp4" if filename.lower().endswith('.mp4') else "audio/mpeg",
            "duration": estimated_duration,
            "language": source_language
        }
        
        print(f"   Sending request to: {transcription_endpoint}")
        print(f"   Data: {transcription_data}")
        
        response = session.post(
            transcription_endpoint, 
            json=transcription_data,
            headers={'Content-Type': 'application/json'},
            timeout=30
        )
        
        print(f"   Response status: {response.status_code}")
        print(f"   Response: {response.text[:200]}...")
        
        if response.status_code != 200:
            print(f"❌ Transcription start failed: {response.status_code}")
            print(f"Response: {response.text}")
            return None
        
        task_info = response.json()
        task_id = task_info.get('id')
        if not task_id:
            print(f"❌ No task ID in response: {task_info}")
            return None
        
        print(f"✅ Transcription started with task ID: {task_id}")
        print(f"   Status: {task_info.get('status', 'Unknown')}")
        
        # STEP 4: Poll for completion
        print("\n⏳ Step 4: Waiting for transcription to complete...")
        status_endpoint = f"{app_base_url}/transcription/status/{task_id}"
        
        max_wait_time = 300  # 5 minutes
        poll_interval = 5  # 5 seconds
        elapsed_time = 0
        
        while elapsed_time < max_wait_time:
            response = session.get(status_endpoint)
            if response.status_code != 200:
                print(f"❌ Status check failed: {response.status_code}")
                break
            
            status_info = response.json()
            status = status_info.get('status', 'Unknown')
            print(f"   Status: {status} (elapsed: {elapsed_time}s)")
            
            if status == 'SUCCESS':
                print("✅ Transcription completed!")
                # Get the full transcription content with segments
                transcription_content_endpoint = f"{app_base_url}/transcription/{task_id}"
                
                # Sometimes segments take a moment to be processed, retry a few times
                for retry in range(3):
                    resp = session.get(transcription_content_endpoint)
                    if resp.status_code == 200:
                        transcription_content = resp.json()
                        segments_count = len(transcription_content.get('segments', []))
                        if segments_count > 0:
                            status_info['result'] = transcription_content
                            print(f"   Retrieved transcription with {segments_count} segments")
                            return status_info
                        elif retry < 2:  # Wait a bit for segments to be processed
                            print(f"   Segments not ready, waiting 5 seconds... (attempt {retry + 1}/3)")
                            time.sleep(5)
                        else:
                            # No segments found, but transcription is complete
                            status_info['result'] = transcription_content
                            print(f"   Transcription complete but no segments available")
                            return status_info
                    else:
                        print(f"   Warning: Could not retrieve transcription content (status {resp.status_code})")
                        return status_info
                
                return status_info
            elif status in ['FAILED', 'ERROR', 'FAILURE']:
                print(f"❌ Transcription failed with status: {status}")
                return status_info
            
            time.sleep(poll_interval)
            elapsed_time += poll_interval
        
        print(f"❌ Transcription timed out after {max_wait_time} seconds")
        return None
            
    except Exception as e:
        print(f"ERROR: {e}")
        return None

def get_transcription_output_path(audio_file_path):
    """
    Determine the appropriate transcription output folder and file path
    """
    audio_filename = Path(audio_file_path).stem
    
    # Determine output folder based on file source
    if "egov" in audio_filename.lower() or "downloads_egov" in str(audio_file_path):
        output_dir = Path("transcriptions_egov")
    else:
        output_dir = Path("transcriptions")
    
    output_dir.mkdir(exist_ok=True)
    output_file = output_dir / f"{audio_filename}_transcription.txt"
    
    return output_file

def transcription_exists(audio_file_path):
    """
    Check if transcription already exists for this audio file
    """
    output_file = get_transcription_output_path(audio_file_path)
    return output_file.exists()

def save_transcription(transcription_data, audio_file_path):
    """
    Save transcription to a text file
    """
    if not transcription_data:
        return None
    
    # Get the appropriate output path
    output_file = get_transcription_output_path(audio_file_path)
    
    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            if isinstance(transcription_data, dict):
                # Extract transcription text if available
                if 'result' in transcription_data and isinstance(transcription_data['result'], dict):
                    result = transcription_data['result']
                    
                    # Write full transcription from segments
                    if 'segments' in result and result['segments']:
                        f.write("TRANSCRIPTION:\n")
                        f.write("=" * 50 + "\n")
                        
                        # Combine all segment texts
                        full_text = ""
                        for segment in result['segments']:
                            if 'text' in segment:
                                full_text += segment['text'] + " "
                        
                        f.write(full_text.strip())
                        f.write("\n\n")
                        
                        # Write detailed segments with timestamps
                        f.write("DETAILED SEGMENTS:\n")
                        f.write("=" * 40 + "\n")
                        for i, segment in enumerate(result['segments'], 1):
                            start = segment.get('start', 'N/A')
                            end = segment.get('end', 'N/A')
                            text = segment.get('text', '')
                            f.write(f"[{start}s - {end}s] {text}\n")
                        f.write("\n")
                    elif 'transcription' in result:
                        f.write("TRANSCRIPTION:\n")
                        f.write("=" * 50 + "\n")
                        f.write(result['transcription'])
                        f.write("\n\n")
                    
                    # Add metadata
                    f.write("METADATA:\n")
                    f.write("=" * 30 + "\n")
                    f.write(f"Task ID: {transcription_data.get('id', 'N/A')}\n")
                    f.write(f"Status: {transcription_data.get('status', 'N/A')}\n")
                    f.write(f"File: {result.get('name', 'N/A')}\n")
                    f.write(f"Duration: {result.get('duration', 'N/A')} seconds\n")
                    f.write(f"Language: {result.get('language', 'N/A')}\n")
                    f.write(f"Segments: {len(result.get('segments', []))}\n")
                else:
                    # Pretty print all JSON data if structure is different
                    f.write(json.dumps(transcription_data, indent=2, ensure_ascii=False))
            else:
                f.write(str(transcription_data))
        
        print(f"Transcription saved to: {output_file}")
        return output_file
        
    except Exception as e:
        print(f"ERROR saving transcription: {e}")
        return None

def main():
    """
    Main function to process audio files from downloads folder
    """
    
    parser = argparse.ArgumentParser(
        description='Transcribe audio files using StackIT AI Assistant',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python transcribe.py                           # Process smallest file (for testing)
  python transcribe.py --file "episode.mp3"     # Process specific file (partial name match)
  python transcribe.py --list                   # List all files with transcription status
  python transcribe.py --all                    # Process all files (skips existing transcriptions)

Notes:
  • Files from downloads/ → transcriptions/
  • Files from downloads_egov/ → transcriptions_egov/
  • Existing transcriptions are automatically skipped
        """
    )
    parser.add_argument('--file', '-f', 
                       help='Specific audio file to transcribe (partial name match in any downloads folder)')
    parser.add_argument('--all', '-a', action='store_true',
                       help='Process all audio files from both downloads folders')
    parser.add_argument('--list', '-l', action='store_true',
                       help='List all available audio files with transcription status')
    
    args = parser.parse_args()
    
    downloads_dir = Path("downloads")
    downloads_egov_dir = Path("downloads_egov")
    
    # Create downloads folder if it doesn't exist
    downloads_dir.mkdir(exist_ok=True)
    
    # Find audio files from both download folders
    audio_files = []
    audio_patterns = ['*.mp3', '*.m4a', '*.wav', '*.ogg', '*.mp4']
    
    # Main downloads folder
    for pattern in audio_patterns:
        audio_files.extend(downloads_dir.glob(pattern))
    
    # eGovernment downloads folder
    if downloads_egov_dir.exists():
        for pattern in audio_patterns:
            audio_files.extend(downloads_egov_dir.glob(pattern))
    
    if not audio_files:
        print("No audio files found in downloads folders")
        print("Place your audio files in one of these folders:")
        print("  • downloads/ (for transcription to transcriptions/)")
        print("  • downloads_egov/ (for transcription to transcriptions_egov/)")
        return 1
    
    # List files if requested
    if args.list:
        print(f"Found {len(audio_files)} audio file(s):")
        for i, file in enumerate(audio_files, 1):
            file_size = file.stat().st_size / (1024 * 1024)
            folder = "downloads" if file.parent.name == "downloads" else "downloads_egov"
            transcription_folder = "transcriptions" if folder == "downloads" else "transcriptions_egov"
            exists = "✅" if transcription_exists(file) else "❌"
            print(f"  {i}. {file.name} ({file_size:.1f} MB) [{folder} → {transcription_folder}] {exists}")
        print("\nLegend: ✅ = transcription exists, ❌ = not transcribed yet")
        return 0
    
    # Select files to process
    files_to_process = []
    
    if args.file:
        # Process specific file
        target_file = None
        for file in audio_files:
            if args.file in file.name or file.name == args.file:
                target_file = file
                break
        
        if not target_file:
            print(f"❌ File '{args.file}' not found in downloads folder")
            print("Available files:")
            for file in audio_files:
                print(f"  - {file.name}")
            return 1
        
        files_to_process = [target_file]
    
    elif args.all:
        # Process all files
        files_to_process = audio_files
        print(f"Will process all {len(audio_files)} files")
    
    else:
        # Default: process smallest file for testing
        files_to_process = [min(audio_files, key=lambda f: f.stat().st_size)]
        print(f"No specific file requested, processing smallest file for testing")
    
    # Process selected files
    successful_transcriptions = 0
    skipped_transcriptions = 0
    failed_transcriptions = 0
    
    for i, selected_file in enumerate(files_to_process, 1):
        file_size = selected_file.stat().st_size / (1024 * 1024)
        
        if len(files_to_process) > 1:
            print(f"\n{'='*60}")
            print(f"Processing file {i}/{len(files_to_process)}: {selected_file.name} ({file_size:.1f} MB)")
            print(f"{'='*60}")
        else:
            print(f"\nProcessing: {selected_file.name} ({file_size:.1f} MB)")
        
        # Check if transcription already exists
        if transcription_exists(selected_file):
            existing_file = get_transcription_output_path(selected_file)
            print(f"⏭️  Transcription already exists: {existing_file}")
            print(f"   Skipping {selected_file.name}")
            skipped_transcriptions += 1
            continue
        
        # Transcribe
        print("Starting transcription...")
        result = upload_and_transcribe(selected_file)
        
        if result:
            # Save transcription
            output_file = save_transcription(result, selected_file)
            if output_file:
                print(f"✅ Transcription completed successfully!")
                print(f"📄 Saved to: {output_file}")
                successful_transcriptions += 1
            else:
                print("❌ Transcription completed but failed to save to file")
                failed_transcriptions += 1
        else:
            print("❌ Transcription failed")
            failed_transcriptions += 1
            if len(files_to_process) > 1:
                print("Continuing with next file...")
    
    # Final summary
    print(f"\n🎉 Processing Summary:")
    print(f"✅ Successful transcriptions: {successful_transcriptions}")
    print(f"⏭️  Skipped (already exists): {skipped_transcriptions}")
    print(f"❌ Failed transcriptions: {failed_transcriptions}")
    print(f"📊 Total files processed: {len(files_to_process)}")
    
    if successful_transcriptions > 0:
        print(f"\n📁 Transcriptions saved to:")
        print(f"   • transcriptions/ (Política Exterior)")
        print(f"   • transcriptions_egov/ (eGovernment)")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())