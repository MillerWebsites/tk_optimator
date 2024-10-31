import os
import importlib

# Get the absolute path to the script's directory
script_dir = os.path.dirname(__file__)

# Construct the absolute path to the models module
models_path = os.path.join(script_dir, '../models.py')

# Import the ModelManager class from the models module
spec = importlib.util.spec_from_file_location("models", models_path)
models = importlib.util.module_from_spec(spec)
spec.loader.exec_module(models)

# Get the ModelManager class
ModelManager = models.ModelManager

# Rest of the code...
model_manager = ModelManager()
from youtube_comment_downloader import YoutubeCommentDownloader
def fetch_comments(video_url):
    downloader = YoutubeCommentDownloader()
    return [
        comment['text']
        for comment in downloader.get_comments_from_url(video_url)
    ]

def save_comments_to_file(comments, filename):
    with open(filename, 'w', encoding='utf-8') as file:
        for comment in comments:
            file.write(comment + '\n')

def main():
    url = input("Enter youtube URL")
    comments = fetch_comments(url)
    save_comments_to_file(comments, 'comments.txt')
    prompt = f"Summarize and extract all insights from the following comment sections for a Youtube Video: \n {comments}"
    response = model_manager.generate_response(prompt)
    for comment in comments:
        print(comment)
    print(response.text)

if __name__ == '__main__':
    main()