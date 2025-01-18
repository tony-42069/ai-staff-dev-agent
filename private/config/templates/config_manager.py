"""
Configuration Management System

This module provides a robust system for managing and updating agent and capability
configurations dynamically. It handles validation, versioning, and provides a clean
API for configuration operations.
"""

from typing import Dict, List, Any, Optional, Union
import yaml
import json
from pathlib import Path
from datetime import datetime
import shutil
import logging
from pydantic import BaseModel, Field, validator
from private.config.templates.capability import RequirementModel

class CapabilityConfig(BaseModel):
    """Capability configuration model."""
    name: str
    description: str
    requirements: List[RequirementModel]
    parameters: Dict[str, Any]
    parent: Optional[str] = None
    implementation: str
    version: str = "1.0.0"

class AgentConfig(BaseModel):
    """Agent configuration model."""
    name: str
    version: str
    capabilities: List[str]
    parameters: Dict[str, Any]
    security_level: str
    environment: Dict[str, str]

class ConfigManager:
    def __init__(self, config_dir: Union[str, Path]):
        """
        Initialize the configuration manager.

        Args:
            config_dir: Directory containing configuration files
        """
        self.config_dir = Path(config_dir)
        self.backup_dir = self.config_dir / "backups"
        self.agents_file = self.config_dir / "agents.yaml"
        self.capabilities_file = self.config_dir / "capabilities.yaml"
        self.logger = logging.getLogger(__name__)
        
        # Create backup directory if it doesn't exist
        self.backup_dir.mkdir(parents=True, exist_ok=True)
        
        # Load current configurations
        self.reload_configurations()

    def reload_configurations(self) -> None:
        """Reload configurations from files."""
        try:
            with open(self.agents_file, 'r') as f:
                self.agents_config = yaml.safe_load(f) or []
            with open(self.capabilities_file, 'r') as f:
                self.capabilities_config = yaml.safe_load(f) or []
                
            # Validate configurations
            self.validate_configurations()
            
        except Exception as e:
            self.logger.error(f"Error loading configurations: {e}")
            raise

    def validate_configurations(self) -> None:
        """Validate all configurations."""
        # Validate agents
        for agent in self.agents_config:
            AgentConfig(**agent)
            
        # Validate capabilities
        for capability in self.capabilities_config:
            CapabilityConfig(**capability)
            
        # Validate capability inheritance
        self._validate_capability_inheritance()

    def _validate_capability_inheritance(self) -> None:
        """Validate capability inheritance relationships."""
        capability_names = {cap['name'] for cap in self.capabilities_config}
        visited = set()
        
        def check_circular_inheritance(name: str, path: List[str]) -> None:
            if name in path:
                raise ValueError(f"Circular inheritance detected: {' -> '.join(path + [name])}")
            
            capability = next((c for c in self.capabilities_config if c['name'] == name), None)
            if not capability:
                raise ValueError(f"Capability not found: {name}")
                
            if capability.get('parent'):
                if capability['parent'] not in capability_names:
                    raise ValueError(f"Parent capability not found: {capability['parent']}")
                check_circular_inheritance(capability['parent'], path + [name])
        
        # Check each capability
        for capability in self.capabilities_config:
            if capability['name'] not in visited:
                check_circular_inheritance(capability['name'], [])
                visited.add(capability['name'])

    def create_backup(self) -> Path:
        """Create a backup of current configurations."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_path = self.backup_dir / f"config_backup_{timestamp}"
        backup_path.mkdir(exist_ok=True)
        
        # Copy configuration files
        shutil.copy2(self.agents_file, backup_path / "agents.yaml")
        shutil.copy2(self.capabilities_file, backup_path / "capabilities.yaml")
        
        return backup_path

    def restore_backup(self, backup_path: Union[str, Path]) -> None:
        """
        Restore configurations from a backup.

        Args:
            backup_path: Path to the backup directory
        """
        backup_path = Path(backup_path)
        if not backup_path.exists():
            raise ValueError(f"Backup path does not exist: {backup_path}")
            
        # Restore files
        shutil.copy2(backup_path / "agents.yaml", self.agents_file)
        shutil.copy2(backup_path / "capabilities.yaml", self.capabilities_file)
        
        # Reload configurations
        self.reload_configurations()

    def update_agent(self, name: str, updates: Dict[str, Any]) -> None:
        """
        Update an agent's configuration.

        Args:
            name: Name of the agent to update
            updates: Dictionary of updates to apply
        """
        # Create backup
        self.create_backup()
        
        try:
            # Find and update agent
            agent = next((a for a in self.agents_config if a['name'] == name), None)
            if not agent:
                raise ValueError(f"Agent not found: {name}")
                
            # Apply updates
            agent.update(updates)
            
            # Validate updated configuration
            AgentConfig(**agent)
            
            # Save changes
            self.save_configurations()
            
        except Exception as e:
            self.logger.error(f"Error updating agent {name}: {e}")
            raise

    def update_capability(self, name: str, updates: Dict[str, Any]) -> None:
        """
        Update a capability's configuration.

        Args:
            name: Name of the capability to update
            updates: Dictionary of updates to apply
        """
        # Create backup
        self.create_backup()
        
        try:
            # Find and update capability
            capability = next((c for c in self.capabilities_config if c['name'] == name), None)
            if not capability:
                raise ValueError(f"Capability not found: {name}")
                
            # Apply updates
            capability.update(updates)
            
            # Validate updated configuration
            CapabilityConfig(**capability)
            self._validate_capability_inheritance()
            
            # Save changes
            self.save_configurations()
            
        except Exception as e:
            self.logger.error(f"Error updating capability {name}: {e}")
            raise

    def save_configurations(self) -> None:
        """Save current configurations to files."""
        try:
            # Save agents configuration
            with open(self.agents_file, 'w') as f:
                yaml.safe_dump(self.agents_config, f, default_flow_style=False)
                
            # Save capabilities configuration
            with open(self.capabilities_file, 'w') as f:
                yaml.safe_dump(self.capabilities_config, f, default_flow_style=False)
                
            self.logger.info("Configurations saved successfully")
            
        except Exception as e:
            self.logger.error(f"Error saving configurations: {e}")
            raise
