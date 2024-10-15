import logging
from functools import lru_cache
from typing import Dict, Any, List, Optional
import google.generativeai as genai
from search_manager import SearchManager
from agents import AgentManager, ToolManager
import json
import re
import os

from config import (
    GEMINI_API_KEY,
    SAFETY_SETTINGS,
    GEMINI_PRO_MODEL,
    GEMINI_FLASH_MODEL
)

logger = logging.getLogger(__name__)


def log_and_raise_error(message: str, exception: Exception):
    logger.error(message)
    raise exception

class ModelFactory:
    @staticmethod
    @lru_cache(maxsize=None)
    def initialize_model(
        system_instruction: str,
        model_name: str = GEMINI_FLASH_MODEL,  # Default to Gemini Flash
        **generation_config: Any
    ) -> genai.GenerativeModel:
        try:
            genai.configure(api_key=GEMINI_API_KEY)
            return genai.GenerativeModel(
                system_instruction=system_instruction,
                model_name=model_name,
                generation_config=generation_config,
                safety_settings=SAFETY_SETTINGS,
            )
        except Exception as e:
            log_and_raise_error(f"Error initializing model: {e}", e)

    @classmethod
    def create_model(cls, instruction: str, **config: Any) -> genai.GenerativeModel:
        return cls.initialize_model(instruction, **config)

class ModelManager:
    MODEL_NAMES = {
        "producer": GEMINI_PRO_MODEL,
        "utility": GEMINI_FLASH_MODEL,
        "default": GEMINI_FLASH_MODEL
    }

    def __init__(self, search_enabled: bool = True, tool_manager: ToolManager = None):
        self.search_enabled = search_enabled
        self.tool_manager = tool_manager

    def get_model(self, agent_type: str = "producer") -> genai.GenerativeModel:
        """Selects the appropriate Gemini model based on agent type."""
        if agent_type not in self.MODEL_NAMES:
            raise ValueError(f"Unknown agent type: {agent_type}")

        model_name = self.MODEL_NAMES[agent_type]
        return ModelFactory.create_model(model_name=model_name) # No more instruction here 

    
    @staticmethod
    def get_search_instructions() -> str:
        return """
        It is important that you double check your work against the latest available information online when making any claim and assertion of which you are not 110-percent certain. When necessary to form a proper response/output, request web searches to verify information or gather additional details and use one or up to two specific, detailed search queries in the following format explicitly:
        ```
        SEARCH_QUERIES: | Query 1 | Query 2 |
        ```
        *IF requesting a web search, you MUST use the above format exactly otherwise it will go unseen.
        You will receive the text or relevant information from top search results' pages in a subsequent message and then you can integrate the relevant information into and complete your original/actual full response.
        """
    def generate_convo_context(self, prompt: str, chat_log: List[str]) -> str:
        return f"\nLatest Progress: {'\n'.join(chat_log[-10:])}\nTarget final output and/or instruction from the user: {prompt}"
    
    def generate_response(
            self,
            agent_type: str,  # Use agent_type directly
            user_prompt: str,
            chat_log: List[str],
            context: str,
            search_manager: SearchManager = None,
        ) -> str:
        try:
            model = self.get_model(agent_type=agent_type)  # Pass agent_type to get_model
            context = generate_convo_context(user_prompt, chat_log)
            response = model.generate_content(context)
            response_text = response.text if response.text else ""

            # Example tool call parsing (adapt as needed)
            match = re.match(r"Tool Call:\s*(\w+)\((.*)\)", response_text)
            if match and self.tool_manager:
                tool_name = match[1]
                arguments_str = match[2]
                arguments = [arg.strip() for arg in arguments_str.split(",") if arg.strip()]

                # Convert arguments to keyword arguments
                tool_kwargs = {}
                for arg in arguments:
                    key, value = arg.split("=", 1)
                    tool_kwargs[key.strip()] = value.strip()

                try:
                    tool_result = self.tool_manager.execute_tool(tool_name, **tool_kwargs)
                    # Integrate tool result into response
                    response_text = f"Tool '{tool_name}' result: {tool_result}\n{response_text}"
                except ValueError as e:
                    response_text = f"Error: Invalid tool name '{tool_name}'"
                except Exception as e:
                    response_text = f"Error executing tool '{tool_name}': {e}"

            chat_log.append(f"{agent_type.capitalize()}: {response_text}")  # Use agent_type here
            return response_text

        except Exception as e:
            logger.error(f"Error generating response for {agent_type}: {e}")  # Use agent_type here
            return f"An error occurred while generating the response: {str(e)}"

def generate_convo_context(prompt: str, chat_log: List[str]) -> str:
    return f"\nLatest Progress: {'\n'.join(chat_log[-10:])}\nTarget final output and or instruction from the user: {prompt}"