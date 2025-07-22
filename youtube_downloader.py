import sys
import yt_dlp

def main():
    if len(sys.argv) < 2:
        print("Usage: python youtube_downloader.py <YouTube URL>")
        sys.exit(1)
    url = sys.argv[1]
    ydl_opts = {
        'outtmpl': '%(title)s.%(ext)s',  # Save as "<title>.<ext>" in current dir
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])

if __name__ == "__main__":
    main() 