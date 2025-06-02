#!/usr/bin/env python3
"""
Test Runner - Convenient shortcuts for running individual tests
Usage: python test_runner.py [test_name] [options]

Available tests:
  tweet     - Run tweet fetching tests
  ingestion - Run ingestion module tests
  alert     - Run alert module tests  
  enrichment- Run enrichment module tests
  scoring   - Run scoring module tests
  all       - Run all tests

Options:
  -v, --verbose    Verbose output
  -f, --failfast   Stop on first failure
  -h, --help       Show this help
"""

import sys
import os
import subprocess
import argparse
import dotenv

# Load environment variables
dotenv.load_dotenv()

# Test configurations
TESTS = {
    'tweet': {
        'file': 'test/test_tweet_fetching.py',
        'description': 'Tweet fetching functionality tests',
        'type': 'standalone'
    },
    'ingestion': {
        'file': 'test/test_ingestion.py', 
        'description': 'Ingestion module unit tests',
        'type': 'unittest'
    },
    'alert': {
        'file': 'test/test_alert.py',
        'description': 'Alert module unit tests', 
        'type': 'unittest'
    },
    'enrichment': {
        'file': 'test/test_enrichment.py',
        'description': 'Enrichment module unit tests',
        'type': 'unittest'
    },
    'scoring': {
        'file': 'test/test_scoring.py',
        'description': 'Score tweets from raw data folder',
        'type': 'standalone'
    }
}

def print_help():
    """Print help message with available tests."""
    print(__doc__)
    print("\nAvailable tests:")
    for name, config in TESTS.items():
        print(f"  {name:<12} - {config['description']}")
    print()

def run_test(test_name, verbose=False, failfast=False):
    """Run a specific test."""
    if test_name not in TESTS:
        print(f"❌ Unknown test: {test_name}")
        print(f"Available tests: {', '.join(TESTS.keys())}")
        return False
    
    test_config = TESTS[test_name]
    test_file = test_config['file']
    
    if not os.path.exists(test_file):
        print(f"❌ Test file not found: {test_file}")
        return False
    
    print(f"🧪 Running {test_config['description']}")
    print(f"📁 File: {test_file}")
    print("=" * 50)
    
    try:
        if test_config['type'] == 'standalone':
            # Run standalone test files directly
            cmd = [sys.executable, test_file]
            result = subprocess.run(cmd, capture_output=False)
        else:
            # For unittest files, try module approach first, then fallback to direct execution
            success = False
            
            # Method 1: Try running as module (works if __init__.py exists)
            try:
                cmd = [sys.executable, '-m', 'unittest']
                if verbose:
                    cmd.append('-v')
                if failfast:
                    cmd.append('-f')
                # Convert file path to module path
                module_path = test_file.replace('/', '.').replace('\\', '.').replace('.py', '')
                cmd.append(module_path)
                
                result = subprocess.run(cmd, capture_output=False)
                if result.returncode == 0:
                    success = True
                else:
                    # If module approach failed, try direct execution
                    print("📝 Module import failed, trying direct execution...")
                    cmd = [sys.executable, test_file]
                    result = subprocess.run(cmd, capture_output=False)
                    if result.returncode == 0:
                        success = True
                        
            except Exception as e:
                print(f"⚠️  Module approach failed: {e}")
                # Fallback to direct execution
                cmd = [sys.executable, test_file]
                result = subprocess.run(cmd, capture_output=False)
                if result.returncode == 0:
                    success = True
            
            if not success and 'result' in locals():
                # If both methods failed, return the last result
                pass
        
        if result.returncode == 0:
            print(f"\n✅ {test_name} tests passed!")
            return True
        else:
            print(f"\n❌ {test_name} tests failed!")
            return False
            
    except Exception as e:
        print(f"❌ Error running test: {e}")
        return False

def run_all_tests(verbose=False, failfast=False):
    """Run all tests."""
    print("🧪 Running all tests")
    print("=" * 50)
    
    results = {}
    for test_name in TESTS.keys():
        print(f"\n{'='*20} {test_name.upper()} {'='*20}")
        results[test_name] = run_test(test_name, verbose, failfast)
        
        if failfast and not results[test_name]:
            break
    
    # Summary
    print("\n" + "="*50)
    print("📊 TEST SUMMARY")
    print("="*50)
    
    passed = sum(results.values())
    total = len(results)
    
    for test_name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"  {test_name:<12} - {status}")
    
    print(f"\nResults: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed!")
        return True
    else:
        print("💥 Some tests failed!")
        return False

def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description='Test Runner for HackSignal', add_help=False)
    parser.add_argument('test', nargs='?', help='Test to run (or "all")')
    parser.add_argument('-v', '--verbose', action='store_true', help='Verbose output')
    parser.add_argument('-f', '--failfast', action='store_true', help='Stop on first failure')
    parser.add_argument('-h', '--help', action='store_true', help='Show help')
    
    args = parser.parse_args()
    
    if args.help or not args.test:
        print_help()
        return
    
    if args.test == 'all':
        success = run_all_tests(args.verbose, args.failfast)
    else:
        success = run_test(args.test, args.verbose, args.failfast)
    
    sys.exit(0 if success else 1)

if __name__ == '__main__':
    main() 