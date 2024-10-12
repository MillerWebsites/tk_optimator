from collections import deque
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

# API Keys
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
GROQ_API_KEY = os.getenv('GROQ_API_KEY')
GOOGLE_CUSTOM_SEARCH_API_KEY = os.getenv('GOOGLE_CUSTOM_SEARCH_API_KEY')
GOOGLE_CUSTOM_SEARCH_ENGINE_ID = os.getenv('GOOGLE_CUSTOM_SEARCH_ENGINE_ID')
BRAVE_SEARCH_API_KEY = os.getenv('BRAVE_SEARCH_API_KEY')
HF_TOKEN = os.getenv('HF_TOKEN')

# Constants
MAX_CHAT_HISTORY_LENGTH = 14
MAX_RETRIES = 3
BACKOFF_FACTOR = 2
MAX_TRUNCATE_LENGTH = 5000  # Length of truncated chat_log items
MAX_INVALID_ATTEMPTS = 3
MAX_SEARCH_RESULTS = 8
MAX_CONTENT_LENGTH = 15000  # Maximum number of characters to extract from each webpage
TIMEOUT = 5
MAX_SEARCH_QUERIES_PER_REQUEST = 2

# Safety Settings
SAFETY_SETTINGS = [
    {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_NONE"},
    {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_NONE"},
    {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_NONE"},
    {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_NONE"},
]

# LLM Model Configuration
LLM_PROVIDER = "gemini"  # Default provider -  You can change this to "openai" if needed
OPENAI_API_KEY = "YOUR_OPENAI_API_KEY"
GEMINI_PRO_MODEL = "models/gemini-1.5-pro-latest"
GEMINI_FLASH_MODEL = "models/gemini-1.5-flash-latest" 
# Add settings for other providers as needed