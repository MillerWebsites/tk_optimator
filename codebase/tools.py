"""Module for defining and managing external tools for the AI assistant."""
import requests
from bs4 import BeautifulSoup
import html2text
import random
import utils

from search_manager import WebContentExtractor, SearchManager  # Import SearchManager
from agent_tools import fetch_latest_arxiv_papers

def foia_search(query: str) -> str:
    """Searches FOIA.gov for the given query and returns the text content.

    Args:
        query (str): The search query.

    Returns:
        str: The text content of the search results from FOIA.gov. 
    """
    url = f"https://search.foia.gov/search?utf8=%E2%9C%93&m=true&affiliate=foia.gov&query={query.replace(' ', '+')}"
    web_content_extractor = WebContentExtractor()
    headers = {
        'User-Agent': random.choice(web_content_extractor.USER_AGENTS),
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.9',
        'Accept-Encoding': 'gzip, deflate, br',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
        'Cache-Control': 'max-age=0',
        'DNT': '1',
    }
    response = requests.get(url, headers=headers, timeout=web_content_extractor.TIMEOUT)
    response.raise_for_status()
    html_content = response.content.decode('utf-8')
    soup = BeautifulSoup(html_content, 'html.parser')

    for script in soup(["script", "style"]):
        script.decompose()

    return html2text.html2text(html_content)


def web_search(search_manager: SearchManager, query: str, num_results: int = 10) -> str:
    """Performs a web search using the provided SearchManager.

    Args:
        search_manager (SearchManager): An instance of the SearchManager class.
        query (str): The search query.
        num_results (int, optional): The maximum number of results to return. Defaults to 3.

    Returns:
        str: A formatted string containing the search results.
    """
    results = search_manager.search(query, num_results)
    return "\n\n".join(
        [
            f"**{result['title']}** ({result['url']})\n{result['snippet']}\n{result['content'][:50000]}"
            for result in results
        ]
    )

class FetchRecentArxivPapersbyTopic:
    def __init__(self):
        pass

    def execute(self, topic):
        papers = fetch_latest_arxiv_papers(topic)
        return "\n\n".join([f"Title: {paper['title']}\nAuthors: {', '.join(paper['authors'])}\nPublished: {paper['published']}\nSummary: {paper['summary']}\nLink: {paper['link']}\n" for paper in papers])