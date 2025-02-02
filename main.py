import logging
import tkinter as tk
from tkinter import ttk, scrolledtext, Menu, filedialog, simpledialog, messagebox

from config import GEMINI_API_KEY, MAX_SEARCH_RESULTS
from models import ModelManager, ModelFactory, LLMProvider, GeminiProvider, generate_convo_context
from agents import AgentManager, ToolManager
import search_manager
from search_manager import SearchManager, SearchProvider, SearchAPI, DuckDuckGoSearchProvider, SearchProvider, WebContentExtractor
from gui import App

# Set up logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


class AIAssistantApp:
    def __init__(self):
        self.model_manager = ModelManager(search_enabled=True)
        self.agent_manager = AgentManager()
        google_api = SearchProvider.create_provider("google")
        duckduckgo_provider = SearchProvider.create_provider("duckduckgo")
        self.search_manager = SearchManager([google_api], duckduckgo_provider)

        # Set LLM provider
        self.model_manager.set_provider("gemini", GEMINI_API_KEY)

        # Register tools
        self.tool_manager = ToolManager()
        self.tool_manager.register_tool("search_and_scrape", self.search_manager.search)
        self.tool_manager.register_tool("foia_search", foia_search)

        self.app = App(self.search_manager, self.model_manager, self.agent_manager, self.tool_manager)  # Pass tool_manager to App

    def run(self):
        try:
            self.app.mainloop()
        except Exception as e:
            logger.error(f"Unexpected error in main loop: {e}")
        finally:
            logger.info("Application closed")


def main():
    try:
        app = AIAssistantApp()
        app.run()
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        messagebox.showerror("Fatal Error", f"An unexpected error occurred: {e}")


if __name__ == "__main__":
    main()
