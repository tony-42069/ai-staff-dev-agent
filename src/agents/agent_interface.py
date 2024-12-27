from enum import Enum
from typing import Dict, List, Any
from abc import ABC, abstractmethod


class AgentCapability(Enum):
    CODE_GENERATION = "code_generation"
    PROJECT_STRUCTURE = "project_structure"
    AGENT_DEVELOPMENT = "agent_development"


class BaseDevAgent(ABC):
    @abstractmethod
    def initialize_capabilities(self) -> None:
        pass

    @abstractmethod
    def process_request(self, request_type: AgentCapability, 
                       context: Dict[str, Any]) -> Dict[str, Any]:
        pass