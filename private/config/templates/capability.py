from typing import List, Dict, Any, Optional
from pydantic import BaseModel
import logging

class RequirementModel(BaseModel):
    name: str
    type: str
    optional: bool = False

class Capability(BaseModel):
    name: str
    description: str
    requirements: List[RequirementModel]
    parameters: Dict[str, Any]
    parent: Optional[str] = None
    _resolved_requirements: List[RequirementModel] = []
    _resolved_parameters: Dict[str, Any] = {}

    def __init__(self, **data):
        # Convert requirement dictionaries to RequirementModel instances
        if 'requirements' in data and isinstance(data['requirements'], list):
            data['requirements'] = [
                RequirementModel(**req) if isinstance(req, dict) else RequirementModel(name=str(req), type='unknown')
                for req in data['requirements']
            ]
        super().__init__(**data)
        self._resolved_requirements = self.requirements.copy()
        self._resolved_parameters = self.parameters.copy()

    def get_requirement_names(self) -> List[str]:
        """Get list of requirement names"""
        return [req.name for req in self.requirements]

    def execute(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute the capability.

        Args:
            task (Dict[str, Any]): The task parameters.

        Returns:
            Dict[str, Any]: The result of the capability execution with 'status' and optional 'message'.
        """
        try:
            raise NotImplementedError("Execute method must be implemented by subclass")
        except Exception as e:
            self.logger.error(f"Error executing capability '{self.name}': {e}")
            return {"status": "error", "message": str(e)}

class CapabilityManager:
    def __init__(self, config: Dict):
        self.config = config
        self.capabilities: Dict[str, Capability] = {}
        self.logger = logging.getLogger(__name__)
        self._inheritance_stack: List[str] = []  # Track inheritance chain
        self.initialize_capabilities()

    def initialize_capabilities(self):
        try:
            self.capabilities = {}
            for capability_config in self.config.get('capabilities', []):
                name = capability_config.get('name', 'unknown')
                try:
                    self.logger.info(f"Initializing capability: {name}")
                    capability = self.create_capability(capability_config)
                    self.capabilities[capability.name] = capability
                    self.logger.info(f"Capability '{name}' initialized successfully")
                except Exception as e:
                    self.logger.error(f"Error initializing capability '{name}': {e}")
            self.logger.info("All capabilities initialized")
        except Exception as e:
            self.logger.error(f"Capability initialization failed: {e}")
            raise

    def create_capability(self, config: Dict) -> Capability:
        """
        Create a capability instance from configuration, handling inheritance.
        """
        try:
            name = config.get('name')
            if name in self._inheritance_stack:
                raise ValueError(f"Circular inheritance detected: {' -> '.join(self._inheritance_stack)} -> {name}")
            
            self._inheritance_stack.append(name)
            
            # Handle parent capability if specified
            parent_name = config.get('parent')
            if parent_name:
                if parent_name not in self.capabilities:
                    parent_config = next((c for c in self.config.get('capabilities', []) 
                                       if c.get('name') == parent_name), None)
                    if not parent_config:
                        raise ValueError(f"Parent capability '{parent_name}' not found")
                    self.capabilities[parent_name] = self.create_capability(parent_config)
                
                parent = self.capabilities[parent_name]
                # Merge requirements and parameters from parent
                parent_reqs = parent._resolved_requirements
                child_reqs = [
                    RequirementModel(**req) if isinstance(req, dict) else RequirementModel(name=str(req), type='unknown')
                    for req in config.get('requirements', [])
                ]
                # Merge using requirement names to avoid duplicates
                merged_req_names = set()
                merged_reqs = []
                for req in parent_reqs + child_reqs:
                    if req.name not in merged_req_names:
                        merged_reqs.append(req)
                        merged_req_names.add(req.name)
                config['requirements'] = merged_reqs
                merged_params = parent._resolved_parameters.copy()
                merged_params.update(config.get('parameters', {}))
                config['parameters'] = merged_params
            
            implementation_name = config.get('implementation')
            if not implementation_name:
                raise ValueError("Implementation class not specified")
            
            # Create capability instance
            implementation_class = config.pop('implementation')
            capability = implementation_class(**config)
            
            self._inheritance_stack.pop()
            return capability
        except Exception as e:
            self.logger.error(f"Failed to create capability from config: {e}")
            raise

    def get_available_capabilities(self) -> List[str]:
        return list(self.capabilities.keys())

# Base capability implementation template
class BaseCapability(Capability):
    def execute(self, task: Dict[str, Any]) -> Dict[str, Any]:
        try:
            self.logger.info(f"Executing capability '{self.name}' with task: {task}")
            
            # Extract parameters from the task
            param1 = task.get("param1")
            param2 = task.get("param2")
            
            # Add your capability execution logic here
            result = {"status": "success", "message": f"Capability '{self.name}' executed successfully."}
            return result
        except Exception as e:
            error_message = f"Error executing capability '{self.name}': {e}"
            self.logger.error(error_message)
            return {"status": "error", "message": error_message}

# Example configuration in YAML
capabilities_config = {
    'capabilities': [
        {
            'name': 'base_capability',
            'description': 'A base capability that others can inherit from',
            'requirements': [
                {
                    'name': 'base_req1',
                    'type': 'package',
                    'optional': False
                },
                {
                    'name': 'base_req2',
                    'type': 'package',
                    'optional': False
                }
            ],
            'parameters': {
                'base_param1': 'value1',
                'base_param2': 'value2'
            },
            'implementation': BaseCapability
        },
        {
            'name': 'derived_capability',
            'description': 'A capability that inherits from base_capability',
            'parent': 'base_capability',
            'requirements': [
                {
                    'name': 'derived_req1',
                    'type': 'package',
                    'optional': False
                }
            ],
            'parameters': {
                'derived_param1': 'value3',
                'base_param1': 'override_value'  # Override parent parameter
            },
            'implementation': BaseCapability
        }
    ]
}
