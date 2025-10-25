import os
import argparse
import requests
from urllib.parse import urljoin, urlparse, unquote
from bs4 import BeautifulSoup
import warnings

VIDEO_EXTS = [".mp4", ".mkv", ".avi", ".mov", ".flv", ".webm", ".wmv"]
USER_AGENT = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
              "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0 Safari/537.36")
REQUEST_TIMEOUT = 15

visited = set()

def normalize_base_url(url):
    return url if url.endswith("/") else url + "/"

def get_folder_name_from_url(url):
    path = unquote(urlparse(url).path)
    parts = [p for p in path.strip("/").split("/") if p]
    return parts[-1] if parts else "root"

def safe_folder_name(name):
    return name.replace(" ", "_").replace("-", "_").replace("%20", "_")

def looks_like_video(href, full_url):
    low = href.lower().split("?", 1)[0]
    for ext in VIDEO_EXTS:
        if low.endswith(ext):
            return True
    path = urlparse(full_url).path.lower()
    return any(path.endswith(ext) for ext in VIDEO_EXTS)

def looks_like_folder(href, full_url, base_url):
    if href.endswith("/"):
        return True
    last = os.path.basename(urlparse(full_url).path.rstrip("/"))
    if "." not in last:
        base_path = urlparse(base_url).path.rstrip("/")
        full_path = urlparse(full_url).path.rstrip("/")
        return full_path.startswith(base_path + "/")
    return False

def fetch_html(session, url, verify, debug=False):
    try:
        r = session.get(url, timeout=REQUEST_TIMEOUT, verify=verify)
        if debug:
            print(f"Fetched: {url} (status {r.status_code})")
        r.raise_for_status()
        return r.text
    except Exception as e:
        if debug:
            print(f"❌ Error fetching {url}: {e}")
        return None

def parse_links(html, base_url):
    soup = BeautifulSoup(html, "html.parser")
    return [(a["href"].strip(), urljoin(base_url, a["href"].strip()))
            for a in soup.find_all("a", href=True)
            if a["href"].strip() not in ("../", "..")]

def get_video_folder_relative(base_url, video_url):
    base_parts = urlparse(base_url).path.strip("/").split("/")
    video_parts = urlparse(video_url).path.strip("/").split("/")
    if len(video_parts) > len(base_parts):
        subfolder_parts = video_parts[:len(video_parts)-1]
        relative_parts = subfolder_parts[len(base_parts):]
        return safe_folder_name("_".join(relative_parts)) or "root"
    return "root"

def crawl_down(session, base_url, current_url, collected_dict, verify, debug=False):
    if not current_url.startswith(base_url):
        return
    norm = current_url.rstrip("/")
    if norm in visited:
        return
    visited.add(norm)

    if debug:
        print(f"\n🔍 Scanning: {current_url}")

    html = fetch_html(session, current_url, verify, debug)
    if html is None:
        return

    links = parse_links(html, current_url)
    for href, full in links:
        if not full.startswith(base_url):
            continue

        if looks_like_video(href, full):
            folder_key = get_video_folder_relative(base_url, full)
            collected_dict.setdefault(folder_key, []).append(full)
            if debug:
                print(f"  🎞 Video in [{folder_key}]: {full}")
        elif looks_like_folder(href, full, base_url):
            folder_url = full if full.endswith("/") else full + "/"
            if debug:
                print(f"  📂 Folder: {folder_url}")
            crawl_down(session, base_url, folder_url, collected_dict, verify, debug)
        else:
            if debug:
                print(f"  ⛔ Skipped: {full}")

def save_playlists(collected_dict, output_root):
    if not collected_dict:
        print("⚠️ No video links found.")
        return
    for folder, links in collected_dict.items():
        folder_path = os.path.join(output_root, folder)
        os.makedirs(folder_path, exist_ok=True)
        m3u_path = os.path.join(folder_path, folder + ".m3u")
        with open(m3u_path, "w", encoding="utf-8") as f:
            for link in links:
                f.write(link + "\n")
        print(f"✅ Saved {len(links)} videos → {m3u_path}")

def main():
    parser = argparse.ArgumentParser(description="Recursively collect video links by folder.")
    parser.add_argument("--url", "-u", required=False, help="Starting folder URL")
    parser.add_argument("--output", "-o", default="/storage/emulated/0/Stream", help="Base output folder")
    parser.add_argument("--insecure", action="store_true", help="Disable SSL verification (for invalid certs)")
    parser.add_argument("--debug", action="store_true", help="Show debug output")
    args = parser.parse_args()

    if not args.url:
        args.url = input("📥 Enter the URL of the series: ").strip()

    base_url = normalize_base_url(args.url)
    root_folder = safe_folder_name(get_folder_name_from_url(base_url))
    output_dir = os.path.join(args.output, root_folder)

    if args.insecure:
        warnings.filterwarnings("ignore", message="Unverified HTTPS request")
        print("⚠️ SSL verification is disabled. Use only with trusted sources.")

    session = requests.Session()
    session.headers.update({"User-Agent": USER_AGENT})

    collected = {}
    crawl_down(session, base_url, base_url, collected, not args.insecure, args.debug)
    save_playlists(collected, output_dir)

if __name__ == "__main__":
    main()