from typing import Dict, Any, List
from dataclasses import dataclass
import ast
import astroid
from pylint.lint import Run
from pylint.reporters import JSONReporter
import io
import sys
import json

@dataclass
class CodeAnalysis:
    """Data class for storing code analysis results"""
    quality_score: float
    issues: List[Dict[str, Any]]
    metrics: Dict[str, Any]
    suggestions: List[str]

class CodeAnalyzerCapability:
    """Capability for performing static code analysis"""
    
    def __init__(self):
        self.name = "code_analyzer"
        self.description = "Performs static code analysis to identify issues and suggest improvements"
        self.requirements = [
            {
                "name": "astroid",
                "type": "package",
                "version": ">=2.14.0"
            },
            {
                "name": "pylint",
                "type": "package", 
                "version": ">=2.17.0"
            }
        ]
        self.parameters = {
            "max_complexity": 10,
            "min_quality_score": 7.0,
            "ignore_patterns": ["*_test.py", "test_*.py"]
        }

    def analyze_code(self, code: str) -> CodeAnalysis:
        """
        Analyze code using multiple static analysis tools
        
        Args:
            code: String containing Python code to analyze
            
        Returns:
            CodeAnalysis object containing analysis results
        """
        # Capture pylint output
        pylint_output = io.StringIO()
        reporter = JSONReporter(pylint_output)
        
        # Write code to a temporary file for pylint analysis
        import tempfile
        import os
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as temp_file:
            temp_file.write(code)
            temp_file.flush()
            temp_path = temp_file.name
        
        try:
            # Run pylint analysis on the temporary file
            Run([temp_path, "--output-format=json", "--reports=n"], reporter=reporter, exit=False)
            
            # Parse pylint output line by line
            pylint_issues = []
            for line in pylint_output.getvalue().splitlines():
                line = line.strip()
                if not line:
                    continue
                try:
                    # Parse each line as a separate JSON object
                    issue_data = json.loads(line)
                    # Keep original error type or convert based on message ID
                    issue_type = issue_data.get("type", "unknown")
                    if issue_data.get("message-id", "").startswith("E"):
                        issue_type = "error"
                    elif issue_data.get("symbol") in ["undefined-variable", "syntax-error"]:
                        issue_type = "error"
                    
                    pylint_issues.append({
                        "type": issue_type,
                        "module": issue_data.get("module", ""),
                        "obj": issue_data.get("obj", ""),
                        "line": int(issue_data.get("line", 0)),
                        "column": int(issue_data.get("column", 0)),
                        "message": issue_data.get("message", "")
                    })
                except json.JSONDecodeError:
                    continue  # Skip invalid JSON lines
        finally:
            # Clean up temporary file
            os.unlink(temp_path)

        # Calculate metrics using astroid
        try:
            module = astroid.parse(code)
            metrics = {
                "num_classes": len(list(module.nodes_of_class(astroid.ClassDef))),
                "num_methods": len(list(module.nodes_of_class(astroid.FunctionDef))),
                "num_imports": len(list(module.nodes_of_class(astroid.Import))) + 
                              len(list(module.nodes_of_class(astroid.ImportFrom)))
            }
        except Exception as e:
            metrics = {
                "error": f"Error calculating metrics: {str(e)}"
            }

        # Generate improvement suggestions
        suggestions = []
        for issue in pylint_issues:
            if issue["type"] in ["error", "warning"]:
                suggestions.append(f"Line {issue['line']}: {issue['message']}")

        # Calculate quality score (0-10 scale)
        total_issues = len(pylint_issues)
        quality_score = float(max(0, min(10, 10 - (total_issues * 0.5))))

        return CodeAnalysis(
            quality_score=quality_score,
            issues=pylint_issues,
            metrics=metrics,
            suggestions=suggestions
        )

    def execute(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute the code analysis capability
        
        Args:
            task: Dictionary containing:
                - code: String of code to analyze
                - parameters: Optional dict of analysis parameters
                
        Returns:
            Dictionary containing analysis results
        """
        code = task.get("code")
        if not code:
            return {
                "error": "No code provided for analysis"
            }

        # Update parameters with any task-specific ones
        parameters = task.get("parameters", {})
        self.parameters.update(parameters)

        try:
            analysis = self.analyze_code(code)
            return {
                "success": True,
                "quality_score": analysis.quality_score,
                "issues": analysis.issues,
                "metrics": analysis.metrics,
                "suggestions": analysis.suggestions
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Analysis failed: {str(e)}"
            }
