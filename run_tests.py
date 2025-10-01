#!/usr/bin/env python3
"""
Test runner script for the movie recap service.
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
    print(f"{'='*60}")
    
    result = subprocess.run(command, shell=True, capture_output=True, text=True)
    
    if result.stdout:
        print("STDOUT:")
        print(result.stdout)
    
    if result.stderr:
        print("STDERR:")
        print(result.stderr)
    
    if result.returncode != 0:
        print(f"❌ FAILED: {description}")
        return False
    else:
        print(f"✅ PASSED: {description}")
        return True


def setup_test_environment():
    """Set up the test environment."""
    print("Setting up test environment...")
    
    # Install test dependencies
    commands = [
        ("pip install -r requirements-test.txt", "Install test dependencies"),
        ("pip install -r backend/requirements.txt", "Install main dependencies"),
    ]
    
    for command, description in commands:
        if not run_command(command, description):
            return False
    
    return True


def run_unit_tests():
    """Run unit tests."""
    print("\n🧪 Running unit tests...")
    
    commands = [
        ("pytest tests/test_auth.py -v", "Authentication tests"),
        ("pytest tests/test_workers.py -v", "Worker tests"),
        ("pytest tests/test_api_endpoints.py -v -k 'not integration'", "API unit tests"),
    ]
    
    results = []
    for command, description in commands:
        results.append(run_command(command, description))
    
    return all(results)


def run_integration_tests():
    """Run integration tests."""
    print("\n🔗 Running integration tests...")
    
    commands = [
        ("pytest tests/ -v -m integration", "Integration tests"),
    ]
    
    results = []
    for command, description in commands:
        results.append(run_command(command, description))
    
    return all(results)


def run_load_tests():
    """Run load tests."""
    print("\n⚡ Running load tests...")
    
    # Start the application in background (would need actual implementation)
    print("Note: Load tests require the application to be running.")
    print("Start the application with: uvicorn app.main:app --host 0.0.0.0 --port 8000")
    print("Then run: locust -f tests/load_test.py --host=http://localhost:8000")
    
    return True


def run_code_quality_checks():
    """Run code quality checks."""
    print("\n🔍 Running code quality checks...")
    
    commands = [
        ("black --check backend/app/", "Code formatting check (Black)"),
        ("isort --check-only backend/app/", "Import sorting check (isort)"),
        ("flake8 backend/app/", "Linting check (flake8)"),
        ("mypy backend/app/", "Type checking (mypy)"),
        ("bandit -r backend/app/", "Security check (bandit)"),
        ("safety check", "Dependency security check (safety)"),
    ]
    
    results = []
    for command, description in commands:
        results.append(run_command(command, description))
    
    return all(results)


def generate_coverage_report():
    """Generate test coverage report."""
    print("\n📊 Generating coverage report...")
    
    commands = [
        ("pytest tests/ --cov=backend/app --cov-report=html --cov-report=term", "Generate coverage report"),
    ]
    
    results = []
    for command, description in commands:
        results.append(run_command(command, description))
    
    if results and all(results):
        print("\n📋 Coverage report generated in htmlcov/index.html")
    
    return all(results)


def run_docker_tests():
    """Run tests in Docker environment."""
    print("\n🐳 Running Docker tests...")
    
    commands = [
        ("docker-compose -f docker-compose.test.yml build", "Build test containers"),
        ("docker-compose -f docker-compose.test.yml up --abort-on-container-exit", "Run tests in containers"),
        ("docker-compose -f docker-compose.test.yml down", "Clean up test containers"),
    ]
    
    results = []
    for command, description in commands:
        results.append(run_command(command, description))
    
    return all(results)


def main():
    """Main test runner function."""
    parser = argparse.ArgumentParser(description="Test runner for movie recap service")
    parser.add_argument("--setup", action="store_true", help="Set up test environment")
    parser.add_argument("--unit", action="store_true", help="Run unit tests")
    parser.add_argument("--integration", action="store_true", help="Run integration tests")
    parser.add_argument("--load", action="store_true", help="Run load tests")
    parser.add_argument("--quality", action="store_true", help="Run code quality checks")
    parser.add_argument("--coverage", action="store_true", help="Generate coverage report")
    parser.add_argument("--docker", action="store_true", help="Run tests in Docker")
    parser.add_argument("--all", action="store_true", help="Run all tests and checks")
    
    args = parser.parse_args()
    
    # Default to running all if no specific options provided
    if not any([args.setup, args.unit, args.integration, args.load, args.quality, args.coverage, args.docker]):
        args.all = True
    
    results = []
    
    if args.setup or args.all:
        results.append(setup_test_environment())
    
    if args.unit or args.all:
        results.append(run_unit_tests())
    
    if args.integration or args.all:
        results.append(run_integration_tests())
    
    if args.quality or args.all:
        results.append(run_code_quality_checks())
    
    if args.coverage or args.all:
        results.append(generate_coverage_report())
    
    if args.load:
        results.append(run_load_tests())
    
    if args.docker:
        results.append(run_docker_tests())
    
    # Summary
    print(f"\n{'='*60}")
    print("TEST SUMMARY")
    print(f"{'='*60}")
    
    if all(results):
        print("🎉 ALL TESTS PASSED!")
        return 0
    else:
        print("❌ SOME TESTS FAILED!")
        return 1


if __name__ == "__main__":
    sys.exit(main())