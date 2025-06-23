import feedparser
import requests
import os
import re
from bs4 import BeautifulSoup

def find_audio_urls_in_page(url):
    """Extract potential audio URLs from a webpage"""
    try:
        response = requests.get(url)
        response.raise_for_status()
        
        # Look for direct audio URLs in the HTML
        audio_urls = []
        
        # Pattern 1: Direct .mp3 URLs (like the podbean link you found)
        mp3_pattern = r'https://[^\s"\'<>]+\.mp3(?:\?[^\s"\'<>]*)?'
        mp3_urls = re.findall(mp3_pattern, response.text)
        audio_urls.extend(mp3_urls)
        
        # Pattern 2: Other audio formats
        audio_pattern = r'https://[^\s"\'<>]+\.(m4a|wav|ogg)(?:\?[^\s"\'<>]*)?'
        other_audio_urls = re.findall(audio_pattern, response.text)
        audio_urls.extend(other_audio_urls)
        
        # Pattern 3: Podbean URLs specifically (more comprehensive)
        podbean_pattern = r'https://[^\s"\'<>]*podbean\.com[^\s"\'<>]*\.(mp3|m4a|wav|ogg)(?:\?[^\s"\'<>]*)?'
        podbean_urls = re.findall(podbean_pattern, response.text)
        audio_urls.extend(podbean_urls)
        
        return list(set(audio_urls))  # Remove duplicates
        
    except Exception as e:
        print(f"Error fetching page {url}: {e}")
        return []

def main():
    # Known podcast page URL
    PODCAST_PAGE = "https://www.politicaexterior.com/podcasts/la-politica-exterior-de-la-union-europea/"
    
    print("Searching for podcast audio files...")
    
    # First, try to find audio URLs directly from the podcast page
    audio_urls = find_audio_urls_in_page(PODCAST_PAGE)
    
    if audio_urls:
        print(f"Found {len(audio_urls)} potential audio URLs:")
        for i, url in enumerate(audio_urls, 1):
            print(f"{i}. {url}")
        
        # Use the first audio URL found
        audio_url = audio_urls[0]
        print(f"\nUsing: {audio_url}")
        
        # Create downloads folder
        downloads_folder = "downloads"
        os.makedirs(downloads_folder, exist_ok=True)
        
        # Download audio file
        try:
            print("Downloading audio file...")
            resp = requests.get(audio_url, stream=True)
            resp.raise_for_status()
            
            # Extract filename from URL
            filename = audio_url.split("/")[-1].split("?")[0]  # Remove query parameters
            if not filename or not filename.endswith(('.mp3', '.m4a', '.wav', '.ogg')):
                filename = f"podcast_episode.mp3"
                
            filepath = os.path.join(downloads_folder, filename)
            
            with open(filepath, "wb") as f:
                for chunk in resp.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
            
            print(f"Successfully saved: {filepath}")
            
        except requests.RequestException as e:
            print(f"ERROR downloading audio: {e}")
        except Exception as e:
            print(f"ERROR: {e}")
    
    else:
        print("No audio URLs found on the podcast page.")
        print("The audio might be loaded dynamically via JavaScript.")
        print("\nTrying RSS feed as fallback...")
        
        # Fallback to RSS feed approach
        RSS_URL = "https://www.politicaexterior.com/feed/"
        feed = feedparser.parse(RSS_URL)
        
        if feed.entries:
            print(f"Found {len(feed.entries)} articles in RSS feed")
            print("\nLatest articles:")
            for i, entry in enumerate(feed.entries[:5]):
                print(f"{i+1}. {entry.title}")
                print(f"   Link: {entry.link}")
                
                # Try to find audio in individual article pages
                if "podcast" in entry.link.lower():
                    print(f"   Checking podcast page for audio...")
                    page_audio_urls = find_audio_urls_in_page(entry.link)
                    if page_audio_urls:
                        print(f"   Found audio: {page_audio_urls[0]}")
        else:
            print("No entries found in RSS feed either.")

if __name__ == "__main__":
    main()
