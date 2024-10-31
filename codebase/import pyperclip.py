import pyperclip
from search_manager import WebContentExtractor
# Grab the text from the clipboard
url = pyperclip.paste()
content = WebContentExtractor.extract_content(url)
# Print the URL to verify
print(f"The content from: {url}\n{content}")