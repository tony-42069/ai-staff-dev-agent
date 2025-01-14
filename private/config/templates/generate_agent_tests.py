#!/usr/bin/env python3
"""
CLI tool for generating agent test files.

This script uses the test generator system to automatically create test files
for agents based on their configuration and capabilities.

Usage:
    python generate_agent_tests.py <agent_name>
    
The script will look for the agent's configuration in the standard location
and generate appropriate test files.
"""

import argparse
import os
import sys
from pathlib import Path
from test_generator import generate_tests

def main():
    parser = argparse.ArgumentParser(description="Generate tests for an agent")
    parser.add_argument("agent_name", help="Name of the agent to generate tests for")
    parser.add_argument("--config-dir", default="private/config",
                       help="Directory containing configuration files")
    parser.add_argument("--output-dir", default="tests",
                       help="Directory where test files should be written")
    args = parser.parse_args()
    
    try:
        # Construct paths
        config_dir = Path(args.config_dir)
        agent_config_path = config_dir / "agents.yaml"
        capabilities_config_path = config_dir / "capabilities.yaml"
        
        # Create output directory if it doesn't exist
        output_dir = Path(args.output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Generate test file path
        test_file_name = f"test_{args.agent_name.lower()}_agent.py"
        output_path = output_dir / test_file_name
        
        # Generate tests
        print(f"Generating tests for agent: {args.agent_name}")
        print(f"Using configuration files from: {config_dir}")
        print(f"Writing test file to: {output_path}")
        
        generate_tests(
            str(agent_config_path),
            str(capabilities_config_path),
            str(output_path),
            args.agent_name
        )
        
        print(f"Successfully generated test file: {output_path}")
        
        # Make the test file executable
        os.chmod(output_path, 0o755)
        
    except Exception as e:
        print(f"Error generating tests: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
