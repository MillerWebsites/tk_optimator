import openai  # Assuming OpenAI for now, add others as needed
from abc import ABC, abstractmethod
import google.generativeai as genai
from config import GEMINI_API_KEY, SAFETY_SETTINGS


class LLMProvider(ABC):
    @abstractmethod
    def generate_response(self, prompt, **kwargs):
        pass


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
        genai.configure(api_key=self.api_key)
        self.client = genai.GenerativeModel(**kwargs)

    def generate_response(self, prompt, **kwargs):
        response = self.client.generate_content(prompt, **kwargs)
        return response.text if response.text else ""