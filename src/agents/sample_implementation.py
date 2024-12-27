from typing import Dict, List, Any
from .agent_interface import BaseDevAgent, AgentCapability


class SampleDevAgent(BaseDevAgent):
    def __init__(self):
        self.capabilities = set(AgentCapability)
    
    def initialize_capabilities(self) -> None:
        print("Initializing basic capabilities")
    
    def process_request(self, request_type: AgentCapability, 
                       context: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "status": "success",
            "message": f"Processed {request_type.value}",
            "result": "Sample implementation result"
        }