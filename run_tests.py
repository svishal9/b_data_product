#!/usr/bin/env python3
"""
Test runner script for SCB Atlas entity types tests.

Provides convenient commands to run different test suites and generate reports.
"""

import subprocess
import sys
from pathlib import Path


def run_command(command, description):
    """Run a shell command and report results."""
    print(f"\n{'='*80}")
    print(f"▶ {description}")
    print(f"{'='*80}\n")
    print(f"Command: {' '.join(command)}\n")
    
    result = subprocess.run(command, cwd=Path(__file__).parent)
    
    if result.returncode == 0:
        print(f"\n✅ {description} - PASSED")
    else:
        print(f"\n❌ {description} - FAILED")
    
    return result.returncode == 0


def main():
    """Main test runner function."""
    
    if len(sys.argv) < 2:
        print_help()
        sys.exit(1)
    
    command = sys.argv[1]
    
    if command == "all":
        # Run all tests
        success = run_command(
            ["python", "-m", "pytest", "-s", "tests/", "-v"],
            "Running all tests"
        )
    
    elif command == "unit":
        # Run unit tests only
        success = run_command(
            ["python", "-m", "pytest", "tests/unit/", "-v"],
            "Running unit tests"
        )
    
    elif command == "integration":
        # Run integration tests only
        success = run_command(
            ["python", "-m", "pytest", "tests/integration/", "-v"],
            "Running integration tests"
        )
    
    elif command == "builders":
        # Run entity builders tests
        success = run_command(
            ["python", "-m", "pytest", "tests/unit/test_entity_builders.py", "-v"],
            "Running entity builders tests"
        )
    
    elif command == "types":
        # Run type definitions tests
        success = run_command(
            ["python", "-m", "pytest", "tests/unit/test_atlas_types.py", "-v"],
            "Running type definitions tests"
        )
    
    elif command == "services":
        # Run service functions tests
        success = run_command(
            ["python", "-m", "pytest", "tests/integration/test_entity_services.py", "-v"],
            "Running entity service tests"
        )
    
    elif command == "coverage":
        # Run tests with coverage report
        success = run_command(
            ["python", "-m", "pytest", "tests/", "--cov=scb_atlas", "--cov-report=html", "-v"],
            "Running tests with coverage report"
        )
        print("\n📊 Coverage report generated in htmlcov/index.html")
    
    elif command == "coverage-term":
        # Run tests with terminal coverage report
        success = run_command(
            ["python", "-m", "pytest", "tests/", "--cov=scb_atlas", "--cov-report=term-missing", "-v"],
            "Running tests with terminal coverage report"
        )
    
    elif command == "fast":
        # Run fast tests only (skip slow)
        success = run_command(
            ["python", "-m", "pytest", "tests/", "-v", "-m", "not slow"],
            "Running fast tests only"
        )
    
    elif command == "quick":
        # Run quick sanity check
        success = run_command(
            ["python", "-m", "pytest", "tests/", "-x", "-q"],
            "Running quick sanity check"
        )
    
    elif command == "verbose":
        # Run all tests with maximum verbosity
        success = run_command(
            ["python", "-m", "pytest", "tests/", "-vv", "-s"],
            "Running tests with maximum verbosity"
        )
    
    else:
        print(f"Unknown command: {command}\n")
        print_help()
        sys.exit(1)
    
    # Print summary
    print(f"\n{'='*80}")
    if success:
        print("✅ All requested tests completed successfully!")
    else:
        print("❌ Some tests failed. Review output above for details.")
    print(f"{'='*80}\n")
    
    sys.exit(0 if success else 1)


def print_help():
    """Print help message."""
    print("""
SCB Atlas Entity Types Test Runner
===================================

Usage: python run_tests.py <command>

Commands:
  all          - Run all tests (unit + integration)
  unit         - Run unit tests only
  integration  - Run integration tests only
  builders     - Run entity builders tests
  types        - Run type definitions tests
  services     - Run entity service tests
  coverage     - Run tests with HTML coverage report
  coverage-term - Run tests with terminal coverage report
  fast         - Run all tests except slow ones
  quick        - Run quick sanity check (fail on first error)
  verbose      - Run tests with maximum verbosity

Examples:
  python run_tests.py all
  python run_tests.py unit
  python run_tests.py coverage
  python run_tests.py quick

Test Directory Structure:
  tests/
  ├── unit/
  │   ├── test_entity_builders.py
  │   └── test_atlas_types.py
  ├── integration/
  │   ├── test_entity_services.py
  │   └── conftest.py
  ├── conftest.py
  └── data/

For more information, see TESTS_README.md
""")


if __name__ == "__main__":
    # Backward-compatible wrapper: keep old entry point working via unified CLI.
    print(
        "[DEPRECATED] `run_tests.py` is deprecated. "
        "Use `scb_dp_cli.py tests <suite>` (or `scb tests <suite>`)."
    )
    from scb_dp_cli import main as scb_main

    if len(sys.argv) < 2:
        print_help()
        raise SystemExit(1)

    raise SystemExit(scb_main(["tests", sys.argv[1]]))

