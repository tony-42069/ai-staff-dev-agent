"""
Improvement Tracker System

This module provides functionality to track, manage, and implement
iterative improvements to the template system based on testing results
and feedback.
"""

import json
import yaml
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Union
from dataclasses import dataclass, asdict
import logging

@dataclass
class Improvement:
    """Represents a system improvement."""
    id: str
    title: str
    description: str
    component: str
    priority: str  # high, medium, low
    status: str  # pending, in_progress, completed, verified
    created_at: str
    updated_at: str
    implemented_at: Optional[str] = None
    verified_at: Optional[str] = None
    test_results: Optional[Dict] = None
    dependencies: List[str] = None
    
    @classmethod
    def create(cls, title: str, description: str, component: str, priority: str) -> 'Improvement':
        """Create a new improvement."""
        now = datetime.now().isoformat()
        return cls(
            id=f"IMP_{now.replace(':', '').replace('.', '').replace('-', '')}",
            title=title,
            description=description,
            component=component,
            priority=priority,
            status="pending",
            created_at=now,
            updated_at=now,
            dependencies=[]
        )

class ImprovementTracker:
    """Manages system improvements."""
    
    def __init__(self, config_dir: Union[str, Path]):
        self.config_dir = Path(config_dir)
        self.improvements_file = self.config_dir / "improvements.json"
        self.logger = logging.getLogger(__name__)
        
        # Create improvements file if it doesn't exist
        if not self.improvements_file.exists():
            self.improvements_file.write_text("[]")
            
        self.improvements = self._load_improvements()
        
    def _load_improvements(self) -> List[Improvement]:
        """Load improvements from file."""
        try:
            with open(self.improvements_file, 'r') as f:
                data = json.load(f)
                return [Improvement(**item) for item in data]
        except Exception as e:
            self.logger.error(f"Error loading improvements: {e}")
            return []
            
    def _save_improvements(self):
        """Save improvements to file."""
        try:
            with open(self.improvements_file, 'w') as f:
                json.dump([asdict(imp) for imp in self.improvements], f, indent=2)
        except Exception as e:
            self.logger.error(f"Error saving improvements: {e}")
            raise
            
    def add_improvement(self, title: str, description: str, component: str, 
                       priority: str = "medium") -> Improvement:
        """Add a new improvement."""
        improvement = Improvement.create(title, description, component, priority)
        self.improvements.append(improvement)
        self._save_improvements()
        return improvement
        
    def update_status(self, id: str, status: str, test_results: Dict = None):
        """Update improvement status."""
        improvement = self.get_improvement(id)
        if not improvement:
            raise ValueError(f"Improvement not found: {id}")
            
        improvement.status = status
        improvement.updated_at = datetime.now().isoformat()
        
        if status == "completed":
            improvement.implemented_at = datetime.now().isoformat()
        elif status == "verified":
            improvement.verified_at = datetime.now().isoformat()
            
        if test_results:
            improvement.test_results = test_results
            
        self._save_improvements()
        
    def get_improvement(self, id: str) -> Optional[Improvement]:
        """Get improvement by ID."""
        return next((imp for imp in self.improvements if imp.id == id), None)
        
    def list_improvements(self, status: str = None, 
                         component: str = None) -> List[Improvement]:
        """List improvements with optional filtering."""
        improvements = self.improvements
        
        if status:
            improvements = [imp for imp in improvements if imp.status == status]
        if component:
            improvements = [imp for imp in improvements if imp.component == component]
            
        return improvements
        
    def add_dependency(self, id: str, dependency_id: str):
        """Add a dependency between improvements."""
        improvement = self.get_improvement(id)
        dependency = self.get_improvement(dependency_id)
        
        if not improvement or not dependency:
            raise ValueError("Improvement or dependency not found")
            
        if dependency_id not in improvement.dependencies:
            improvement.dependencies.append(dependency_id)
            self._save_improvements()
            
    def get_next_improvements(self) -> List[Improvement]:
        """Get improvements that are ready to be implemented."""
        ready = []
        
        for imp in self.improvements:
            if imp.status != "pending":
                continue
                
            # Check if all dependencies are completed
            deps_completed = all(
                self.get_improvement(dep_id).status == "completed"
                for dep_id in (imp.dependencies or [])
            )
            
            if deps_completed:
                ready.append(imp)
                
        # Sort by priority
        priority_order = {"high": 0, "medium": 1, "low": 2}
        ready.sort(key=lambda x: priority_order[x.priority])
        
        return ready
        
    def generate_report(self, output_file: Union[str, Path] = None) -> str:
        """Generate a report of improvements and their status."""
        now = datetime.now().isoformat()
        
        report = [
            f"Improvement Status Report - {now}",
            "=" * 50,
            ""
        ]
        
        # Summary statistics
        total = len(self.improvements)
        completed = len([imp for imp in self.improvements if imp.status == "completed"])
        verified = len([imp for imp in self.improvements if imp.status == "verified"])
        pending = len([imp for imp in self.improvements if imp.status == "pending"])
        in_progress = len([imp for imp in self.improvements if imp.status == "in_progress"])
        
        report.extend([
            "Summary:",
            f"Total Improvements: {total}",
            f"Completed: {completed}",
            f"Verified: {verified}",
            f"Pending: {pending}",
            f"In Progress: {in_progress}",
            "",
            "Details:",
            "-" * 50
        ])
        
        # Group by status
        for status in ["in_progress", "pending", "completed", "verified"]:
            improvements = self.list_improvements(status=status)
            if improvements:
                report.extend([
                    f"\n{status.upper()}:",
                    "-" * len(status)
                ])
                
                for imp in improvements:
                    report.extend([
                        f"\nID: {imp.id}",
                        f"Title: {imp.title}",
                        f"Component: {imp.component}",
                        f"Priority: {imp.priority}",
                        f"Created: {imp.created_at}",
                        f"Updated: {imp.updated_at}"
                    ])
                    if imp.dependencies:
                        report.append(f"Dependencies: {', '.join(imp.dependencies)}")
                    report.append("")
                    
        report_text = "\n".join(report)
        
        if output_file:
            Path(output_file).write_text(report_text)
            
        return report_text

def initialize_improvements(config_dir: Path):
    """Initialize improvement tracking with initial improvements."""
    tracker = ImprovementTracker(config_dir)
    
    # Add initial improvements if none exist
    if not tracker.improvements:
        # Template system improvements
        tracker.add_improvement(
            "Enhanced Error Handling",
            "Implement more detailed error messages and recovery mechanisms",
            "template_system",
            "high"
        )
        
        tracker.add_improvement(
            "Template Validation",
            "Add pre-generation validation of template parameters",
            "template_system",
            "medium"
        )
        
        # Configuration management improvements
        tracker.add_improvement(
            "Configuration Versioning",
            "Implement version control for configuration changes",
            "config_management",
            "high"
        )
        
        # Test system improvements
        tracker.add_improvement(
            "Performance Testing",
            "Add performance benchmarks to test suite",
            "testing",
            "medium"
        )
        
        tracker.add_improvement(
            "Integration Tests",
            "Add end-to-end integration tests",
            "testing",
            "high"
        )
        
    return tracker

if __name__ == "__main__":
    # Initialize tracker
    config_dir = Path("private/config")
    tracker = initialize_improvements(config_dir)
    
    # Generate and print report
    report = tracker.generate_report()
    print(report)
