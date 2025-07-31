#!/usr/bin/env python
"""
Custom test runner for the MCDA API project.
Provides easy commands to run different test suites.
"""
import subprocess
import sys


def run_command(command):
    """Run a command and return the result"""
    try:
        result = subprocess.run(command, shell=True,
                                capture_output=True, text=True)
        print(result.stdout)
        if result.stderr:
            print("STDERR:", result.stderr)
        return result.returncode == 0
    except Exception as e:
        print(f"Error running command: {e}")
        return False


def run_all_tests():
    """Run all tests in the project"""
    print("🧪 Running all tests...")
    return run_command("python manage.py test --verbosity=2")


def run_app_tests(app_name):
    """Run tests for a specific app"""
    print(f"🧪 Running tests for {app_name}...")
    return run_command(f"python manage.py test {app_name} --verbosity=2")


def run_coverage():
    """Run tests with coverage report"""
    print("📊 Running tests with coverage...")
    commands = [
        "coverage run --source='.' manage.py test",
        "coverage report -m",
        "coverage html"
    ]

    for cmd in commands:
        if not run_command(cmd):
            print(f"Failed to run: {cmd}")
            return False

    print("📄 Coverage report generated in htmlcov/index.html")
    return True


def run_specific_test(test_path):
    """Run a specific test class or method"""
    print(f"🎯 Running specific test: {test_path}")
    return run_command(f"python manage.py test {test_path} --verbosity=2")


def main():
    if len(sys.argv) < 2:
        print("""
🧪 MCDA API Test Runner

Usage:
    python test_runner.py all                    # Run all tests
    python test_runner.py Account                # Run Account app tests
    python test_runner.py Privacy                # Run Privacy app tests
    python test_runner.py Relationships          # Run Relationships app tests
    python test_runner.py coverage               # Run tests with coverage
    python test_runner.py specific <test_path>   # Run specific test
    
Examples:
    python test_runner.py specific Account.tests.UsersModelTest
    python test_runner.py specific Account.tests.UsersModelTest.test_create_user
        """)
        return

    command = sys.argv[1].lower()

    if command == 'all':
        success = run_all_tests()
    elif command == 'coverage':
        success = run_coverage()
    elif command == 'specific':
        if len(sys.argv) < 3:
            print("❌ Please provide test path for specific test")
            return
        success = run_specific_test(sys.argv[2])
    elif command in ['account', 'privacy', 'relationships']:
        success = run_app_tests(command.capitalize())
    else:
        print(f"❌ Unknown command: {command}")
        return

    if success:
        print("✅ Tests completed successfully!")
    else:
        print("❌ Tests failed!")
        sys.exit(1)


if __name__ == "__main__":
    main()
