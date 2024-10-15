from os import system
import openai  # Assuming OpenAI for now, add others as needed
from abc import ABC, abstractmethod
import google.generativeai as genai
from config import GEMINI_API_KEY, SAFETY_SETTINGS
import json


# genai.GenerativeModel(model_name: str = "gemini-1.5-pro-latest", safety_settings: Any | None = None, generation_config: GenerationConfigType | None = None, tools: FunctionLibraryType | None = None, tool_config: ToolConfigType | None = None, system_instruction: ContentType | None = None) -> GenerativeModel



class LLMProvider(ABC):
    @abstractmethod
    def generate_response(self, prompt, **kwargs):
        pass


#load agents from json file and return as dictionary
def load_agents():
    with open("agents.json", "r") as f:
        return json.load(f)

def save_agents(agents):
    with open("agents.json", "w") as f:
        json.dump(agents, f, indent=2)

class OpenAIProvider(LLMProvider):
    def __init__(self, api_key):
        openai.api_key = api_key

    def generate_response(self, prompt, **kwargs):
        response = openai.Completion.create(
            engine=kwargs.get("engine", "text-davinci-003"),  # Default engine
            prompt=prompt,
            max_tokens=kwargs.get("max_tokens", 100),  # Default max tokens
            temperature=kwargs.get("temperature", 0.7),  # Default temperature
            # ... other OpenAI parameters
        )
        return response.choices[0].text.strip()


class GeminiProvider(LLMProvider):
    def __init__(self, api_key, **kwargs):
        self.api_key = api_key
        self.agents = load_agents()
        default_assistant = "default_assistant"
        genai.configure(api_key=self.api_key)
        self.client = genai.GenerativeModel(
            model_name="models/gemini-1.5-pro-latest", 
            safety_settings=SAFETY_SETTINGS, 
            generation_config={"temperature": 0.5,},
            system_instruction=self.agents[default_assistant]
            tools = agents.default_tools
            )
        

    def generate_response(self, prompt, **kwargs):
        response = self.client.generate_content(prompt, **kwargs)
        return response.text if response.text else ""