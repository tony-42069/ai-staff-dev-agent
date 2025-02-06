# 🚀 AI Staff Development Agent 🤖

A sophisticated framework for creating and managing AI development agents. This project provides core intelligence capabilities for agent creation, project generation, code generation, and development task management.

## ✨ Features

- **Core Intelligence Engine**: Manages agent configurations and capabilities
- **Agent Factory**: Creates new AI agents with customizable capabilities
- **Agent Manager**: Handles agent lifecycle and execution
- **Enhanced Template System**: 
  - Dynamic template generation
  - Capability inheritance support
  - Configuration validation
  - Comprehensive error handling
- **Configuration Management**:
  - Dynamic configuration updates
  - Backup and restore functionality
  - Inheritance validation
  - Version control integration
- **Testing Framework**: 
  - Automated test generation
  - Comprehensive test suite
  - Detailed test reporting
  - CI/CD pipeline integration
- **Improvement Tracking**:
  - Priority-based improvements
  - Dependency management
  - Progress tracking
  - Status reporting

## � Getting Started

### Prerequisites
- Python 3.8+
- pip

### Installation
1. Clone the repository:
   ```bash
   git clone https://github.com/tony-42069/ai-staff-dev-agent.git
   cd ai-staff-dev-agent
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

### Running Tests
The project includes several testing tools:

1. Run the comprehensive test suite:
```bash
python private/config/templates/run_tests.py
```

2. Generate tests for a specific agent:
```bash
python private/config/templates/generate_agent_tests.py <agent_name>
```

3. Run individual test files:
```bash
python -m unittest test_dev_agent.py -v
```

Test reports are generated in JSON and text formats in the `test_reports` directory.

## 🗂️ Project Structure

```
ai-staff-dev-agent/
├── src/
│   └── core/
│       └── intelligence.py        # Core intelligence implementation
├── private/
│   └── config/
│       ├── templates/             # System templates
│       │   ├── agent_class.py.template
│       │   ├── capability.py.template
│       │   ├── test_agent.py.template
│       │   ├── config_manager.py
│       │   ├── test_generator.py
│       │   ├── run_tests.py
│       │   ├── improvement_tracker.py
│       │   └── manage_improvements.py
│       ├── agents.yaml           # Agent configurations
│       └── capabilities.yaml     # Capability configurations
├── tests/
│   ├── test_dev_agent.py        # Core unit tests
│   └── test_suite.py            # Comprehensive test suite
├── test_reports/                # Generated test reports
├── requirements.txt             # Python dependencies
└── README.md                    # Documentation
```

## � Current Status

✅ Core framework implemented  
✅ Agent creation and management working  
✅ Enhanced template system completed  
✅ Dynamic agent loading implemented  
✅ Capability inheritance system working  
✅ Configuration management system active  
✅ Comprehensive testing framework in place  
✅ Improvement tracking system implemented  

## 🛣️ Next Steps

Use the improvement tracking system to view and manage next steps:
```bash
# List all planned improvements
python private/config/templates/manage_improvements.py list

# Show next improvements to implement
python private/config/templates/manage_improvements.py next

# Generate improvement status report
python private/config/templates/manage_improvements.py report
```

## 🛠️ Configuration Management

Manage system configurations using the provided CLI tool:
```bash
# List current configurations
python private/config/templates/manage_config.py list-agents
python private/config/templates/manage_config.py list-capabilities

# Update configurations
python private/config/templates/manage_config.py update-agent <name> <updates>
python private/config/templates/manage_config.py update-capability <name> <updates>

# Create configuration backup
python private/config/templates/manage_config.py backup

# Validate configurations
python private/config/templates/manage_config.py validate
```

## 🤝 Contributing


Contributions are welcome! Please follow these steps:
1. Fork the repository
2. Create a new branch for your feature
3. Commit your changes
4. Push to the branch
5. Submit a pull request

## � License


This project is licensed under the MIT License - see the LICENSE file for details.
