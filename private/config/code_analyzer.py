from typing import Dict, Any, List
from dataclasses import dataclass
import ast
import astroid
from pylint.lint import Run
from pylint.reporters import JSONReporter
import io
import sys
import re
from pathlib import Path

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
        # Run multiple analysis passes
        pylint_results = self._run_pylint_analysis(code)
        ast_metrics = self._calculate_ast_metrics(code)
        patterns = self._detect_patterns(code)
        suggestions = self._generate_suggestions(pylint_results, ast_metrics, patterns)
        
        # Calculate final quality score
        quality_score = self._calculate_quality_score(pylint_results, ast_metrics, patterns)
        
        return CodeAnalysis(
            quality_score=quality_score,
            issues=pylint_results,
            metrics={**ast_metrics, **patterns},
            suggestions=suggestions
        )

    def _run_pylint_analysis(self, code: str) -> List[Dict[str, Any]]:
        """Run pylint analysis on code"""
        pylint_output = io.StringIO()
        reporter = JSONReporter(pylint_output)
        
        # Create temporary file for pylint
        with Path('temp_code.py').open('w') as f:
            f.write(code)
        
        try:
            # Run pylint
            Run(['temp_code.py', '--output-format=json'], reporter=reporter, exit=False)
            
            # Parse results
            results = []
            for issue in ast.literal_eval(pylint_output.getvalue()):
                results.append({
                    "type": issue["type"],
                    "module": issue["module"],
                    "obj": issue["obj"],
                    "line": issue["line"],
                    "column": issue["column"],
                    "message": issue["message"],
                    "symbol": issue.get("symbol", "unknown")
                })
            return results
        except Exception as e:
            return [{
                "type": "error",
                "message": f"Pylint analysis failed: {str(e)}"
            }]
        finally:
            Path('temp_code.py').unlink(missing_ok=True)

    def _calculate_ast_metrics(self, code: str) -> Dict[str, Any]:
        """Calculate metrics using AST analysis"""
        try:
            module = astroid.parse(code)
            
            # Basic metrics
            metrics = {
                "num_classes": len(list(module.nodes_of_class(astroid.ClassDef))),
                "num_methods": len(list(module.nodes_of_class(astroid.FunctionDef))),
                "num_imports": len(list(module.nodes_of_class(astroid.Import))) + 
                              len(list(module.nodes_of_class(astroid.ImportFrom))),
                "lines_of_code": len(code.splitlines()),
                "comment_lines": len([l for l in code.splitlines() if l.strip().startswith('#')])
            }
            
            # Complexity metrics
            metrics.update(self._calculate_complexity_metrics(module))
            
            # Documentation metrics
            metrics.update(self._calculate_documentation_metrics(module))
            
            return metrics
        except Exception as e:
            return {"error": f"AST analysis failed: {str(e)}"}

    def _calculate_complexity_metrics(self, module: astroid.Module) -> Dict[str, Any]:
        """Calculate code complexity metrics"""
        metrics = {
            "max_depth": 0,
            "max_complexity": 0,
            "total_complexity": 0,
            "num_branches": 0
        }
        
        for node in module.nodes_of_class((astroid.FunctionDef, astroid.MethodDef)):
            # Calculate cyclomatic complexity
            complexity = 1  # Base complexity
            complexity += len([n for n in node.nodes_of_class(astroid.If)])
            complexity += len([n for n in node.nodes_of_class(astroid.For)])
            complexity += len([n for n in node.nodes_of_class(astroid.While)])
            complexity += len([n for n in node.nodes_of_class(astroid.ExceptHandler)])
            
            metrics["max_complexity"] = max(metrics["max_complexity"], complexity)
            metrics["total_complexity"] += complexity
            
            # Calculate nesting depth
            depth = 0
            current = node
            while current.parent:
                if isinstance(current.parent, (astroid.FunctionDef, astroid.ClassDef)):
                    depth += 1
                current = current.parent
            metrics["max_depth"] = max(metrics["max_depth"], depth)
            
            # Count branches
            metrics["num_branches"] += len(list(node.nodes_of_class((
                astroid.If, astroid.For, astroid.While, astroid.ExceptHandler
            ))))
        
        return metrics

    def _calculate_documentation_metrics(self, module: astroid.Module) -> Dict[str, Any]:
        """Calculate documentation coverage metrics"""
        metrics = {
            "documented_classes": 0,
            "documented_methods": 0,
            "total_classes": 0,
            "total_methods": 0
        }
        
        for node in module.nodes_of_class(astroid.ClassDef):
            metrics["total_classes"] += 1
            if node.doc:
                metrics["documented_classes"] += 1
            
            for method in node.nodes_of_class(astroid.FunctionDef):
                metrics["total_methods"] += 1
                if method.doc:
                    metrics["documented_methods"] += 1
        
        # Calculate percentages
        metrics["class_documentation_rate"] = (
            (metrics["documented_classes"] / metrics["total_classes"] * 100)
            if metrics["total_classes"] > 0 else 100
        )
        metrics["method_documentation_rate"] = (
            (metrics["documented_methods"] / metrics["total_methods"] * 100)
            if metrics["total_methods"] > 0 else 100
        )
        
        return metrics

    def _detect_patterns(self, code: str) -> Dict[str, Any]:
        """Detect code patterns and anti-patterns"""
        patterns = {
            "patterns_found": [],
            "anti_patterns_found": []
        }
        
        # Good patterns
        if re.search(r'def\s+__init__\s*\(self', code):
            patterns["patterns_found"].append("proper_class_initialization")
        
        if re.search(r'class\s+\w+\([\w\s,]+\):', code):
            patterns["patterns_found"].append("inheritance_used")
        
        if re.search(r'try\s*:', code) and re.search(r'except\s+\w+\s+as\s+\w+:', code):
            patterns["patterns_found"].append("proper_exception_handling")
        
        if re.search(r'with\s+[\w\s\(\)]+:', code):
            patterns["patterns_found"].append("context_manager_used")
        
        if re.search(r'@property', code):
            patterns["patterns_found"].append("property_decorator_used")
        
        # Anti-patterns
        if re.search(r'except\s*:', code):
            patterns["anti_patterns_found"].append("bare_except")
        
        if re.search(r'global\s+\w+', code):
            patterns["anti_patterns_found"].append("global_variable_used")
        
        if re.search(r'\w+\s*=\s*\[\];\s*for\s+', code):
            patterns["anti_patterns_found"].append("list_comprehension_alternative")
        
        if re.search(r'print\s*\(', code):
            patterns["anti_patterns_found"].append("print_for_debugging")
        
        return patterns

    def _generate_suggestions(
        self,
        pylint_results: List[Dict[str, Any]],
        ast_metrics: Dict[str, Any],
        patterns: Dict[str, Any]
    ) -> List[str]:
        """Generate improvement suggestions based on analysis results"""
        suggestions = []
        
        # Complexity suggestions
        if ast_metrics.get("max_complexity", 0) > self.parameters["max_complexity"]:
            suggestions.append(
                f"High complexity detected (score: {ast_metrics['max_complexity']}). "
                "Consider breaking down complex functions into smaller ones."
            )
        
        if ast_metrics.get("max_depth", 0) > 3:
            suggestions.append(
                f"Deep nesting detected (depth: {ast_metrics['max_depth']}). "
                "Consider restructuring deeply nested code."
            )
        
        # Documentation suggestions
        doc_rate = ast_metrics.get("method_documentation_rate", 0)
        if doc_rate < 80:
            suggestions.append(
                f"Low documentation coverage ({doc_rate:.1f}%). "
                "Consider adding docstrings to undocumented methods."
            )
        
        # Pattern-based suggestions
        for anti_pattern in patterns.get("anti_patterns_found", []):
            if anti_pattern == "bare_except":
                suggestions.append(
                    "Avoid bare 'except' clauses. "
                    "Catch specific exceptions instead."
                )
            elif anti_pattern == "global_variable_used":
                suggestions.append(
                    "Global variables detected. "
                    "Consider using class attributes or function parameters instead."
                )
            elif anti_pattern == "list_comprehension_alternative":
                suggestions.append(
                    "List building with loop detected. "
                    "Consider using list comprehension for better readability."
                )
            elif anti_pattern == "print_for_debugging":
                suggestions.append(
                    "Print statements detected. "
                    "Consider using proper logging for debugging."
                )
        
        # Pylint-based suggestions
        error_count = len([r for r in pylint_results if r["type"] in ("error", "warning")])
        if error_count > 0:
            suggestions.append(
                f"Found {error_count} potential issues. "
                "Review the detailed findings in the issues list."
            )
        
        return suggestions

    def _calculate_quality_score(
        self,
        pylint_results: List[Dict[str, Any]],
        ast_metrics: Dict[str, Any],
        patterns: Dict[str, Any]
    ) -> float:
        """Calculate overall code quality score (0-10)"""
        score = 10.0  # Start with perfect score
        
        # Deduct for pylint issues
        error_count = len([r for r in pylint_results if r["type"] == "error"])
        warning_count = len([r for r in pylint_results if r["type"] == "warning"])
        score -= error_count * 1.0  # -1.0 for each error
        score -= warning_count * 0.5  # -0.5 for each warning
        
        # Deduct for complexity
        if (max_complexity := ast_metrics.get("max_complexity", 0)) > self.parameters["max_complexity"]:
            score -= (max_complexity - self.parameters["max_complexity"]) * 0.3
        
        # Deduct for documentation
        doc_rate = ast_metrics.get("method_documentation_rate", 0)
        if doc_rate < 80:
            score -= (80 - doc_rate) / 20  # -1.0 for every 20% below 80%
        
        # Deduct for anti-patterns
        score -= len(patterns.get("anti_patterns_found", [])) * 0.5
        
        # Add bonus for good patterns
        score += len(patterns.get("patterns_found", [])) * 0.2
        
        # Ensure score stays within bounds
        return max(0.0, min(10.0, score))

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
                "status": "error",
                "message": "No code provided for analysis"
            }

        # Update parameters with any task-specific ones
        self.parameters.update(task.get("parameters", {}))

        try:
            analysis = self.analyze_code(code)
            return {
                "status": "success",
                "quality_score": analysis.quality_score,
                "issues": analysis.issues,
                "metrics": analysis.metrics,
                "suggestions": analysis.suggestions
            }
        except Exception as e:
            return {
                "status": "error",
                "message": f"Analysis failed: {str(e)}"
            }
