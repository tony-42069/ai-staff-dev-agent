import unittest
from typing import Dict, Any
import ast
from private.config.code_analyzer import CodeAnalyzerCapability, CodeAnalysis

class TestCodeAnalyzer(unittest.TestCase):
    def setUp(self):
        self.analyzer = CodeAnalyzerCapability()
        self.sample_code = """
def example_function(x, y):
    z = x + y
    return z

class ExampleClass:
    def __init__(self):
        self.value = 0
    
    def increment(self):
        self.value += 1
"""
        self.invalid_code = """
def broken_function():
    x = 1
    return x + y  # undefined variable y
"""

    def test_initialization(self):
        """Test proper initialization of the analyzer"""
        self.assertEqual(self.analyzer.name, "code_analyzer")
        self.assertIsNotNone(self.analyzer.description)
        self.assertIsInstance(self.analyzer.requirements, list)
        self.assertIsInstance(self.analyzer.parameters, dict)

    def test_analyze_valid_code(self):
        """Test analysis of valid Python code"""
        result = self.analyzer.analyze_code(self.sample_code)
        self.assertIsInstance(result, CodeAnalysis)
        self.assertIsInstance(result.quality_score, float)
        self.assertGreaterEqual(result.quality_score, 0)
        self.assertLessEqual(result.quality_score, 10)
        self.assertIsInstance(result.issues, list)
        self.assertIsInstance(result.metrics, dict)
        self.assertIsInstance(result.suggestions, list)

    def test_analyze_invalid_code(self):
        """Test analysis of invalid Python code"""
        result = self.analyzer.analyze_code(self.invalid_code)
        self.assertIsInstance(result, CodeAnalysis)
        self.assertTrue(any(issue["type"] == "error" for issue in result.issues))

    def test_metrics_calculation(self):
        """Test calculation of code metrics"""
        result = self.analyzer.analyze_code(self.sample_code)
        metrics = result.metrics
        self.assertIn("num_classes", metrics)
        self.assertIn("num_methods", metrics)
        self.assertIn("num_imports", metrics)
        self.assertEqual(metrics["num_classes"], 1)  # ExampleClass
        self.assertEqual(metrics["num_methods"], 3)  # example_function, __init__, increment

    def test_execute_with_valid_task(self):
        """Test execution with valid task input"""
        task = {
            "code": self.sample_code,
            "parameters": {
                "max_complexity": 5,
                "min_quality_score": 8.0
            }
        }
        result = self.analyzer.execute(task)
        self.assertTrue(result["success"])
        self.assertIn("quality_score", result)
        self.assertIn("issues", result)
        self.assertIn("metrics", result)
        self.assertIn("suggestions", result)

    def test_execute_with_missing_code(self):
        """Test execution with missing code"""
        task = {
            "parameters": {
                "max_complexity": 5
            }
        }
        result = self.analyzer.execute(task)
        self.assertIn("error", result)
        self.assertEqual(result["error"], "No code provided for analysis")

    def test_parameter_override(self):
        """Test parameter override in execute"""
        original_max_complexity = self.analyzer.parameters["max_complexity"]
        task = {
            "code": self.sample_code,
            "parameters": {
                "max_complexity": 15
            }
        }
        self.analyzer.execute(task)
        self.assertEqual(self.analyzer.parameters["max_complexity"], 15)
        # Reset parameter
        self.analyzer.parameters["max_complexity"] = original_max_complexity

if __name__ == "__main__":
    unittest.main()
