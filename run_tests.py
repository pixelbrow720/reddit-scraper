#!/usr/bin/env python3
"""
Reddit Scraper Test Runner
Comprehensive testing and code quality checks
"""

import os
import sys
import subprocess
import argparse
from pathlib import Path
import time

def run_command(cmd, description, check=True):
    """Run a command and handle output."""
    print(f"\n🔄 {description}")
    print(f"Command: {' '.join(cmd)}")
    print("-" * 50)
    
    start_time = time.time()
    
    try:
        result = subprocess.run(cmd, check=check, capture_output=False)
        duration = time.time() - start_time
        
        if result.returncode == 0:
            print(f"✅ {description} completed successfully ({duration:.2f}s)")
        else:
            print(f"❌ {description} failed ({duration:.2f}s)")
        
        return result.returncode == 0
    except subprocess.CalledProcessError as e:
        duration = time.time() - start_time
        print(f"❌ {description} failed with exit code {e.returncode} ({duration:.2f}s)")
        return False
    except FileNotFoundError:
        print(f"❌ Command not found: {cmd[0]}")
        print(f"💡 Please install: pip install {cmd[0]}")
        return False

def check_dependencies():
    """Check if required tools are installed."""
    tools = {
        'pytest': 'pytest',
        'black': 'black',
        'flake8': 'flake8',
        'mypy': 'mypy',
        'bandit': 'bandit',
        'safety': 'safety'
    }
    
    missing = []
    for tool, package in tools.items():
        try:
            subprocess.run([tool, '--version'], capture_output=True, check=True)
        except (subprocess.CalledProcessError, FileNotFoundError):
            missing.append(package)
    
    if missing:
        print(f"❌ Missing tools: {', '.join(missing)}")
        print(f"💡 Install with: pip install {' '.join(missing)}")
        return False
    
    return True

def run_unit_tests():
    """Run unit tests."""
    cmd = [
        'pytest', 
        'tests/', 
        '-v',
        '--tb=short',
        '--durations=10'
    ]
    return run_command(cmd, "Running unit tests")

def run_integration_tests():
    """Run integration tests."""
    cmd = [
        'pytest', 
        'tests/test_integration.py', 
        '-v',
        '--tb=short'
    ]
    return run_command(cmd, "Running integration tests")

def run_performance_tests():
    """Run performance tests."""
    cmd = [
        'pytest', 
        'tests/test_performance.py', 
        '-v',
        '--tb=short'
    ]
    return run_command(cmd, "Running performance tests")

def run_coverage():
    """Run tests with coverage."""
    cmd = [
        'pytest', 
        'tests/', 
        '--cov=src',
        '--cov-report=html',
        '--cov-report=term-missing',
        '--cov-fail-under=80'
    ]
    
    success = run_command(cmd, "Running tests with coverage")
    
    if success:
        print("\n📊 Coverage report generated in htmlcov/index.html")
    
    return success

def run_linting():
    """Run code linting."""
    success = True
    
    # Flake8
    cmd = ['flake8', 'src/', 'tests/', '--max-line-length=100', '--extend-ignore=E203,W503']
    success &= run_command(cmd, "Running Flake8 linting")
    
    # Black check
    cmd = ['black', '--check', '--diff', 'src/', 'tests/']
    success &= run_command(cmd, "Checking code formatting with Black", check=False)
    
    return success

def run_type_checking():
    """Run type checking with MyPy."""
    cmd = ['mypy', 'src/', '--ignore-missing-imports']
    return run_command(cmd, "Running type checking with MyPy", check=False)

def run_security_scan():
    """Run security scanning."""
    success = True
    
    # Bandit
    cmd = ['bandit', '-r', 'src/', '-f', 'json', '-o', 'bandit-report.json']
    success &= run_command(cmd, "Running Bandit security scan", check=False)
    
    # Safety
    cmd = ['safety', 'check', '--json', '--output', 'safety-report.json']
    success &= run_command(cmd, "Running Safety dependency scan", check=False)
    
    return success

def format_code():
    """Format code with Black and isort."""
    success = True
    
    # Black formatting
    cmd = ['black', 'src/', 'tests/']
    success &= run_command(cmd, "Formatting code with Black")
    
    # isort
    try:
        cmd = ['isort', 'src/', 'tests/']
        success &= run_command(cmd, "Sorting imports with isort")
    except FileNotFoundError:
        print("💡 isort not found, skipping import sorting")
    
    return success

def run_frontend_tests():
    """Run frontend tests."""
    frontend_dir = Path("frontend")
    
    if not frontend_dir.exists():
        print("⚠️  Frontend directory not found, skipping frontend tests")
        return True
    
    # Check if node_modules exists
    node_modules = frontend_dir / "node_modules"
    if not node_modules.exists():
        print("📦 Installing frontend dependencies...")
        cmd = ['npm', 'install']
        if not run_command(cmd, "Installing frontend dependencies"):
            return False
    
    # Run tests
    cmd = ['npm', 'test', '--', '--coverage', '--watchAll=false']
    return run_command(cmd, "Running frontend tests")

def generate_test_report():
    """Generate comprehensive test report."""
    print("\n📋 Generating test report...")
    
    report_content = f"""
# Reddit Scraper Test Report

Generated on: {time.strftime('%Y-%m-%d %H:%M:%S')}

## Test Results

### Unit Tests
- Location: tests/
- Framework: pytest
- Coverage: See htmlcov/index.html

### Integration Tests  
- Location: tests/test_integration.py
- Tests end-to-end workflows

### Performance Tests
- Location: tests/test_performance.py
- Benchmarks scraping performance

### Frontend Tests
- Location: frontend/src/
- Framework: Jest + React Testing Library

## Code Quality

### Linting (Flake8)
- Max line length: 100
- Ignored: E203, W503

### Formatting (Black)
- Line length: 100
- Target Python versions: 3.9+

### Type Checking (MyPy)
- Strict mode enabled
- Missing imports ignored

### Security Scanning
- Bandit: Static security analysis
- Safety: Dependency vulnerability scan

## Reports Generated

- Coverage: htmlcov/index.html
- Bandit: bandit-report.json
- Safety: safety-report.json

## Running Tests

```bash
# All tests
python run_tests.py --all

# Specific test types
python run_tests.py --unit
python run_tests.py --integration
python run_tests.py --performance

# Code quality
python run_tests.py --lint
python run_tests.py --security
python run_tests.py --format
```
"""
    
    with open("TEST_REPORT.md", "w") as f:
        f.write(report_content)
    
    print("✅ Test report generated: TEST_REPORT.md")

def main():
    """Main test runner function."""
    parser = argparse.ArgumentParser(description="Reddit Scraper Test Runner")
    parser.add_argument('--all', action='store_true', help='Run all tests and checks')
    parser.add_argument('--unit', action='store_true', help='Run unit tests')
    parser.add_argument('--integration', action='store_true', help='Run integration tests')
    parser.add_argument('--performance', action='store_true', help='Run performance tests')
    parser.add_argument('--frontend', action='store_true', help='Run frontend tests')
    parser.add_argument('--coverage', action='store_true', help='Run tests with coverage')
    parser.add_argument('--lint', action='store_true', help='Run linting')
    parser.add_argument('--type-check', action='store_true', help='Run type checking')
    parser.add_argument('--security', action='store_true', help='Run security scans')
    parser.add_argument('--format', action='store_true', help='Format code')
    parser.add_argument('--report', action='store_true', help='Generate test report')
    parser.add_argument('--check-deps', action='store_true', help='Check dependencies')
    
    args = parser.parse_args()
    
    # If no specific tests specified, show help
    if not any(vars(args).values()):
        parser.print_help()
        return
    
    print("🧪 Reddit Scraper Test Runner")
    print("=" * 50)
    
    # Check dependencies
    if args.check_deps or args.all:
        if not check_dependencies():
            print("\n❌ Missing dependencies. Please install required tools.")
            return 1
    
    success = True
    start_time = time.time()
    
    # Run tests
    if args.unit or args.all:
        success &= run_unit_tests()
    
    if args.integration or args.all:
        success &= run_integration_tests()
    
    if args.performance or args.all:
        success &= run_performance_tests()
    
    if args.frontend or args.all:
        success &= run_frontend_tests()
    
    if args.coverage or args.all:
        success &= run_coverage()
    
    # Code quality checks
    if args.lint or args.all:
        success &= run_linting()
    
    if args.type_check or args.all:
        success &= run_type_checking()
    
    if args.security or args.all:
        success &= run_security_scan()
    
    # Code formatting
    if args.format:
        success &= format_code()
    
    # Generate report
    if args.report or args.all:
        generate_test_report()
    
    # Summary
    total_time = time.time() - start_time
    print("\n" + "=" * 50)
    print(f"🏁 Test run completed in {total_time:.2f} seconds")
    
    if success:
        print("✅ All tests and checks passed!")
        return 0
    else:
        print("❌ Some tests or checks failed!")
        return 1

if __name__ == "__main__":
    sys.exit(main())