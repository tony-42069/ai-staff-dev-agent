#!/usr/bin/env python3
"""
CLI tool for managing agent and capability configurations.

This script provides command-line access to the configuration management system,
allowing users to view, update, backup, and restore configurations.

Usage:
    python manage_config.py [command] [options]

Commands:
    list-agents             List all configured agents
    list-capabilities      List all configured capabilities
    update-agent           Update an agent's configuration
    update-capability     Update a capability's configuration
    backup                Create a configuration backup
    restore               Restore from a backup
    validate              Validate current configurations
"""

import argparse
import sys
import json
import shutil
from pathlib import Path
from config_manager import ConfigManager

def parse_args():
    parser = argparse.ArgumentParser(description="Manage agent and capability configurations")
    subparsers = parser.add_subparsers(dest="command", help="Command to execute")
    
    # List agents command
    subparsers.add_parser("list-agents", help="List all configured agents")
    
    # List capabilities command
    subparsers.add_parser("list-capabilities", help="List all configured capabilities")
    
    # Update agent command
    update_agent_parser = subparsers.add_parser("update-agent", help="Update an agent's configuration")
    update_agent_parser.add_argument("name", help="Name of the agent to update")
    update_agent_parser.add_argument("updates", help="JSON string of updates to apply")
    
    # Update capability command
    update_cap_parser = subparsers.add_parser("update-capability", help="Update a capability's configuration")
    update_cap_parser.add_argument("name", help="Name of the capability to update")
    update_cap_parser.add_argument("updates", help="JSON string of updates to apply")
    
    # Backup command
    backup_parser = subparsers.add_parser("backup", help="Create a configuration backup")
    backup_parser.add_argument("--output-dir", help="Custom output directory for backup")
    
    # Restore command
    restore_parser = subparsers.add_parser("restore", help="Restore from a backup")
    restore_parser.add_argument("backup_path", help="Path to backup directory")
    
    # Validate command
    subparsers.add_parser("validate", help="Validate current configurations")
    
    return parser.parse_args()

def main():
    args = parse_args()
    
    try:
        # Initialize config manager
        config_dir = Path("private/config")
        manager = ConfigManager(config_dir)
        
        if args.command == "list-agents":
            # List all agents
            for agent in manager.agents_config:
                print(f"\nAgent: {agent['name']}")
                print(f"Version: {agent['version']}")
                print("Capabilities:", ", ".join(agent['capabilities']))
                print("Parameters:", json.dumps(agent['parameters'], indent=2))
                
        elif args.command == "list-capabilities":
            # List all capabilities
            for cap in manager.capabilities_config:
                print(f"\nCapability: {cap['name']}")
                print(f"Description: {cap['description']}")
                if cap.get('parent'):
                    print(f"Parent: {cap['parent']}")
                print("Requirements:", ", ".join(cap['requirements']))
                print("Parameters:", json.dumps(cap['parameters'], indent=2))
                
        elif args.command == "update-agent":
            # Update agent configuration
            updates = json.loads(args.updates)
            manager.update_agent(args.name, updates)
            print(f"Successfully updated agent: {args.name}")
            
        elif args.command == "update-capability":
            # Update capability configuration
            updates = json.loads(args.updates)
            manager.update_capability(args.name, updates)
            print(f"Successfully updated capability: {args.name}")
            
        elif args.command == "backup":
            # Create backup
            output_dir = args.output_dir if args.output_dir else None
            backup_path = manager.create_backup()
            if output_dir:
                # Copy backup to custom location
                backup_path = shutil.copytree(backup_path, Path(output_dir) / backup_path.name)
            print(f"Backup created at: {backup_path}")
            
        elif args.command == "restore":
            # Restore from backup
            manager.restore_backup(args.backup_path)
            print(f"Successfully restored from backup: {args.backup_path}")
            
        elif args.command == "validate":
            # Validate configurations
            manager.validate_configurations()
            print("All configurations are valid")
            
        else:
            print("No command specified. Use --help for usage information.")
            sys.exit(1)
            
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
