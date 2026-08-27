"""
Runner script for persistence tests
"""

import subprocess
import sys
import os

def run_test(test_file):
    """Run a test file and return success status"""
    print(f"Running {test_file}...")
    try:
        result = subprocess.run([sys.executable, test_file], 
                              capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✓ {test_file} PASSED")
            return True
        else:
            print(f"✗ {test_file} FAILED")
            print(f"Error output:\n{result.stderr}")
            return False
    except Exception as e:
        print(f"Error running {test_file}: {e}")
        return False

if __name__ == "__main__":
    # Create test output directory if it doesn't exist
    if not os.path.exists('test_output'):
        os.makedirs('test_output')
    
    # Run all tests
    test_files = [
        'tests/integration/test_persistence.py',
        'tests/integration/test_database_persistence.py'
    ]
    
    results = []
    for test_file in test_files:
        results.append(run_test(test_file))
    
    # Print summary
    print("\n" + "="*50)
    print("TEST SUMMARY")
    print("="*50)
    print(f"Total tests: {len(results)}")
    print(f"Passed: {sum(results)}")
    print(f"Failed: {len(results) - sum(results)}")
    
    if all(results):
        print("✓ All tests PASSED")
        sys.exit(0)
    else:
        print("✗ Some tests FAILED")
        sys.exit(1)
