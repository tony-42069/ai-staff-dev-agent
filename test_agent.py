from src.agents.sample_implementation import SampleDevAgent
from src.agents.agent_interface import AgentCapability


def main():
    # Create agent instance
    agent = SampleDevAgent()
    
    # Initialize capabilities
    agent.initialize_capabilities()
    
    # Test a request
    test_context = {
        "project_name": "test_project",
        "language": "python"
    }
    
    result = agent.process_request(
        AgentCapability.CODE_GENERATION,
        test_context
    )
    
    print("\nTest Result:")
    print(f"Status: {result['status']}")
    print(f"Message: {result['message']}")
    print(f"Result: {result['result']}")


if __name__ == "__main__":
    main()