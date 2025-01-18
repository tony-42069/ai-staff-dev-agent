"""
Test Generator for Agent Test Cases

This module generates test cases for agents based on their configuration and capabilities.
It automatically creates test cases for capability initialization, parameter validation,
requirement verification, and inheritance relationships.
"""

from typing import Dict, Any, List
import yaml
import json
from pathlib import Path
from private.config.templates.capability import RequirementModel

class TestGenerator:
    def __init__(self, agent_config: Dict[str, Any], capabilities_config: List[Dict[str, Any]]):
        """
        Initialize the test generator.

        Args:
            agent_config: Agent configuration dictionary
            capabilities_config: List of capability configurations
        """
        self.agent_config = agent_config
        self.capabilities_config = capabilities_config
        self.template_dir = Path("private/config/templates")
        
    def generate_test_file(self, output_path: str) -> None:
        """
        Generate a test file for the agent.

        Args:
            output_path: Path where the test file should be written
        """
        # Read test template
        template_path = self.template_dir / "test_agent.py.template"
        with open(template_path, "r") as f:
            template = f.read()
            
        # Generate test content
        content = template.format(
            name=self.agent_config["name"],
            name_lower=self.agent_config["name"].lower(),
            expected_capabilities=self._generate_expected_capabilities(),
            inheritance_map=self._generate_inheritance_map(),
            test_tasks=self._generate_test_tasks(),
            error_test_cases=self._generate_error_test_cases(),
            capability_tests=self._generate_capability_specific_tests()
        )
        
        # Write test file
        with open(output_path, "w") as f:
            f.write(content)
            
    def _generate_expected_capabilities(self) -> str:
        """Generate the list of expected capabilities."""
        capabilities = [cap["name"] for cap in self.capabilities_config]
        return json.dumps(capabilities, indent=4)
        
    def _generate_inheritance_map(self) -> str:
        """Generate the inheritance map for capabilities."""
        inheritance_map = {}
        for cap in self.capabilities_config:
            inheritance_map[cap["name"]] = cap.get("parent")
        return json.dumps(inheritance_map, indent=4)
        
    def _generate_test_tasks(self) -> str:
        """Generate test tasks for each capability."""
        test_tasks = {}
        for cap in self.capabilities_config:
            tasks = self._generate_tasks_for_capability(cap)
            test_tasks[cap["name"]] = tasks
        return json.dumps(test_tasks, indent=4)
        
    def _generate_tasks_for_capability(self, capability: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate test tasks for a specific capability."""
        tasks = []
        
        # Generate basic task
        basic_task = {
            "type": "basic",
            "parameters": capability.get("parameters", {})
        }
        tasks.append(basic_task)
        
        # Generate parameter validation task
        if capability.get("parameters"):
            validation_task = {
                "type": "validation",
                "parameters": {
                    k: self._generate_test_value(v)
                    for k, v in capability["parameters"].items()
                }
            }
            tasks.append(validation_task)
            
        return tasks
        
    def _generate_error_test_cases(self) -> str:
        """Generate error test cases for each capability."""
        error_cases = {}
        for cap in self.capabilities_config:
            cases = self._generate_error_cases_for_capability(cap)
            error_cases[cap["name"]] = cases
        return json.dumps(error_cases, indent=4)
        
    def _generate_error_cases_for_capability(self, capability: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate error test cases for a specific capability."""
        cases = [
            {
                "name": "invalid_parameters",
                "method": "execute",
                "error_msg": "Invalid parameters provided",
                "task": {"invalid": "task"}
            }
        ]
        
        # Handle requirements - now always in dictionary format
        requirements = capability.get("requirements", [])
        for req in requirements:
            # Validate requirement format
            if not isinstance(req, dict) or "name" not in req or "type" not in req:
                raise ValueError(f"Invalid requirement format in capability '{capability['name']}': {req}")
            
            cases.append({
                "name": f"missing_{req['name']}_requirement",
                "method": "check_requirement",
                "error_msg": f"Requirement '{req['name']}' (type: {req['type']}) not met for capability '{capability['name']}'",
                "task": {"type": "basic"}
            })
        
        # Add inheritance-specific error cases if capability has a parent
        if capability.get("parent"):
            cases.append({
                "name": "parent_not_found",
                "method": "initialize",
                "error_msg": f"Parent capability '{capability['parent']}' not found",
                "task": {"type": "basic"}
            })
            
        return cases
        
    def _generate_capability_specific_tests(self) -> str:
        """Generate capability-specific test methods."""
        test_methods = []
        
        for cap in self.capabilities_config:
            method = self._generate_test_method_for_capability(cap)
            test_methods.append(method)
            
        return "\n\n".join(test_methods)
        
    def _generate_test_method_for_capability(self, capability: Dict[str, Any]) -> str:
        """Generate a test method for a specific capability."""
        method_name = f"test_{capability['name']}_capability"
        params = capability.get("parameters", {})
        param_assertions = []
        
        for key, value in params.items():
            assertion = f"        self.assertIn('{key}', capability.parameters)"
            param_assertions.append(assertion)
            
        param_assertions_str = "\n".join(param_assertions)
        
        # Add requirement assertions - now using structured requirement format
        req_assertions = []
        for req in capability.get("requirements", []):
            # Validate requirement format
            if not isinstance(req, dict) or "name" not in req or "type" not in req:
                raise ValueError(f"Invalid requirement format in capability '{capability['name']}': {req}")
            
            req_assertion = (
                f"        self.assertTrue(\n"
                f"            self.agent.check_requirement('{req['name']}', '{req['type']}'),\n"
                f"            f\"Requirement '{req['name']}' (type: {req['type']}) not met\"\n"
                f"        )"
            )
            req_assertions.append(req_assertion)
            
        req_assertions_str = "\n".join(req_assertions) if req_assertions else "        pass"
        
        return f'''
    def {method_name}(self):
        """Test {capability['name']} capability"""
        capability = self.agent.capabilities["{capability['name']}"]
        self.assertIsNotNone(capability)
        
        # Test parameters
{param_assertions_str}
        
        # Test requirements
{req_assertions_str}
        
        # Test execution
        result = capability.execute({{"type": "test"}})
        self.assertEqual(result["status"], "success")'''
        
    def _generate_test_value(self, value: Any) -> Any:
        """Generate a test value based on the parameter type."""
        if isinstance(value, bool):
            return not value
        elif isinstance(value, (int, float)):
            return value + 1
        elif isinstance(value, str):
            return f"test_{value}"
        elif isinstance(value, list):
            return value + ["test_value"]
        elif isinstance(value, dict):
            return {k: self._generate_test_value(v) for k, v in value.items()}
        return value

def generate_tests(agent_config_path: str, capabilities_config_path: str, output_path: str, agent_name: str) -> None:
    """
    Generate tests for an agent based on configuration files.

    Args:
        agent_config_path: Path to the agent configuration file
        capabilities_config_path: Path to the capabilities configuration file
        output_path: Path where the test file should be written
    """
    # Load configurations
    with open(agent_config_path, "r") as f:
        agents_config = yaml.safe_load(f)
    with open(capabilities_config_path, "r") as f:
        raw_capabilities = yaml.safe_load(f)
        
    # Convert requirements to RequirementModel instances
    capabilities_config = []
    for cap in raw_capabilities:
        if "requirements" in cap:
            cap["requirements"] = [
                RequirementModel(**req) if isinstance(req, dict) else RequirementModel(name=str(req), type="unknown")
                for req in cap["requirements"]
            ]
        capabilities_config.append(cap)
        
    # Find the specific agent configuration
    agent_config = next(
        (agent for agent in agents_config if agent["name"] == agent_name),
        None
    )
    if agent_config is None:
        raise ValueError(f"Agent '{agent_name}' not found in configuration")
        
    # Generate tests
    generator = TestGenerator(agent_config, capabilities_config)
    generator.generate_test_file(output_path)
