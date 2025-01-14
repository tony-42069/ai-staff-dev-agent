#!/usr/bin/env python3
"""
Test Runner Script

This script runs the template system test suite and generates detailed test reports.
It supports various output formats and can be integrated into CI/CD pipelines.
"""

import unittest
import sys
import os
import time
import json
from datetime import datetime
from pathlib import Path
from unittest.runner import TextTestRunner
from unittest.result import TestResult
from test_suite import TestTemplateSystem

class DetailedTestResult(TestResult):
    """Extended test result class with timing and details."""
    
    def __init__(self):
        super().__init__()
        self.start_time = None
        self.test_results = []
        
    def startTest(self, test):
        self.start_time = time.time()
        super().startTest(test)
        
    def addSuccess(self, test):
        elapsed = time.time() - self.start_time
        self.test_results.append({
            'name': test.id(),
            'status': 'success',
            'time': elapsed
        })
        super().addSuccess(test)
        
    def addError(self, test, err):
        elapsed = time.time() - self.start_time
        self.test_results.append({
            'name': test.id(),
            'status': 'error',
            'time': elapsed,
            'error': {
                'type': err[0].__name__,
                'message': str(err[1])
            }
        })
        super().addError(test, err)
        
    def addFailure(self, test, err):
        elapsed = time.time() - self.start_time
        self.test_results.append({
            'name': test.id(),
            'status': 'failure',
            'time': elapsed,
            'error': {
                'type': err[0].__name__,
                'message': str(err[1])
            }
        })
        super().addFailure(test, err)

class DetailedTestRunner(TextTestRunner):
    """Test runner that uses DetailedTestResult."""
    
    def __init__(self, report_dir: Path, **kwargs):
        super().__init__(**kwargs)
        self.report_dir = report_dir
        self.report_dir.mkdir(parents=True, exist_ok=True)
        
    def _makeResult(self):
        return DetailedTestResult()
        
    def generate_report(self, result: DetailedTestResult, run_time: float):
        """Generate test report in multiple formats."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Generate JSON report
        json_report = {
            'timestamp': timestamp,
            'total_tests': result.testsRun,
            'failures': len(result.failures),
            'errors': len(result.errors),
            'run_time': run_time,
            'test_results': result.test_results
        }
        
        json_path = self.report_dir / f"test_report_{timestamp}.json"
        with open(json_path, 'w') as f:
            json.dump(json_report, f, indent=2)
            
        # Generate text report
        text_path = self.report_dir / f"test_report_{timestamp}.txt"
        with open(text_path, 'w') as f:
            f.write(f"Test Report - {timestamp}\n")
            f.write("=" * 50 + "\n\n")
            f.write(f"Total Tests: {result.testsRun}\n")
            f.write(f"Failures: {len(result.failures)}\n")
            f.write(f"Errors: {len(result.errors)}\n")
            f.write(f"Run Time: {run_time:.2f}s\n\n")
            
            f.write("Test Results:\n")
            f.write("-" * 50 + "\n")
            for test_result in result.test_results:
                f.write(f"\nTest: {test_result['name']}\n")
                f.write(f"Status: {test_result['status']}\n")
                f.write(f"Time: {test_result['time']:.2f}s\n")
                if 'error' in test_result:
                    f.write(f"Error Type: {test_result['error']['type']}\n")
                    f.write(f"Error Message: {test_result['error']['message']}\n")
                    
        return json_path, text_path

def run_tests(report_dir: Path = None):
    """
    Run the test suite and generate reports.
    
    Args:
        report_dir: Directory where test reports should be saved.
                   Defaults to 'test_reports' in the current directory.
    
    Returns:
        Tuple of (success: bool, report_paths: list)
    """
    if report_dir is None:
        report_dir = Path.cwd() / "test_reports"
        
    # Create test suite
    suite = unittest.TestLoader().loadTestsFromTestCase(TestTemplateSystem)
    
    # Run tests with detailed runner
    runner = DetailedTestRunner(
        report_dir,
        verbosity=2,
        stream=sys.stdout
    )
    
    start_time = time.time()
    result = runner.run(suite)
    run_time = time.time() - start_time
    
    # Generate reports
    json_path, text_path = runner.generate_report(result, run_time)
    
    success = result.wasSuccessful()
    return success, [json_path, text_path]

if __name__ == "__main__":
    success, report_paths = run_tests()
    print("\nTest reports generated:")
    for path in report_paths:
        print(f"- {path}")
    sys.exit(0 if success else 1)
