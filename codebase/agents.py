"""Module for defining AI agents and their interactions with tools."""
import json
import os
import logging
from typing import Dict, Any, Optional, Callable, List
import re
import inspect

logger = logging.getLogger(__name__)


class ToolManager:
    """Manages the registration and execution of external tools."""

    def __init__(self):
        self.tools: Dict[str, Callable] = {}

    def register_tool(self, tool_name: str, function: Callable):
        """Registers a tool with the manager."""
        self.tools[tool_name] = function

    def execute_tool(self, tool_name: str, *args, **kwargs) -> Any:
        """Executes a registered tool."""
        if tool_name in self.tools:
            return self.tools[tool_name](*args, **kwargs)
        else:
            raise ValueError(f"Tool '{tool_name}' not registered.")


class Agent:
    """Represents an AI agent with specific instructions and capabilities."""

    def __init__(
        self,
        name: str,
        agent_type: str,
        model_manager,  # Forward reference in parameter list
        tool_manager: ToolManager,
        instruction: str,  # Base instruction for the agent's role
        tools: List[str],  # List of tool names assigned to this agent
        model_config: Optional[Dict[str, Any]] = None,
    ):
        self.name = name
        self.agent_type = agent_type
        self.model_manager = model_manager
        self.tool_manager = tool_manager
        self.tools = tools
        self.instruction = self._construct_instructions(instruction)  # Build full instructions
        self.model_config = model_config
        self.chat_log: List[str] = []

    def _construct_instructions(self, base_instruction: str) -> str:
        """Constructs the full system instructions, including tool docstrings."""
        full_instruction = base_instruction

        for tool_name in self.tools:
            tool_function = self.tool_manager.tools.get(tool_name)
            if tool_function:
                docstring = inspect.getdoc(tool_function)  # Get the docstring
                full_instruction += f"\n\n### Tool: {tool_name}\n{docstring}"

        return full_instruction

    def generate_response(self, user_prompt: str, context: str = "") -> str:
        """Generates a response from the agent's model."""
        from models import ModelManager  # Import ModelManager here

        response = self.model_manager.generate_response(
            agent_type=self.agent_type,
            user_prompt=user_prompt,
            chat_log=self.chat_log,
            context=context
        )

        # Check for tool call in response
        tool_match = re.search(r"Tool Call:\s*(\w+)\((.*)\)", response)
        if tool_match:
            tool_name = tool_match.group(1)
            tool_args_str = tool_match.group(2)
            tool_args = [arg.strip() for arg in tool_args_str.split(",") if arg.strip()]

            if tool_name in self.tools:
                try:
                    tool_result = self.tool_manager.execute_tool(tool_name, *tool_args)
                    response = f"Tool '{tool_name}' result: {tool_result}\n{response}"
                except Exception as e:
                    response = f"Error executing tool '{tool_name}': {e}\n{response}"
            else:
                response = f"Error: Tool '{tool_name}' not available.\n{response}"

        self.chat_log.append(f"{self.name.capitalize()}: {response}")
        return response


class AgentManager:
    """Manages the creation, loading, and updating of AI agents."""

    def __init__(self, tool_manager: ToolManager, file_path: str = "agents.json"):
        self.file_path = file_path
        self.agents = self.load_agents()
        self.tool_manager = tool_manager

    def load_agents(self) -> Dict[str, Dict[str, Any]]:
        """Loads agents from a JSON file."""
        if not os.path.exists(self.file_path):
            return {}
        try:
            with open(self.file_path, "r") as f:
                return json.load(f)
        except json.JSONDecodeError as e:
            logger.error(f"Error loading agents from {self.file_path}: {e}")
            return {}

    def save_agents(self) -> None:
        """Saves agents to a JSON file."""
        try:
            with open(self.file_path, "w") as f:
                json.dump(self.agents, f, indent=2)
        except IOError as e:
            logger.error(f"Error saving agents to {self.file_path}: {e}")

    def manage_agent(
        self,
        name: str,
        agent_type: str,
        model_manager,  # No type hint here
        tool_manager: ToolManager,
        action: str,
        instruction: Optional[str] = None,
        model_config: Optional[Dict[str, Any]] = None
    ) -> bool:
        if action == "create":
            if name in self.agents:
                logger.warning(f"Agent '{name}' already exists")
                return False
            self.agents[name] = {
                "agent_type": agent_type,
                "instruction": instruction,
                "model_config": model_config
            }
        elif action == "update":
            if name not in self.agents:
                logger.warning(f"Agent '{name}' does not exist")
                return False
            if instruction is not None:
                self.agents[name]["instruction"] = instruction
            if agent_type is not None:
                self.agents[name]["agent_type"] = agent_type
        elif action == "delete":
            if name not in self.agents:
                logger.warning(f"Agent '{name}' does not exist")
                return False
            del self.agents[name]
        else:
            logger.error(f"Unknown action '{action}'")
            return False
        self.save_agents()
        return True

    def create_agent(
        self,
        name: str,
        agent_type: str,
        model_manager,  # No type hint here
        tool_manager: ToolManager,
        instruction: str,
        model_config: Dict[str, Any] = None
    ) -> Agent:
        """Creates a new agent."""
        if self.manage_agent(name, agent_type, model_manager, tool_manager, "create", instruction, model_config):
            return Agent(name, agent_type, model_manager, tool_manager, instruction, model_config)
        else:
            return None  # Or raise an exception if creation fails