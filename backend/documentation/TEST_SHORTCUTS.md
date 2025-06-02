# HackSignal Test Shortcuts

This document describes the various shortcut commands available for running tests in the HackSignal project.

## Available Test Shortcuts

### 🐍 Python Test Runner (Universal)

The main test runner works on all platforms:

```bash
# Run individual tests
python test_runner.py tweet          # Tweet fetching tests
python test_runner.py ingestion      # Ingestion module tests
python test_runner.py alert          # Alert module tests
python test_runner.py enrichment     # Enrichment module tests
python test_runner.py scoring        # Scoring module tests
python test_runner.py all            # Run all tests

# With options
python test_runner.py tweet -v       # Verbose output
python test_runner.py alert -f       # Fail fast (stop on first failure)
python test_runner.py all -v -f      # Verbose + fail fast
```

### 💻 PowerShell Scripts (Windows)

For PowerShell users:

```powershell
# Main test script
.\test.ps1 tweet                      # Run tweet tests
.\test.ps1 alert -v                   # Run alert tests with verbose output
.\test.ps1 all -f                     # Run all tests, stop on first failure
.\test.ps1 -h                         # Show help

# Individual shortcuts
.\test-tweet.ps1                      # Tweet fetching tests
.\test-alert.ps1                      # Alert module tests
.\test-ingestion.ps1                  # Ingestion module tests
.\test-enrichment.ps1                 # Enrichment module tests
.\test-scoring.ps1                    # Scoring module tests
```

### 🖥️ Batch Files (Windows Command Prompt)

For Command Prompt users:

```cmd
REM Main test script
test.bat tweet                        REM Run tweet tests
test.bat alert -v                     REM Run alert tests with verbose output
test.bat all -f                       REM Run all tests, stop on first failure
test.bat help                         REM Show help

REM Individual shortcuts
test-tweet.bat                        REM Tweet fetching tests
test-alert.bat                        REM Alert module tests
test-ingestion.bat                    REM Ingestion module tests
test-enrichment.bat                   REM Enrichment module tests
test-scoring.bat                      REM Scoring module tests
```

## Test Descriptions

| Test Name    | File                          | Description                                            |
| ------------ | ----------------------------- | ------------------------------------------------------ |
| `tweet`      | `test/test_tweet_fetching.py` | Tests tweet fetching functionality and API integration |
| `ingestion`  | `test/test_ingestion.py`      | Unit tests for data ingestion module                   |
| `alert`      | `test/test_alert.py`          | Unit tests for alert system module                     |
| `enrichment` | `test/test_enrichment.py`     | Unit tests for data enrichment module                  |
| `scoring`    | `test/test_scoring.py`        | Unit tests for scoring algorithm module                |

## Options

| Option           | Description                         |
| ---------------- | ----------------------------------- |
| `-v, --verbose`  | Show detailed test output           |
| `-f, --failfast` | Stop running tests on first failure |
| `-h, --help`     | Show help message                   |

## Examples

### Quick Test Runs

```bash
# Quick tweet test
python test_runner.py tweet

# Quick check of all modules
python test_runner.py all -f
```

### Detailed Testing

```bash
# Verbose output for debugging
python test_runner.py enrichment -v

# Run all tests with full output
python test_runner.py all -v
```

### PowerShell Examples

```powershell
# Quick test with PowerShell
.\test-alert.ps1

# Detailed run with options
.\test.ps1 scoring -v -f
```

### Batch File Examples

```cmd
REM Quick command prompt test
test-ingestion.bat

REM Full test run
test.bat all -v
```

## Direct Test Execution

You can also run tests directly (for advanced users):

```bash
# Run unittest tests directly
python -m unittest test.test_ingestion -v
python -m unittest test.test_alert -v
python -m unittest test.test_enrichment -v
python -m unittest test.test_scoring -v

# Run standalone test directly
python test/test_tweet_fetching.py
```

## Troubleshooting

### Permission Issues (PowerShell)

If you get execution policy errors with PowerShell scripts:

```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### Python Not Found

Make sure Python is in your PATH, or use:

```bash
py test_runner.py tweet        # On Windows with Python Launcher
python3 test_runner.py tweet   # On systems with python3 command
```

### Test Dependencies

Make sure all dependencies are installed:

```bash
pip install -r requirements.txt
```

## Integration with Development Workflow

### Before Commits

```bash
# Quick check before committing
python test_runner.py all -f
```

### During Development

```bash
# Test specific module you're working on
python test_runner.py ingestion -v
```

### CI/CD Integration

The test runner returns appropriate exit codes for CI/CD systems:

-   `0` for success
-   `1` for failure

## Adding New Tests

To add a new test module:

1. Create your test file in the `test/` directory
2. Add it to the `TESTS` dictionary in `test_runner.py`
3. Create corresponding shortcut files (optional)
4. Update this documentation

Example addition to `test_runner.py`:

```python
'newmodule': {
    'file': 'test/test_newmodule.py',
    'description': 'New module unit tests',
    'type': 'unittest'  # or 'standalone'
}
```
