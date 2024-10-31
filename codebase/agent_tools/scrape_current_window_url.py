import pygetwindow as gw
import pyperclip
import keyboard
from .search_manager import WebContentExtractor, SearchManager, SearchProvider, SearchAPI, DuckDuckGoSearchProvider
import datetime
import os
import psutil

def get_edge_url_with_psutil():
    for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
        if proc.info['name'] == 'msedge.exe':
            cmdline = proc.info['cmdline']
            for arg in cmdline:
                if arg.startswith('https://'):
                    return arg

def capture_url():
    # Get the active Edge window
    edge_window = gw.getActiveWindow()

    if "Microsoft Edge" not in edge_window.title:
        return None
    # Get the URL from the clipboard
    url = pyperclip.paste()

    if not url.startswith("http"):
        # If the clipboard doesn't contain a URL, try to get the URL from the Edge window title
        url = edge_window.title.split(" - ")[0]
    if not url.startswith("https://"):
        url = get_edge_url_with_psutil()
        
    return url
    
def save_to_file(url, content):
    """Save the URL and content to a new text file with a timestamp on the desktop."""
    timestamp = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
    desktop = os.path.join(os.path.join(os.environ['USERPROFILE']), 'Desktop')
    with open(os.path.join(desktop, f"Scraped_URL_{timestamp}.txt"), "w") as f:
        f.write(f"{url}\n{content}")


url = capture_url()
content_extractor = WebContentExtractor()
content = content_extractor.extract_content(url)
save_to_file(url, content)
print(f"Captured URL: {url}")
print(f"Captured content: {content}")
input("Press Enter to exit...")