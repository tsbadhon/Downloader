#!/usr/bin/env python3

import subprocess
import sys
import shutil
import json

def check_dependency(name):
    return shutil.which(name) is not None

def install_ytdlp():
    try:
        print("Installing/updating yt-dlp...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "--upgrade", "yt-dlp"])
    except subprocess.CalledProcessError:
        print("Failed to install yt-dlp. Please check your internet connection.")
        sys.exit(1)

def get_available_formats(url):
    try:
        result = subprocess.run(
            ["yt-dlp", "--list-formats", url],
            capture_output=True,
            text=True,
            check=True
        )
        return result.stdout
    except subprocess.CalledProcessError:
        return None

def download_video(url):
    # TikTok specific headers to avoid detection
    custom_opts = [
        "--referer", "https://www.tiktok.com/",
        "--user-agent", "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        "-o", "/storage/emulated/0/YouTube/Tiktok/%(title)s.%(ext)s"  # Set download location
    ]
    
    # Try different format options in order of preference
    format_options = [
        ["-f", "bestvideo+bestaudio", "--merge-output-format", "mp4"],
        ["-f", "best"],
        ["-f", "bv+ba"],
        ["-f", "mp4"]
    ]
    
    for fmt in format_options:
        try:
            print(f"\nTrying format: {' '.join(fmt)}")
            subprocess.run(
                ["yt-dlp"] + custom_opts + fmt + [url],
                check=True
            )
            print("\nDownload completed successfully!")
            return True
        except subprocess.CalledProcessError:
            continue
    
    return False

def main():
    # Check and install yt-dlp if needed
    if not check_dependency("yt-dlp"):
        install_ytdlp()
    
    # Check for ffmpeg
    if not check_dependency("ffmpeg"):
        print("\nWarning: ffmpeg is not installed. Video merging might fail.")
        print("Install it in Termux with: pkg install ffmpeg\n")
    
    # Get TikTok URL
    url = input("Paste TikTok video URL: ").strip()
    
    # Try to download
    if not download_video(url):
        print("\nAll download attempts failed. Possible reasons:")
        print("1. URL is invalid or video is private")
        print("2. TikTok is blocking downloads from your region")
        print("3. Server-side restrictions")
        
        # Show available formats if possible
        print("\nChecking available formats...")
        formats = get_available_formats(url)
        if formats:
            print("\nAvailable formats:\n")
            print(formats)
            print("\nYou can try manually specifying a format with:")
            print(f"yt-dlp -f FORMAT_ID {url}")
        else:
            print("Could not retrieve format information")

if __name__ == "__main__":
    main()