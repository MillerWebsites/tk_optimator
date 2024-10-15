from config import GEMINI_API_KEY
import config
import llm_providers
from llm_providers import GeminiProvider

import agents

from agents import AgentManager, ToolManager
import search_manager
from search_manager import SearchManager, SearchProvider, SearchAPI, DuckDuckGoSearchProvider
import tools

from models import ModelManager

#agent_mannager = AgentManager()
#get_agents


#initialize gemini-1.5-pro-latest
def initialize_model(system_instruction: str, model_name: str = "gemini_1.5_pro_latest", temperature: float = 0.5) -> None:
    """Initialize a model with the given system instruction and temperature."""
    client = GeminiProvider(api_key=GEMINI_API_KEY)
    config = {
        system_instruction: model_name,
        "temperature": temperature,
    }

response = model_manager.model_name.generate_response("your_prompt")
print(response)

