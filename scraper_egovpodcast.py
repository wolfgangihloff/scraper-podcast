#!/usr/bin/env python3
"""
eGovernment Podcast Scraper
Downloads all episodes from egovernment-podcast.com
"""

import os
import re
import time
from pathlib import Path
from urllib.parse import urljoin, urlparse

import feedparser
import requests

# Try to import selenium for headless browsing
try:
    from selenium import webdriver
    from selenium.webdriver.chrome.options import Options
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    from selenium.common.exceptions import TimeoutException, WebDriverException
    SELENIUM_AVAILABLE = True
except ImportError:
    SELENIUM_AVAILABLE = False
    print("⚠️  Selenium not available. Install with: pip install selenium")

def clean_filename(filename):
    """Clean filename for filesystem compatibility"""
    # Remove or replace invalid characters
    filename = re.sub(r'[<>:"/\\|?*]', '-', filename)
    filename = re.sub(r'\s+', ' ', filename)  # Multiple spaces to single
    filename = filename.strip()
    return filename

def download_audio(url, filename, downloads_dir):
    """Download audio file with progress tracking and robust error handling"""
    try:
        print(f"Downloading: {filename}")
        print(f"URL: {url}")
        
        # Ensure downloads directory exists
        try:
            downloads_dir.mkdir(parents=True, exist_ok=True)
        except OSError as e:
            print(f"❌ Error creating downloads directory: {e}")
            return None
        
        filepath = downloads_dir / filename
        
        # Check if file already exists
        if filepath.exists():
            print(f"File already exists: {filepath}")
            return filepath
        
        # Download with timeout and error handling
        try:
            response = requests.get(url, stream=True, timeout=30)
            response.raise_for_status()
        except requests.RequestException as e:
            print(f"❌ Network error downloading {filename}: {e}")
            return None
        
        # Get file size for progress tracking
        total_size = int(response.headers.get('content-length', 0))
        downloaded_size = 0
        
        # Download with file operation error handling
        try:
            with open(filepath, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
                        downloaded_size += len(chunk)
                        
                        # Show progress
                        if total_size > 0:
                            progress = (downloaded_size / total_size) * 100
                            print(f"\rProgress: {progress:.1f}% ({downloaded_size // (1024*1024):.1f}MB / {total_size // (1024*1024):.1f}MB)", end='', flush=True)
            
            # Verify download completed successfully
            if filepath.exists() and filepath.stat().st_size > 0:
                print(f"\n✅ Successfully downloaded: {filepath}")
                return filepath
            else:
                print(f"\n❌ Download failed: File is empty or missing")
                # Clean up empty file
                if filepath.exists():
                    try:
                        filepath.unlink()
                    except OSError:
                        pass
                return None
                
        except IOError as e:
            print(f"\n❌ File I/O error downloading {filename}: {e}")
            # Clean up partial file
            if filepath.exists():
                try:
                    filepath.unlink()
                except OSError:
                    pass
            return None
        except OSError as e:
            print(f"\n❌ File system error downloading {filename}: {e}")
            return None
        
    except Exception as e:
        print(f"❌ Unexpected error downloading {filename}: {e}")
        return None

def extract_audio_with_browser(episode_url):
    """Extract audio URL using headless browser to execute JavaScript"""
    if not SELENIUM_AVAILABLE:
        return None
    
    try:
        # Set up Chrome options for headless browsing
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--window-size=1920,1080")
        
        # Initialize the driver
        driver = webdriver.Chrome(options=chrome_options)
        driver.set_page_load_timeout(30)
        
        # Load the page
        driver.get(episode_url)
        
        # Wait for the page to load and JavaScript to execute
        time.sleep(3)
        
        # Look for cdn.podseed.org URLs in the page source after JS execution
        page_source = driver.page_source
        
        # Pattern for podseed CDN URLs
        podseed_pattern = r'https://cdn\.podseed\.org/egovernment/[^"\'?\s]*\.mp4[^"\'?\s]*'
        matches = re.findall(podseed_pattern, page_source)
        
        driver.quit()
        
        if matches:
            # Return the first match (should be the audio file)
            return matches[0]
        
        return None
        
    except Exception as e:
        print(f"Browser extraction failed: {e}")
        if 'driver' in locals():
            try:
                driver.quit()
            except:
                pass
        return None

def try_direct_cdn_url(episode_url):
    """Try to construct direct CDN URL based on episode number"""
    try:
        # Extract episode number from URL
        episode_match = re.search(r'egov(\d+)', episode_url)
        if not episode_match:
            return None
        
        episode_num_str = episode_match.group(1)
        episode_int = int(episode_num_str)
        episode_num_padded = f"{episode_int:03d}"  # 009, 010, etc.
        
        # Different CDN patterns for different episode ranges
        potential_urls = []
        
        # Very recent episodes (220+): cdn.podseed.org with MP4
        if episode_int >= 220:
            potential_urls.extend([
                f"https://cdn.podseed.org/egovernment/egov{episode_num_str}.mp4",
                f"https://cdn.podseed.org/egovernment/egov{episode_num_str}.mp4?ptm_source=webplayer&ptm_context=episode&ptm_file=egov{episode_num_str}.mp4",
            ])
        
        # Medium episodes (around 150-219): master.podseed.org with MP4
        if 150 <= episode_int < 220:
            potential_urls.extend([
                f"https://master.podseed.org/egovernment/egov{episode_num_str}.mp4",
                f"https://cdn.podseed.org/egovernment/egov{episode_num_str}.mp4",
                f"https://master.podseed.org/egovernment/egov{episode_num_str}.mp3",
                f"https://cdn.podseed.org/egovernment/egov{episode_num_str}.mp3",
            ])
        
        # Older episodes: master.podseed.org with different formats
        if episode_int < 150:
            potential_urls.extend([
                f"https://master.podseed.org/egovernment/egov{episode_num_padded}_aac.m4a",
                f"https://master.podseed.org/egovernment/egov{episode_num_str}_aac.m4a",
                f"https://master.podseed.org/egovernment/egov{episode_num_padded}.m4a",
                f"https://master.podseed.org/egovernment/egov{episode_num_str}.m4a",
                f"https://master.podseed.org/egovernment/egov{episode_num_padded}.mp3",
                f"https://master.podseed.org/egovernment/egov{episode_num_str}.mp3",
            ])
        
        # Test each URL
        for url in potential_urls:
            if test_audio_url(url):
                return url
        
        return None
        
    except Exception as e:
        print(f"Direct URL construction failed: {e}")
        return None

def extract_audio_from_page(episode_url):
    """Extract audio URL from individual episode page"""
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1'
        }
        
        response = requests.get(episode_url, headers=headers, timeout=10)
        response.raise_for_status()
        
        # Look for podseed.org URLs in the page content - both cdn and master
        podseed_patterns = [
            r'https://cdn\.podseed\.org/egovernment/[^"\'?\s&]*\.(mp4|mp3|m4a)[^"\'?\s]*',
            r'https://master\.podseed\.org/egovernment/[^"\'?\s&]*\.(mp4|mp3|m4a)[^"\'?\s]*'
        ]
        
        audio_urls = []
        for pattern in podseed_patterns:
            matches = re.findall(pattern, response.text)
            audio_urls.extend(matches)
        
        if audio_urls:
            # Prefer MP4 files, then M4A, then MP3
            mp4_matches = [m for m in audio_urls if '.mp4' in m]
            if mp4_matches:
                return mp4_matches[0]
            
            m4a_matches = [m for m in audio_urls if '.m4a' in m]
            if m4a_matches:
                return m4a_matches[0]
            
            return audio_urls[0]
        
        # Alternative: look for any audio file URLs
        audio_patterns = [
            r'https://[^"\'?\s&]+\.mp4',
            r'https://[^"\'?\s&]+\.mp3',
            r'https://[^"\'?\s&]+\.m4a'
        ]
        
        for pattern in audio_patterns:
            matches = re.findall(pattern, response.text)
            if matches:
                # Clean the URL
                url = matches[0]
                if '?' in url:
                    url = url.split('?')[0]
                return url
        
        return None
        
    except Exception as e:
        print(f"Error extracting audio from {episode_url}: {e}")
        return None

def get_episodes_from_rss():
    """Get episodes from RSS feed"""
    rss_url = "https://egovernment-podcast.com/feed/mp3/"
    
    try:
        print(f"Fetching RSS feed: {rss_url}")
        feed = feedparser.parse(rss_url)
        
        if feed.bozo:
            print("Warning: RSS feed has parsing issues")
        
        episodes = []
        
        for entry in feed.entries:
            episode_data = {
                'title': entry.title,
                'link': entry.link,
                'published': entry.get('published', ''),
                'description': entry.get('description', ''),
                'audio_url': None
            }
            
            # Try to get audio URL from enclosures
            if hasattr(entry, 'enclosures') and entry.enclosures:
                for enclosure in entry.enclosures:
                    if enclosure.type and 'audio' in enclosure.type:
                        episode_data['audio_url'] = enclosure.href
                        break
            
            episodes.append(episode_data)
        
        print(f"Found {len(episodes)} episodes in RSS feed")
        return episodes
        
    except Exception as e:
        print(f"Error fetching RSS feed: {e}")
        return []

def get_episodes_from_overview_page():
    """Get episodes from the episode overview page"""
    overview_url = "https://egovernment-podcast.com/episodenuebersicht/"
    
    try:
        print(f"Fetching episode overview: {overview_url}")
        response = requests.get(overview_url, timeout=10)
        response.raise_for_status()
        
        # Look for episode links in the overview page
        # Pattern: links to individual episode pages
        episode_pattern = r'href="(https://egovernment-podcast\.com/egov\d+-[^"]+/)"'
        matches = re.findall(episode_pattern, response.text)
        
        episodes = []
        for match in matches:
            # Extract episode number from URL
            episode_num_match = re.search(r'egov(\d+)', match)
            episode_num = episode_num_match.group(1) if episode_num_match else "unknown"
            
            episodes.append({
                'title': f"Episode {episode_num}",
                'link': match,
                'episode_number': episode_num,
                'audio_url': None
            })
        
        print(f"Found {len(episodes)} episode links in overview page")
        return episodes
        
    except Exception as e:
        print(f"Error fetching episode overview: {e}")
        return []

def generate_potential_audio_urls(episode_number):
    """Generate potential audio URLs based on the pattern we observed"""
    base_url = "https://cdn.podseed.org/egovernment/"
    
    # Try different formats based on the pattern observed
    potential_urls = [
        f"{base_url}egov{episode_number}.mp4",
        f"{base_url}egov{episode_number}.mp3",
        f"{base_url}egov{episode_number}.m4a"
    ]
    
    return potential_urls

def test_audio_url(url):
    """Test if an audio URL is accessible"""
    try:
        response = requests.head(url, timeout=5)
        return response.status_code == 200
    except:
        return False

def main():
    """Main scraper function"""
    print("🎧 eGovernment Podcast Scraper")
    print("=" * 50)
    
    # Create downloads directory
    downloads_dir = Path("downloads_egov")
    downloads_dir.mkdir(exist_ok=True)
    
    # Strategy 1: Try RSS feed first
    episodes = get_episodes_from_rss()
    
    # Strategy 2: If RSS doesn't have enough episodes, try overview page
    if len(episodes) < 10:  # RSS might be limited
        print("RSS feed seems limited, trying episode overview page...")
        overview_episodes = get_episodes_from_overview_page()
        
        if overview_episodes:
            episodes = overview_episodes
    
    # Strategy 3: If we still don't have many episodes, try systematic approach
    if len(episodes) < 50:
        print("Trying systematic approach for episodes 1-220...")
        episodes = []
        
        for i in range(1, 221):  # Episodes 1-220
            episode_num = str(i).zfill(3) if i < 100 else str(i)  # Pad with zeros if needed
            
            # Try different episode number formats
            for num_format in [str(i), str(i).zfill(3)]:
                potential_urls = generate_potential_audio_urls(num_format)
                
                for url in potential_urls:
                    if test_audio_url(url):
                        episodes.append({
                            'title': f"eGovernment Podcast Episode {i}",
                            'episode_number': str(i),
                            'audio_url': url,
                            'link': f"https://egovernment-podcast.com/egov{i}/"
                        })
                        print(f"✅ Found Episode {i}: {url}")
                        break
                else:
                    continue
                break
    
    if not episodes:
        print("❌ No episodes found!")
        return
    
    print(f"\n📊 Found {len(episodes)} episodes total")
    
    # Download episodes
    successful_downloads = 0
    failed_downloads = 0
    
    for i, episode in enumerate(episodes, 1):
        print(f"\n--- Episode {i}/{len(episodes)} ---")
        
        # Get audio URL using multiple methods
        audio_url = None
        episode_link = episode.get('link')
        
        if episode_link:
            print(f"Finding audio URL for: {episode['title']}")
            print(f"Episode page: {episode_link}")
            
            # Method 1: Try direct CDN URL construction (fastest)
            print("  → Trying direct CDN URL...")
            audio_url = try_direct_cdn_url(episode_link)
            
            # Method 2: Try headless browser if available and direct method failed
            if not audio_url and SELENIUM_AVAILABLE:
                print("  → Trying headless browser...")
                audio_url = extract_audio_with_browser(episode_link)
            
            # Method 3: Fallback to static HTML parsing
            if not audio_url:
                print("  → Trying static HTML parsing...")
                audio_url = extract_audio_from_page(episode_link)
        
        # Last resort: RSS feed URL if extraction failed
        if not audio_url:
            rss_audio_url = episode.get('audio_url')
            if rss_audio_url and 'podlove' not in rss_audio_url:
                print("  → Using RSS feed URL...")
                audio_url = rss_audio_url
        
        if not audio_url:
            print(f"❌ No audio URL found for: {episode['title']}")
            failed_downloads += 1
            continue
        
        print(f"✅ Found audio URL: {audio_url}")
        
        # Clean filename
        title = episode.get('title', f"Episode {episode.get('episode_number', i)}")
        filename = clean_filename(title)
        
        # Add episode number if not in title
        if 'episode_number' in episode and episode['episode_number'] not in filename:
            filename = f"egov{episode['episode_number']} - {filename}"
        
        # Get file extension from URL
        parsed_url = urlparse(audio_url)
        ext = os.path.splitext(parsed_url.path)[1] or '.mp4'
        filename = f"{filename}{ext}"
        
        # Check if already downloaded
        filepath = downloads_dir / filename
        if filepath.exists():
            print(f"⏭️  Already exists: {filename}")
            continue
        
        # Download
        result = download_audio(audio_url, filename, downloads_dir)
        
        if result:
            successful_downloads += 1
        else:
            failed_downloads += 1
        
        # Be respectful - small delay between downloads
        time.sleep(2)
    
    print(f"\n🎉 Download Summary:")
    print(f"✅ Successful: {successful_downloads}")
    print(f"❌ Failed: {failed_downloads}")
    print(f"📁 Files saved in: {downloads_dir}")
    
    if successful_downloads > 0:
        print(f"\n🎧 Ready to transcribe! You can now:")
        print(f"   1. Move files to 'downloads' folder: mv {downloads_dir}/*.mp4 downloads/")
        print(f"   2. Run transcription: python transcribe.py --all")

if __name__ == "__main__":
    main()