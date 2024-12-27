# In tests/test_core_intelligence.py
class TestCoreIntelligence(unittest.TestCase):
    def setUp(self):
        self.core = CoreIntelligence(Path("private/config"))
        self.factory = AgentFactory(self.core)

    def test_agent_creation(self):
        config = AgentConfig(
            name="DevAgent",
            version="1.0.0",
            capabilities=["project_generation", "code_generation"],
            parameters={},
            security_level="high",
            environment={"PYTHON_VERSION": "3.9"}
        )
        agent = self.factory.create_agent(config)
        self.assertIsNotNone(agent)
        self.assertTrue(agent.initialize())