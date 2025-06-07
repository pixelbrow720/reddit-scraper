#!/usr/bin/env python3
"""
Test runner for Reddit Scraper
Runs all tests with coverage reporting and performance analysis.
"""

import os
import sys
import subprocess
import argparse
from pathlib import Path

def run_command(command, description):
    """Run a command and handle errors."""
    print(f"\n{'='*60}")
    print(f"Running: {description}")
    print(f"Command: {command}")
    print('='*60)
    
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(result.stdout)
        if result.stderr:
            print("STDERR:", result.stderr)
        return True
    except subprocess.CalledProcessError as e:
        print(f"ERROR: {description} failed!")
        print(f"Return code: {e.returncode}")
        print(f"STDOUT: {e.stdout}")
        print(f"STDERR: {e.stderr}")
        return False

def install_dependencies():
    """Install test dependencies."""
    print("Installing test dependencies...")
    
    commands = [
        "pip install -r requirements.txt",
        "pip install -r requirements-dev.txt"
    ]
    
    for cmd in commands:
        if not run_command(cmd, f"Installing dependencies: {cmd}"):
            return False
    
    return True

def run_unit_tests():
    """Run unit tests with coverage."""
    print("\nRunning unit tests with coverage...")
    
    # Create coverage directory
    os.makedirs("htmlcov", exist_ok=True)
    
    command = "python -m pytest tests/ -v --cov=src --cov-report=html --cov-report=term-missing --cov-report=xml"
    return run_command(command, "Unit tests with coverage")

def run_specific_tests(test_pattern):
    """Run specific tests matching pattern."""
    command = f"python -m pytest tests/ -v -k '{test_pattern}'"
    return run_command(command, f"Tests matching pattern: {test_pattern}")

def run_performance_tests():
    """Run performance-specific tests."""
    command = "python -m pytest tests/test_performance.py -v -m performance"
    return run_command(command, "Performance tests")

def run_integration_tests():
    """Run integration tests."""
    command = "python -m pytest tests/test_integration.py -v -m integration"
    return run_command(command, "Integration tests")

def run_linting():
    """Run code linting and formatting checks."""
    print("\nRunning code quality checks...")
    
    checks = [
        ("flake8 src/ --max-line-length=100 --ignore=E203,W503", "Flake8 linting"),
        ("black --check src/ tests/", "Black formatting check"),
        ("isort --check-only src/ tests/", "Import sorting check"),
        ("mypy src/ --ignore-missing-imports", "Type checking")
    ]
    
    all_passed = True
    for command, description in checks:
        if not run_command(command, description):
            all_passed = False
    
    return all_passed

def fix_formatting():
    """Fix code formatting issues."""
    print("\nFixing code formatting...")
    
    fixes = [
        ("black src/ tests/", "Black formatting"),
        ("isort src/ tests/", "Import sorting")
    ]
    
    for command, description in fixes:
        run_command(command, description)

def generate_test_report():
    """Generate comprehensive test report."""
    print("\nGenerating test report...")
    
    # Run tests with detailed output
    command = "python -m pytest tests/ --html=test_report.html --self-contained-html --cov=src --cov-report=html"
    return run_command(command, "Generating test report")

def run_security_checks():
    """Run security checks."""
    print("\nRunning security checks...")
    
    # Install safety if not available
    run_command("pip install safety", "Installing safety")
    
    # Check for known vulnerabilities
    command = "safety check"
    return run_command(command, "Security vulnerability check")

def run_benchmark_tests():
    """Run benchmark tests."""
    print("\nRunning benchmark tests...")
    
    # Create a simple benchmark script
    benchmark_script = """
import time
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.core.performance_monitor import PerformanceMonitor
from src.processors.post_processor import PostProcessor

def benchmark_post_processing():
    monitor = PerformanceMonitor(save_to_file=False)
    processor = PostProcessor()
    
    # Generate test data
    posts = []
    for i in range(1000):
        posts.append({
            'id': f'post_{i}',
            'title': f'Test Post {i}',
            'author': f'user_{i % 100}',
            'score': i * 10,
            'num_comments': i * 2,
            'created_utc': 1640995200 + i,
            'selftext': f'Content for post {i}',
            'is_nsfw': i % 10 == 0,
            'is_self': True
        })
    
    # Benchmark filtering
    op_id = monitor.start_operation('filter_posts')
    filtered = processor.filter_posts(posts)
    metrics = monitor.end_operation(op_id, success=True)
    
    print(f"Filtered {len(posts)} posts to {len(filtered)} in {metrics.duration:.3f}s")
    print(f"Processing rate: {len(posts) / metrics.duration:.1f} posts/second")
    
    # Benchmark derived fields
    op_id = monitor.start_operation('add_derived_fields')
    enhanced = processor.add_derived_fields(filtered)
    metrics = monitor.end_operation(op_id, success=True)
    
    print(f"Enhanced {len(filtered)} posts in {metrics.duration:.3f}s")
    print(f"Enhancement rate: {len(filtered) / metrics.duration:.1f} posts/second")

if __name__ == '__main__':
    benchmark_post_processing()
    """
    
    # Write benchmark script
    with open('benchmark_temp.py', 'w') as f:
        f.write(benchmark_script)
    
    try:
        result = run_command("python benchmark_temp.py", "Benchmark tests")
        return result
    finally:
        # Clean up
        if os.path.exists('benchmark_temp.py'):
            os.remove('benchmark_temp.py')

def main():
    """Main test runner function."""
    parser = argparse.ArgumentParser(description='Reddit Scraper Test Runner')
    parser.add_argument('--install-deps', action='store_true', help='Install test dependencies')
    parser.add_argument('--unit', action='store_true', help='Run unit tests')
    parser.add_argument('--integration', action='store_true', help='Run integration tests')
    parser.add_argument('--performance', action='store_true', help='Run performance tests')
    parser.add_argument('--lint', action='store_true', help='Run linting checks')
    parser.add_argument('--fix', action='store_true', help='Fix formatting issues')
    parser.add_argument('--security', action='store_true', help='Run security checks')
    parser.add_argument('--benchmark', action='store_true', help='Run benchmark tests')
    parser.add_argument('--report', action='store_true', help='Generate test report')
    parser.add_argument('--all', action='store_true', help='Run all tests and checks')
    parser.add_argument('--pattern', type=str, help='Run tests matching pattern')
    
    args = parser.parse_args()
    
    # If no specific arguments, run basic tests
    if not any(vars(args).values()):
        args.unit = True
    
    success = True
    
    try:
        if args.install_deps or args.all:
            if not install_dependencies():
                success = False
        
        if args.fix:
            fix_formatting()
        
        if args.lint or args.all:
            if not run_linting():
                success = False
        
        if args.unit or args.all:
            if not run_unit_tests():
                success = False
        
        if args.integration or args.all:
            if not run_integration_tests():
                success = False
        
        if args.performance or args.all:
            if not run_performance_tests():
                success = False
        
        if args.pattern:
            if not run_specific_tests(args.pattern):
                success = False
        
        if args.security or args.all:
            if not run_security_checks():
                success = False
        
        if args.benchmark or args.all:
            if not run_benchmark_tests():
                success = False
        
        if args.report or args.all:
            if not generate_test_report():
                success = False
        
        # Print summary
        print("\n" + "="*60)
        if success:
            print("🎉 ALL TESTS PASSED!")
            print("\nTest artifacts generated:")
            if os.path.exists("htmlcov/index.html"):
                print(f"  📊 Coverage report: {os.path.abspath('htmlcov/index.html')}")
            if os.path.exists("test_report.html"):
                print(f"  📋 Test report: {os.path.abspath('test_report.html')}")
        else:
            print("❌ SOME TESTS FAILED!")
            print("Check the output above for details.")
        print("="*60)
        
        return 0 if success else 1
        
    except KeyboardInterrupt:
        print("\n\nTests interrupted by user.")
        return 1
    except Exception as e:
        print(f"\n\nUnexpected error: {e}")
        return 1

if __name__ == '__main__':
    sys.exit(main())