#!/usr/bin/env python3
"""
CLI tool for managing system improvements.

This script provides command-line access to the improvement tracking system,
allowing users to add, update, and monitor improvements to the template system.

Usage:
    python manage_improvements.py [command] [options]

Commands:
    list                List all improvements
    add                 Add a new improvement
    update             Update improvement status
    report             Generate improvement report
    next               Show next improvements to implement
    add-dependency     Add dependency between improvements
"""

import argparse
import sys
import json
from pathlib import Path
from improvement_tracker import ImprovementTracker, initialize_improvements

def parse_args():
    parser = argparse.ArgumentParser(description="Manage system improvements")
    subparsers = parser.add_subparsers(dest="command", help="Command to execute")
    
    # List command
    list_parser = subparsers.add_parser("list", help="List improvements")
    list_parser.add_argument("--status", help="Filter by status")
    list_parser.add_argument("--component", help="Filter by component")
    
    # Add command
    add_parser = subparsers.add_parser("add", help="Add new improvement")
    add_parser.add_argument("title", help="Improvement title")
    add_parser.add_argument("description", help="Improvement description")
    add_parser.add_argument("component", help="Component to improve")
    add_parser.add_argument("--priority", default="medium", 
                           choices=["high", "medium", "low"],
                           help="Improvement priority")
    
    # Update command
    update_parser = subparsers.add_parser("update", help="Update improvement status")
    update_parser.add_argument("id", help="Improvement ID")
    update_parser.add_argument("status", choices=["pending", "in_progress", 
                                                "completed", "verified"],
                             help="New status")
    update_parser.add_argument("--test-results", help="JSON string of test results")
    
    # Report command
    report_parser = subparsers.add_parser("report", help="Generate improvement report")
    report_parser.add_argument("--output", help="Output file path")
    
    # Next improvements command
    subparsers.add_parser("next", help="Show next improvements to implement")
    
    # Add dependency command
    dep_parser = subparsers.add_parser("add-dependency", 
                                      help="Add dependency between improvements")
    dep_parser.add_argument("id", help="Improvement ID")
    dep_parser.add_argument("dependency_id", help="Dependency improvement ID")
    
    return parser.parse_args()

def main():
    args = parse_args()
    
    try:
        # Initialize tracker
        config_dir = Path("private/config")
        tracker = initialize_improvements(config_dir)
        
        if args.command == "list":
            # List improvements
            improvements = tracker.list_improvements(
                status=args.status,
                component=args.component
            )
            
            if not improvements:
                print("No improvements found matching criteria")
                return
                
            for imp in improvements:
                print(f"\nID: {imp.id}")
                print(f"Title: {imp.title}")
                print(f"Status: {imp.status}")
                print(f"Priority: {imp.priority}")
                print(f"Component: {imp.component}")
                
        elif args.command == "add":
            # Add new improvement
            improvement = tracker.add_improvement(
                args.title,
                args.description,
                args.component,
                args.priority
            )
            print(f"Added improvement with ID: {improvement.id}")
            
        elif args.command == "update":
            # Update improvement status
            test_results = None
            if args.test_results:
                test_results = json.loads(args.test_results)
                
            tracker.update_status(args.id, args.status, test_results)
            print(f"Updated improvement {args.id} status to: {args.status}")
            
        elif args.command == "report":
            # Generate report
            report = tracker.generate_report(args.output)
            if args.output:
                print(f"Report saved to: {args.output}")
            else:
                print(report)
                
        elif args.command == "next":
            # Show next improvements
            improvements = tracker.get_next_improvements()
            if not improvements:
                print("No improvements ready for implementation")
                return
                
            print("Next improvements to implement:")
            for imp in improvements:
                print(f"\nID: {imp.id}")
                print(f"Title: {imp.title}")
                print(f"Priority: {imp.priority}")
                print(f"Component: {imp.component}")
                
        elif args.command == "add-dependency":
            # Add dependency
            tracker.add_dependency(args.id, args.dependency_id)
            print(f"Added dependency: {args.id} -> {args.dependency_id}")
            
        else:
            print("No command specified. Use --help for usage information.")
            sys.exit(1)
            
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
