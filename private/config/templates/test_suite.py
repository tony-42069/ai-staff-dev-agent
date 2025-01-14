"""
Comprehensive test suite for the template system.

This module provides a complete test suite that validates the functionality
of all template components, including agent creation, capability inheritance,
configuration management, and test generation.
"""

import unittest
import tempfile
import shutil
from pathlib import Path
import yaml
import json
from typing import Dict, Any

from config_manager import ConfigManager
from test_generator import TestGenerator

class TestTemplateSystem(unittest.TestCase):
    def setUp(self):
        """Set up test environment."""
        # Create temporary directory for tests
        self.test_dir = Path(tempfile.mkdtemp())
        self.config_dir = self.test_dir / "config"
        self.config_dir.mkdir()
        
        # Create test configurations
        self.create_test_configs()
        
        # Initialize config manager
        self.config_manager = ConfigManager(self.config_dir)
        
    def tearDown(self):
        """Clean up test environment."""
        shutil.rmtree(self.test_dir)
        
    def create_test_configs(self):
        """Create test configuration files."""
        # Create agents.yaml
        agents_config = [{
            "name": "TestAgent",
            "version": "1.0.0",
            "capabilities": ["test_capability", "derived_capability"],
            "parameters": {
                "test_param": "value"
            },
            "security_level": "high",
            "environment": {
                "TEST_MODE": "true"
            }
        }]
        
        # Create capabilities.yaml
        capabilities_config = [
            {
                "name": "base_capability",
                "description": "Base test capability",
                "requirements": ["base_req"],
                "parameters": {
                    "base_param": "value"
                },
                "implementation": "BaseImplementation",
                "version": "1.0.0"
            },
            {
                "name": "derived_capability",
                "description": "Derived test capability",
                "parent": "base_capability",
                "requirements": ["derived_req"],
                "parameters": {
                    "derived_param": "value"
                },
                "implementation": "DerivedImplementation",
                "version": "1.0.0"
            }
        ]
        
        # Write configurations
        with open(self.config_dir / "agents.yaml", "w") as f:
            yaml.safe_dump(agents_config, f)
        with open(self.config_dir / "capabilities.yaml", "w") as f:
            yaml.safe_dump(capabilities_config, f)
            
    def test_config_manager_initialization(self):
        """Test configuration manager initialization."""
        self.assertIsNotNone(self.config_manager)
        self.assertTrue(hasattr(self.config_manager, "agents_config"))
        self.assertTrue(hasattr(self.config_manager, "capabilities_config"))
        
    def test_config_validation(self):
        """Test configuration validation."""
        # Test valid configurations
        self.config_manager.validate_configurations()
        
        # Test invalid agent configuration
        with self.assertRaises(Exception):
            self.config_manager.agents_config[0]["security_level"] = None
            self.config_manager.validate_configurations()
            
    def test_capability_inheritance(self):
        """Test capability inheritance validation."""
        # Test valid inheritance
        self.config_manager._validate_capability_inheritance()
        
        # Test circular inheritance
        capabilities = self.config_manager.capabilities_config
        capabilities.append({
            "name": "circular_capability",
            "description": "Test circular inheritance",
            "parent": "derived_capability",
            "requirements": [],
            "parameters": {},
            "implementation": "CircularImplementation",
            "version": "1.0.0"
        })
        capabilities[1]["parent"] = "circular_capability"  # Create circular dependency
        
        with self.assertRaises(ValueError):
            self.config_manager._validate_capability_inheritance()
            
    def test_config_backup_restore(self):
        """Test configuration backup and restore functionality."""
        # Create backup
        backup_path = self.config_manager.create_backup()
        self.assertTrue(backup_path.exists())
        
        # Modify configuration
        original_config = self.config_manager.agents_config[0].copy()
        self.config_manager.agents_config[0]["version"] = "2.0.0"
        
        # Restore backup
        self.config_manager.restore_backup(backup_path)
        
        # Verify restoration
        self.assertEqual(
            self.config_manager.agents_config[0]["version"],
            original_config["version"]
        )
        
    def test_config_updates(self):
        """Test configuration update functionality."""
        # Test agent update
        agent_updates = {
            "version": "2.0.0",
            "parameters": {"new_param": "value"}
        }
        self.config_manager.update_agent("TestAgent", agent_updates)
        
        updated_agent = next(
            a for a in self.config_manager.agents_config
            if a["name"] == "TestAgent"
        )
        self.assertEqual(updated_agent["version"], "2.0.0")
        self.assertEqual(updated_agent["parameters"]["new_param"], "value")
        
        # Test capability update
        capability_updates = {
            "description": "Updated description",
            "parameters": {"new_param": "value"}
        }
        self.config_manager.update_capability("base_capability", capability_updates)
        
        updated_capability = next(
            c for c in self.config_manager.capabilities_config
            if c["name"] == "base_capability"
        )
        self.assertEqual(updated_capability["description"], "Updated description")
        self.assertEqual(updated_capability["parameters"]["new_param"], "value")
        
    def test_test_generation(self):
        """Test automatic test generation functionality."""
        # Initialize test generator
        generator = TestGenerator(
            self.config_manager.agents_config[0],
            self.config_manager.capabilities_config
        )
        
        # Generate test file
        test_file = self.test_dir / "test_generated_agent.py"
        generator.generate_test_file(str(test_file))
        
        # Verify test file creation
        self.assertTrue(test_file.exists())
        
        # Verify test file content
        with open(test_file, "r") as f:
            content = f.read()
            self.assertIn("class TestTestAgent(unittest.TestCase):", content)
            self.assertIn("test_capability_inheritance", content)
            self.assertIn("test_capability_requirements", content)
            
def run_tests():
    """Run the test suite."""
    unittest.main()

if __name__ == "__main__":
    run_tests()
