# Configuration Management Documentation

## Overview

The configuration management system provides robust handling of agent and capability configurations, including validation, versioning, backup/restore functionality, and inheritance management.

## Components

### 1. Configuration Manager (`config_manager.py`)

Core component for managing configurations with validation and versioning support.

#### Features:
- Dynamic configuration updates
- Validation with Pydantic models
- Backup and restore functionality
- Inheritance validation
- Error handling and logging

#### Usage:
```python
from config_manager import ConfigManager

manager = ConfigManager("private/config")
manager.validate_configurations()
```

### 2. Management CLI (`manage_config.py`)

Command-line interface for configuration management operations.

#### Features:
- List and filter configurations
- Update configurations
- Create/restore backups
- Validate configurations
- Handle inheritance relationships

## Configuration Files

### 1. Agent Configuration (`agents.yaml`)

Defines agent configurations including capabilities and parameters.

```yaml
- name: "ExampleAgent"
  version: "1.0.0"
  capabilities:
    - base_capability
    - derived_capability
  parameters:
    max_concurrent_tasks: 5
  security_level: "high"
  environment:
    PYTHON_VERSION: "3.9"
```

### 2. Capability Configuration (`capabilities.yaml`)

Defines capabilities with inheritance relationships and requirements.

```yaml
- name: base_capability
  description: "Base capability for operations"
  requirements:
    - name: "requirement1"
      type: "package"
      version: ">=1.0.0"
  parameters:
    param1: "value1"
  implementation: |
    # Implementation code

- name: derived_capability
  parent: base_capability
  description: "Derived capability"
  requirements:
    - name: "requirement2"
      type: "system"
      version: "latest"
  parameters:
    param2: "value2"
```

#### Requirement Structure
Requirements must follow this format to ensure compatibility with test generation:
```yaml
requirements:
  - name: string      # Name of the requirement (required)
    type: string      # Type of requirement: package, system, capability (required)
    version: string   # Version specification (optional)
    optional: bool    # Whether requirement is optional (default: false)
```

This structure is critical for:
- Test generation compatibility
- Proper inheritance handling
- Validation system functionality
- Error detection and reporting

## Command-Line Interface

### 1. Listing Configurations

```bash
# List all agents
python private/config/templates/manage_config.py list-agents

# List all capabilities
python private/config/templates/manage_config.py list-capabilities
```

### 2. Updating Configurations

```bash
# Update agent configuration
python private/config/templates/manage_config.py update-agent ExampleAgent \
  '{"version": "1.1.0", "parameters": {"max_concurrent_tasks": 10}}'

# Update capability configuration
python private/config/templates/manage_config.py update-capability base_capability \
  '{"description": "Updated description", "parameters": {"new_param": "value"}}'
```

### 3. Backup and Restore

```bash
# Create backup
python private/config/templates/manage_config.py backup --output-dir backups/

# Restore from backup
python private/config/templates/manage_config.py restore backups/config_backup_20231025
```

### 4. Validation

```bash
# Validate all configurations
python private/config/templates/manage_config.py validate
```

## Validation System

### 1. Configuration Models

Pydantic models ensure configuration validity:

```python
class AgentConfig(BaseModel):
    name: str
    version: str
    capabilities: List[str]
    parameters: Dict[str, Any]
    security_level: str
    environment: Dict[str, str]

class RequirementConfig(BaseModel):
    name: str
    type: str
    version: Optional[str] = None
    optional: bool = False

class CapabilityConfig(BaseModel):
    name: str
    description: str
    requirements: List[RequirementConfig]
    parameters: Dict[str, Any]
    parent: Optional[str]
    implementation: str
```

### 2. Inheritance Validation

The system validates capability inheritance:
- Prevents circular dependencies
- Ensures parent capabilities exist
- Validates parameter inheritance
- Merges requirements correctly

## Backup System

### 1. Backup Structure

```
backups/
├── config_backup_20231025_120000/
│   ├── agents.yaml
│   └── capabilities.yaml
└── config_backup_20231025_130000/
    ├── agents.yaml
    └── capabilities.yaml
```

### 2. Backup Features

- Timestamped backups
- Complete configuration state
- Easy restoration
- Version tracking

## Best Practices

1. **Configuration Updates**
   - Always validate before updating
   - Use backups before major changes
   - Document configuration changes
   - Test after updates

2. **Inheritance Management**
   - Keep inheritance chains shallow
   - Document parent-child relationships
   - Validate inheritance impacts
   - Monitor capability dependencies

3. **Backup Management**
   - Regular backup schedule
   - Verify backup integrity
   - Clean old backups
   - Document backup contents

4. **Validation**
   - Validate after every change
   - Check inheritance chains
   - Verify requirement satisfaction
   - Test configuration loading

## Troubleshooting

Common issues and solutions:

1. **Test Generation Issues**
   - Known Issue: KeyError: 'requirement' in test generation
     * Cause: Mismatch between capability configuration and test expectations
     * Solution: Ensure requirements follow the structured format above
   - Validation Tips:
     * Use proper requirement structure with name and type
     * Verify inheritance properly merges requirements
     * Check requirement compatibility across capabilities

2. **Validation Failures**
   - Check configuration syntax
   - Verify required fields
   - Validate data types
   - Check inheritance relationships

2. **Backup/Restore Issues**
   - Verify backup directory permissions
   - Check file integrity
   - Validate backup contents
   - Ensure consistent versions

3. **Inheritance Problems**
   - Check for circular dependencies
   - Verify parent capabilities
   - Validate parameter inheritance
   - Check requirement propagation

## Error Messages

Common error messages and their meanings:

1. `ConfigurationError: Invalid configuration format`
   - Configuration file syntax error
   - Missing required fields
   - Invalid data types

2. `InheritanceError: Circular dependency detected`
   - Circular inheritance chain
   - Invalid parent reference
   - Inheritance loop

3. `ValidationError: Invalid parameter value`
   - Parameter type mismatch
   - Missing required parameter
   - Invalid parameter value
