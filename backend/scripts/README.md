# HackSignal Test Scripts

This directory contains convenient shortcut scripts for running tests.

## Usage

### 🐍 Python Test Runner (Recommended)

From the project root directory:

```bash
python test_runner.py [test_name] [options]
```

### 💻 PowerShell Scripts

From the project root directory:

```powershell
.\scripts\test.ps1 [test_name] [options]     # Main script
.\scripts\test-tweet.ps1                     # Tweet tests shortcut
.\scripts\test-alert.ps1                     # Alert tests shortcut
.\scripts\test-ingestion.ps1                 # Ingestion tests shortcut
.\scripts\test-enrichment.ps1                # Enrichment tests shortcut
.\scripts\test-scoring.ps1                   # Scoring tests shortcut
```

### 🖥️ Batch Files

From the project root directory:

```cmd
scripts\test.bat [test_name] [options]       REM Main script
scripts\test-tweet.bat                       REM Tweet tests shortcut
scripts\test-alert.bat                       REM Alert tests shortcut
scripts\test-ingestion.bat                   REM Ingestion tests shortcut
scripts\test-enrichment.bat                  REM Enrichment tests shortcut
scripts\test-scoring.bat                     REM Scoring tests shortcut
```

## Available Tests

| Test Name    | Description                        |
| ------------ | ---------------------------------- |
| `tweet`      | Tweet fetching functionality tests |
| `ingestion`  | Ingestion module unit tests        |
| `alert`      | Alert module unit tests            |
| `enrichment` | Enrichment module unit tests       |
| `scoring`    | Scoring module unit tests          |
| `all`        | Run all tests                      |

## Options

| Option           | Description                         |
| ---------------- | ----------------------------------- |
| `-v, --verbose`  | Show detailed test output           |
| `-f, --failfast` | Stop running tests on first failure |
| `-h, --help`     | Show help message                   |

## Examples

```bash
# Python (recommended - works on all platforms)
python test_runner.py alert -v
python test_runner.py all

# PowerShell (Windows)
.\scripts\test.ps1 scoring -f
.\scripts\test-alert.ps1

# Batch (Windows Command Prompt)
scripts\test.bat enrichment
scripts\test-ingestion.bat
```
