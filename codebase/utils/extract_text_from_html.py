import requests
from bs4 import BeautifulSoup
import re
import gzip
import io
from selenium import webdriver
from selenium.webdriver.edge.options import Options
from selenium.webdriver.edge.service import Service
from webdriver_manager.microsoft import EdgeChromiumDriverManager

def extract_text_from_html(url, extract_outside_main=False, extract_comments=False):
    # Request with headers
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.9',
        'Accept-Encoding': 'gzip, deflate, br',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
        'Cache-Control': 'max-age=0',
        'DNT': '1',
    }
    response = requests.get(url, headers=headers)

    content_type = response.headers.get('Content-Type', '')
    if 'text/html' not in content_type:
        raise ValueError(f"Expected HTML, but received {content_type}")

    # Handle gzip or plain text
    if response.headers.get('Content-Encoding') == 'gzip':
        try:
            html_content = gzip.decompress(response.content).decode('utf-8')
        except (gzip.BadGzipFile, OSError):
            html_content = response.text
    else:
        html_content = response.text

    soup = BeautifulSoup(html_content, 'html.parser')
    main_content = soup.find(['div', 'main', 'article'], class_=re.compile(r'(main|content)', re.I)) or soup.body
    main_text = main_content.get_text(separator=' ', strip=True) if main_content else ''

    # Fall back to Selenium if main_text is invalid
    if len(main_text) < 200 and ('cookies' in main_text.lower() or 'javascript' in main_text.lower() or len(main_text) < 10):
        main_text = extract_with_selenium(url)

    # Optionally extract outside text and comments
    outside_text = extract_outside_main_content(soup, main_content) if extract_outside_main else ''
    comments = extract_comments_section(soup) if extract_comments else ''

    # Combine extracted content
    return clean_text(f"{main_text} {outside_text} {comments}".strip())

def extract_outside_main_content(soup, main_content):
    outside_tags = soup.find_all(['p', 'h1', 'h2', 'h3', 'h4'])
    return ' '.join(tag.get_text(strip=True) for tag in outside_tags if tag not in main_content.descendants)

def extract_comments_section(soup):
    comment_section = soup.find('div', class_='comments')
    return comment_section.get_text(separator=' ', strip=True) if comment_section else ''

def extract_with_selenium(url):
    # Set up Edge options for headless browsing with human-like behavior
    edge_options = Options()
    edge_options.add_argument("--headless")
    edge_options.add_argument("--disable-gpu")
    edge_options.add_argument("--no-sandbox")

    # Human-like headers and user-agent simulation
    edge_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")
    edge_options.add_argument("accept=text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8")
    edge_options.add_argument("accept-language=en-US,en;q=0.9")
    edge_options.add_argument("accept-encoding=gzip, deflate, br")

    # Set up the WebDriver for Edge
    service = Service(EdgeChromiumDriverManager().install())
    driver = webdriver.Edge(service=service, options=edge_options)

    # Load the page with Selenium
    driver.get(url)

    # Wait for JavaScript to execute
    driver.implicitly_wait(10)

    # Get the page source after JavaScript execution
    html_content = driver.page_source

    # Close the browser
    driver.quit()

    # Parse the HTML content with BeautifulSoup
    soup = BeautifulSoup(html_content, 'html.parser')

    # Extract main content
    main_content = soup.find(['div', 'main', 'article'], class_=re.compile(r'(main|content)', re.I)) or soup.body
    return main_content.get_text(separator=' ', strip=True) if main_content else ''


def clean_text(text):
    # Remove HTML tags
    text = re.sub(r'<[^>]+>', '', text)

    # Remove duplicate/multiple adjacent new lines and white space characters
    text = re.sub(r'\s+', ' ', text)

    # Remove any symbols other than punctuation and dollar signs
    text = re.sub(r'[^\w\s.,$]', '', text)

    return text.strip()


# Example usage
url = 'https://www.newsweek.com/tony-hinchcliffe-followers-puerto-rico-trump-1975892'
extracted_text = extract_text_from_html(url, extract_outside_main=False, extract_comments=False)
print(extracted_text)

with open('extracted_text.txt', 'w', encoding='utf-8') as f:
    f.write(extracted_text)



import random
import time
import string
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.edge.service import Service
from selenium.webdriver.edge.options import Options
from webdriver_manager.microsoft import EdgeChromiumDriverManager

# List of user agents to randomize from
USER_AGENTS = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Safari/537.36',
    'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
    'Mozilla/5.0 (iPhone; CPU iPhone OS 14_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0 Mobile/15E148 Safari/604.1'
]

# Random User-Agent generator
def random_user_agent():
    return random.choice(USER_AGENTS)

# Random delay function
def random_delay(min_delay=1, max_delay=5):
    time.sleep(random.uniform(min_delay, max_delay))

# Simulate scrolling through the page
def human_like_scroll(driver, scroll_times=5):
    for i in range(scroll_times):
        # Scroll by random amounts between 300 and 800 pixels
        scroll_distance = random.randint(300, 800)
        driver.execute_script(f"window.scrollBy(0, {scroll_distance});")
        random_delay(1, 3)  # Random delay between scrolls

# Simulate mouse movements
def human_like_mouse_move(driver):
    action = ActionChains(driver)
    # Move to random points on the page
    for _ in range(random.randint(5, 10)):
        x_offset = random.randint(0, 1000)
        y_offset = random.randint(0, 1000)
        action.move_by_offset(x_offset, y_offset).perform()
        random_delay(0.5, 1.5)

# Random browser window size
def random_window_size(driver):
    width = random.randint(800, 1600)
    height = random.randint(600, 1200)
    driver.set_window_size(width, height)

# Simulate typing behavior
def human_like_typing(element, text):
    for char in text:
        element.send_keys(char)
        random_delay(0.1, 0.3)

def extract_with_selenium(url):
    try:
        # Set up Edge options for headless browsing with human-like behavior
        edge_options = Options()
        edge_options.add_argument("--disable-gpu")
        edge_options.add_argument("--no-sandbox")
        
        # Randomize User-Agent
        user_agent = random_user_agent()
        edge_options.add_argument(f"user-agent={user_agent}")

        # Disable headless for more human-like browsing (optional, headless makes detection easier)
        # edge_options.add_argument("--headless")  # Uncomment this to enable headless mode

        # Set up the WebDriver for Edge
        service = Service(EdgeChromiumDriverManager().install())
        driver = webdriver.Edge(service=service, options=edge_options)

        # Randomize window size and position
        random_window_size(driver)
        driver.set_window_position(random.randint(0, 100), random.randint(0, 100))

        # Load the page
        driver.get(url)

        # Simulate human-like browsing
        human_like_scroll(driver, scroll_times=random.randint(3, 7))
        human_like_mouse_move(driver)
        
        # Simulate typing in a search box (if needed, depends on the page interaction)
        # search_box = driver.find_element_by_name('q')  # Example of interacting with a search box
        # human_like_typing(search_box, 'search query here')

        # Wait for JavaScript to execute
        driver.implicitly_wait(random.randint(5, 10))

        # Get the page source after JavaScript execution
        html_content = driver.page_source

        # Close the browser
        driver.quit()

        # Return the page content
        return html_content

    except Exception as e:
        print(f"Selenium error: {e}")
        return ''

# Example usage of the function
url = 'https://www.theatlantic.com/education/archive/2015/10/complex-academic-writing/412255/'
html_content = extract_with_selenium(url)
print(html_content)