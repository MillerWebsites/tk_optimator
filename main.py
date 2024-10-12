import logging
import tkinter as tk
from tkinter import ttk, scrolledtext, Menu, filedialog, simpledialog, messagebox
from functools import partial

from config import GEMINI_API_KEY, MAX_SEARCH_RESULTS, LLM_PROVIDER, OPENAI_API_KEY, GEMINI_PRO_MODEL, GEMINI_FLASH_MODEL
from models import ModelManager
from agents import AgentManager, ToolManager
import search_manager
from search_manager import SearchManager, SearchProvider, SearchAPI, DuckDuckGoSearchProvider
from gui import App
from llm_providers import OpenAIProvider, GeminiProvider  # Import GeminiProvider
import tools  # Import the tools module

# Set up logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


class AIAssistantApp:
    def __init__(self):
        self.search_manager = SearchManager(
            [
                SearchAPI(
                    "Google",
                    "YOUR_GOOGLE_CUSTOM_SEARCH_API_KEY",
                    "https://www.googleapis.com/customsearch/v1",
                    {"cx": "YOUR_GOOGLE_CUSTOM_SEARCH_ENGINE_ID"},
                    100,
                    "items",
                    1,
                )
            ],
            duckduckgo_provider=DuckDuckGoSearchProvider(),
        )
        self.tool_manager = ToolManager()
        # Register the search_manager instance as a tool
        self.tool_manager.register_tool("web_search", self.search_manager.search)  
        self.tool_manager.register_tool("foia_search", tools.foia_search)
        self.model_manager = ModelManager(search_enabled=True, tool_manager=self.tool_manager)
        self.agent_manager = AgentManager(self.tool_manager)
        self.llm_provider = self._initialize_llm_provider()

        # Initialize agents *after* other components
        self.researcher_agent = self.agent_manager.create_agent(
            "researcher",
            "utility",  # Set agent_type to "utility"
            self.model_manager,
            self.tool_manager,
            instruction="Instructions for the researcher agent...",
            tools=["web_search", "foia_search"]  # Assign tools to the researcher
        )
        self.writer_agent = self.agent_manager.create_agent(
            "writer",
            "producer",  # Set agent_type to "producer"
            self.model_manager,
            self.tool_manager,
            instruction="Instructions for the writer agent...",
            tools=["web_search"] # Assign tools to the writer 
        )

        self.app = App(
            self.search_manager,
            self.tool_manager,
            self.model_manager,
            self.agent_manager,
            self.llm_provider,
            self.researcher_agent,  # Pass the agents to your App
            self.writer_agent,
        )

    def _initialize_llm_provider(self):
        if LLM_PROVIDER == "openai":
            return OpenAIProvider(OPENAI_API_KEY)
        elif LLM_PROVIDER == "gemini":
            return GeminiProvider(GEMINI_API_KEY, model_name=GEMINI_PRO_MODEL)  # Initialize with Gemini Pro
        # ... add other providers
        else:
            raise ValueError(f"Unsupported LLM provider: {LLM_PROVIDER}")

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