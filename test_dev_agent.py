"""
Test script for Developer Agent functionality
"""
import unittest
from pathlib import Path
from src.core.intelligence import CoreIntelligence, AgentFactory, AgentManager, AgentConfig

class TestDevAgent(unittest.TestCase):
    def setUp(self):
        """Set up test environment"""
        self.config_path = Path("private/config")
        self.core = CoreIntelligence(self.config_path)
        self.factory = AgentFactory(self.core)
        self.manager = AgentManager(self.core)

    def test_core_initialization(self):
        """Test if core intelligence loads configurations correctly"""
        # Verify capabilities loaded
        self.assertIn('project_generation', self.core.capabilities)
        self.assertIn('agent_creation', self.core.capabilities)
        self.assertIn('code_generation', self.core.capabilities)
        self.assertIn('development_tasks', self.core.capabilities)

    def test_agent_creation(self):
        """Test creating a new agent"""
        test_config = AgentConfig(
            name="TestAgent",
            version="1.0.0",
            capabilities=["code_generation", "project_generation"],
            parameters={"max_concurrent_projects": 1},
            security_level="medium",
            environment={"PYTHON_VERSION": "3.9"}
        )
        success = self.factory.create_agent(test_config)
        self.assertTrue(success)

    def test_agent_management(self):
        """Test agent lifecycle management"""
        # First create the agent
        test_config = AgentConfig(
            name="DevAgent",
            version="1.0.0",
            capabilities=["code_generation", "project_generation"],
            parameters={"max_concurrent_projects": 1},
            security_level="medium",
            environment={"PYTHON_VERSION": "3.9"}
        )
        self.factory.create_agent(test_config)
        
        # Now test management
        success = self.manager.start_agent('DevAgent')
        self.assertTrue(success)
        
        # Verify agent is running
        self.assertIn('DevAgent', self.manager.running_agents)
        
        # Stop the agent
        success = self.manager.stop_agent('DevAgent')
        self.assertTrue(success)
        self.assertNotIn('DevAgent', self.manager.running_agents)

if __name__ == '__main__':
    unittest.main()