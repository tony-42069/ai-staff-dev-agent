#!/usr/bin/env python3

from pathlib import Path
from typing import Dict, Any, List, Optional
import yaml
from pydantic import BaseModel

class RequirementModel(BaseModel):
    name: str
    type: str = "package"
    optional: bool = False

class TestGenerator:
    def __init__(self, agent_config: Dict[str, Any], capabilities_config: List[Dict[str, Any]]):
        """Initialize with standardized RequirementModel instances"""
        self.agent_config = agent_config
        # Convert requirements at initialization
        self.capabilities_config = self._standardize_requirements(capabilities_config)
        self.template_dir = Path("private/config/templates")
        
    def _standardize_requirements(self, configs: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Standardize all requirements to RequirementModel instances"""
        standardized = []
        for cap in configs:
            cap_copy = cap.copy()
            if "requirements" in cap_copy:
                cap_copy["requirements"] = [
                    req if isinstance(req, RequirementModel)
                    else RequirementModel(**req) if isinstance(req, dict)
                    else RequirementModel(name=str(req), type="package", optional=False)
                    for req in cap_copy["requirements"]
                ]
            standardized.append(cap_copy)
        return standardized

    def _generate_error_cases_for_capability(self, capability: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate error test cases with debug logging"""
        print(f"DEBUG: Processing capability: {capability['name']}")
        print(f"DEBUG: Requirements: {capability.get('requirements', [])}")
        
        cases = [
            {
                "name": "invalid_parameters",
                "method": "execute",
                "error_msg": "Invalid parameters provided",
                "task": {"invalid": "task"}
            }
        ]
        
        for req in capability.get("requirements", []):
            print(f"DEBUG: Processing requirement: {req}")
            # Handle both dict and RequirementModel formats
            if hasattr(req, 'dict'):
                # Handle Pydantic model
                req_dict = req.dict()
                req_name = req_dict.get('name')
                req_type = req_dict.get('type', 'package')
            elif isinstance(req, dict):
                req_name = req.get('name')
                req_type = req.get('type', 'package')
            else:
                print(f"DEBUG: Unknown requirement format: {type(req)}")
                continue

            if req_name:
                cases.append({
                    "name": f"missing_{req_name}_requirement",
                    "method": "check_requirement",
                    "error_msg": f"Requirement '{req_name}' (type: {req_type}) not met",
                    "task": {"type": "basic"}
                })
        
        if capability.get("parent"):
            cases.append({
                "name": "parent_not_found",
                "method": "initialize",
                "error_msg": f"Parent capability '{capability['parent']}' not found",
                "task": {"type": "basic"}
            })
            
        return cases

    def _generate_test_method_for_capability(self, capability: Dict[str, Any]) -> str:
        """Generate test methods with proper requirement handling"""
        method_name = f"test_{capability['name']}_capability"
        
        # Generate parameter assertions
        params = capability.get("parameters", {})
        param_assertions = [
            f"        self.assertIn('{key}', capability.parameters)"
            for key in params
        ]
        param_assertions_str = "\n".join(param_assertions) or "        pass"
        
        # Generate requirement assertions with safer access and renamed variable
        req_assertions = []
        for req_obj in capability.get("requirements", []):
            # Handle both dict and RequirementModel formats
            if hasattr(req_obj, 'name'):
                req_name = req_obj.name
                req_type = req_obj.type
            else:
                req_name = req_obj.get('name')
                req_type = req_obj.get('type', 'package')

            if req_name:  # Only add assertion if we have a requirement name
                req_assertions.append(
                    f"        self.assertTrue(\n"
                    f"            self.agent.check_requirement('{req_name}', '{req_type}'),\n"
                    f"            f\"Requirement '{req_name}' (type: {req_type}) not met\"\n"
                    f"        )"
                )
        
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

    def _generate_expected_capabilities(self) -> List[str]:
        """Generate list of expected capabilities"""
        return self.agent_config.get("capabilities", [])

    def _generate_inheritance_map(self) -> Dict[str, Optional[str]]:
        """Generate map of capability inheritance relationships"""
        return {
            cap["name"]: cap.get("parent")
            for cap in self.capabilities_config
        }

    def _generate_test_tasks(self) -> Dict[str, List[Dict[str, Any]]]:
        """Generate test tasks for each capability"""
        return {
            cap["name"]: [{"type": "test"}]
            for cap in self.capabilities_config
        }

    def _generate_error_test_cases(self) -> Dict[str, List[Dict[str, Any]]]:
        """Generate error test cases for each capability"""
        return {
            cap["name"]: self._generate_error_cases_for_capability(cap)
            for cap in self.capabilities_config
        }

    def _generate_capability_specific_tests(self) -> str:
        """Generate capability-specific test methods"""
        test_methods = []
        for capability in self.capabilities_config:
            test_methods.append(self._generate_test_method_for_capability(capability))
        return "\n".join(test_methods)

    def generate_test_file(self, output_path: str) -> None:
        """Generate a test file for the agent with debug logging"""
        print("DEBUG: Starting test file generation")
        template_path = self.template_dir / "test_agent.py.template"
        with open(template_path, "r") as f:
            template = f.read()
        
        # Create template context
        context = {
            "name": self.agent_config["name"],
            "name_lower": self.agent_config["name"].lower(),
            "expected_capabilities": self._generate_expected_capabilities(),
            "inheritance_map": self._generate_inheritance_map(),
            "test_tasks": self._generate_test_tasks(),
            "error_test_cases": self._generate_error_test_cases(),
            "capability_tests": self._generate_capability_specific_tests()
        }
        
        print("DEBUG: Template context generated:")
        for key, value in context.items():
            print(f"DEBUG: {key}: {value[:100] if isinstance(value, str) else value}")
            
        try:
            # Replace all placeholders in template
            content = template.format(**context)
            print("DEBUG: Template formatting successful")
        except KeyError as e:
            print(f"DEBUG: KeyError during template formatting: {e}")
            raise
            
        # Write test file
        with open(output_path, "w") as f:
            f.write(content)
        print(f"DEBUG: Test file written to {output_path}")

def generate_tests(agent_config_path: str, capabilities_config_path: str, output_path: str, agent_name: str) -> None:
    """Generate tests with proper requirement handling"""
    # Load configurations
    with open(agent_config_path, "r") as f:
        agents_config = yaml.safe_load(f)
    with open(capabilities_config_path, "r") as f:
        capabilities_config = yaml.safe_load(f)
        
    # Find the specific agent configuration
    agent_config = next(
        (agent for agent in agents_config if agent["name"] == agent_name),
        None
    )
    if agent_config is None:
        raise ValueError(f"Agent '{agent_name}' not found in configuration")
        
    # Generate tests with standardized requirements
    generator = TestGenerator(agent_config, capabilities_config)
    generator.generate_test_file(output_path)

if __name__ == "__main__":
    import sys
    if len(sys.argv) != 5:
        print("Usage: test_generator.py <agent_config_path> <capabilities_config_path> <output_path> <agent_name>")
        sys.exit(1)
    generate_tests(sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4])
