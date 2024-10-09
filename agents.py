import json
import os
import logging
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)

class Agent:
    def __init__(self, file_path: str = "agents.json"):
        self.file_path = file_path
        self.agents = self.load_agents()

    def load_agents(self) -> Dict[str, Dict[str, Any]]:
        if not os.path.exists(self.file_path):
            return {}
        try:
            with open(self.file_path, "r") as f:
                return json.load(f)
        except json.JSONDecodeError as e:
            logger.error(f"Error loading agents from {self.file_path}: {e}")
            return {}

    def save_agents(self) -> None:
        try:
            with open(self.file_path, "w") as f:
                json.dump(self.agents, f, indent=2)
        except IOError as e:
            logger.error(f"Error saving agents to {self.file_path}: {e}")

    def manage_agent(self, name: str, action: str, instruction: Optional[str] = None, model_config: Optional[Dict[str, Any]] = None) -> bool:
        if action == "create":
            if name in self.agents:
                logger.warning(f"Agent '{name}' already exists")
                return False
            self.agents[name] = {"instruction": instruction, "model_config": model_config}
        elif action == "update":
            if name not in self.agents:
                logger.warning(f"Agent '{name}' does not exist")
                return False
            if instruction is not None:
                self.agents[name]["instruction"] = instruction
            if model_config is not None:
                self.agents[name]["model_config"] = model_config
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

    def create_agent(self, name: str, instruction: str, model_config: Dict[str, Any]) -> bool:
        return self.manage_agent(name, "create", instruction, model_config)

    def update_agent(self, name: str, instruction: Optional[str] = None, model_config: Optional[Dict[str, Any]] = None) -> bool:
        return self.manage_agent(name, "update", instruction, model_config)

    def delete_agent(self, name: str) -> bool:
        return self.manage_agent(name, "delete")

    def get_agent(self, name: str) -> Optional[Dict[str, Any]]:
        return self.agents.get(name)

    def list_agents(self) -> list:
        return list(self.agents.keys())
