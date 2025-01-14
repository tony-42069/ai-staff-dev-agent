# Template System Documentation

## Overview

The template system provides a robust framework for generating agent code, configurations, and tests. It supports dynamic template generation, capability inheritance, and comprehensive error handling.

## Components

### 1. Agent Class Template (`agent_class.py.template`)

The base template for generating agent classes with configurable capabilities.

#### Features:
- Dynamic capability loading
- Configuration management
- Error handling and logging
- Lifecycle management (initialization, cleanup)

#### Usage:
```python
from agents.example.agent import ExampleAgent

agent = ExampleAgent()
agent.initialize()
```

### 2. Capability Template (`capability.py.template`)

Template for creating agent capabilities with inheritance support.

#### Features:
- Capability inheritance
- Parameter management
- Requirement validation
- Implementation flexibility

#### Example:
```python
class CustomCapability(BaseCapability):
    def execute(self, task: Dict[str, Any]) -> Dict[str, Any]:
        # Implementation
        pass
```

### 3. Test Template (`test_agent.py.template`)

Template for generating comprehensive test suites.

#### Features:
- Automatic test generation
- Capability testing
- Inheritance validation
- Error case coverage

#### Expected Structure:
```python
class TestAgentCapabilities(unittest.TestCase):
    def setUp(self):
        self.agent = AgentUnderTest()
        self.capabilities = self.agent.get_capabilities()

    def test_capability_requirements(self):
        """Validate capability requirements are met."""
        for capability in self.capabilities:
            requirements = capability.get_requirements()
            # Verify each requirement
            for req in requirements:
                self.assertTrue(
                    self.agent.has_requirement(req),
                    f"Missing requirement: {req}"
                )
```

#### Current Limitations:
- Requirement handling needs refactoring
- Template structure must match capability configuration
- Inheritance validation needs enhancement

## Configuration

### Agent Configuration (`agents.yaml`)
```yaml
- name: "ExampleAgent"
  version: "1.0.0"
  capabilities:
    - capability_one
    - capability_two
  parameters:
    param1: value1
```

### Capability Configuration (`capabilities.yaml`)
```yaml
- name: base_capability
  description: "Base capability"
  requirements:
    - requirement_one
  parameters:
    param1: value1

- name: derived_capability
  parent: base_capability
  description: "Derived capability"
  requirements:
    - requirement_two
```

## Usage Examples

### 1. Creating a New Agent

```bash
# Generate agent structure
python -m tools.generate_agent ExampleAgent

# Add capabilities
python private/config/templates/manage_config.py update-agent ExampleAgent \
  '{"capabilities": ["capability_one", "capability_two"]}'
```

### 2. Adding a New Capability

```bash
# Add capability configuration
python private/config/templates/manage_config.py update-capability NewCapability \
  '{"description": "New capability", "parent": "base_capability"}'
```

### 3. Generating Tests

```bash
# Generate tests for an agent
python private/config/templates/generate_agent_tests.py ExampleAgent
```

## Error Handling

The template system includes comprehensive error handling:

1. Template Validation Errors
2. Configuration Validation Errors
3. Inheritance Validation Errors
4. Runtime Errors

Example error handling:
```python
try:
    agent.initialize()
except ConfigurationError as e:
    logger.error(f"Configuration error: {e}")
except CapabilityError as e:
    logger.error(f"Capability error: {e}")
```

## Best Practices

1. **Template Customization**
   - Keep templates modular
   - Use clear naming conventions
   - Document template parameters

2. **Capability Design**
   - Follow single responsibility principle
   - Use inheritance appropriately
   - Validate requirements thoroughly

3. **Testing**
   - Generate comprehensive tests
   - Include error cases
   - Validate inheritance chains
   - Verify requirement handling
   - Test configuration compatibility

4. **Configuration Management**
   - Use version control
   - Maintain backups
   - Validate changes
   - Ensure format consistency

## Troubleshooting

Common issues and solutions:

1. **Template Generation Fails**
   - Verify template syntax
   - Check configuration validity
   - Ensure all required files exist

2. **Capability Inheritance Issues**
   - Check for circular dependencies
   - Verify parent capability exists
   - Validate parameter inheritance

3. **Test Generation Problems**
   - Known Issue: Test generation fails with KeyError: 'requirement'
     * Root Cause: Mismatch between capability configuration and test template structure
     * Resolution: Update test templates to match current capability format
   - Verify capability configuration format:
     * Check requirements are properly defined
     * Validate inheritance structure
     * Ensure all required fields are present
   - Review test template compatibility:
     * Verify template handles current capability structure
     * Check requirement handling logic
     * Test inheritance chain validation
   - Common Solutions:
     * Update test templates to match capability format
     * Add validation for configuration structure
     * Implement proper error handling
     * Test inheritance scenarios thoroughly
