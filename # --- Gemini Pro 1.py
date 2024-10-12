# --- Gemini Pro 1.5 latest base class ---

# Import Google-GenerativeAI and set up a conversational chat with Gemini Pro 1.5 latest
from google_generativeai import GoogleGenerativeAI

client = GoogleGenerativeAI()    # Initialize the client with your API key

# Start the conversation
client.converse()
