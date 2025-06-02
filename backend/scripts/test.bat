@echo off
REM HackSignal Test Runner Batch File
REM Usage: scripts\test.bat [test_name] [options]

if "%1"=="" goto :help
if "%1"=="help" goto :help
if "%1"=="-h" goto :help
if "%1"=="--help" goto :help

echo Running HackSignal Tests...
cd /d "%~dp0.."
python test_runner.py %*
goto :end

:help
echo HackSignal Test Runner
echo ======================
echo.
echo Usage: scripts\test.bat [test_name] [options]
echo.
echo Available tests:
echo   tweet       - Run tweet fetching tests
echo   ingestion   - Run ingestion module tests
echo   alert       - Run alert module tests
echo   enrichment  - Run enrichment module tests
echo   scoring     - Run scoring module tests
echo   all         - Run all tests
echo.
echo Options:
echo   -v, --verbose   Verbose output
echo   -f, --failfast  Stop on first failure
echo   -h, --help      Show this help
echo.
echo Examples:
echo   scripts\test.bat tweet          # Run tweet tests
echo   scripts\test.bat alert -v       # Run alert tests with verbose output
echo   scripts\test.bat all -f         # Run all tests, stop on first failure
echo.
echo Individual shortcuts:
echo   scripts\test-tweet.bat          # Run tweet tests
echo   scripts\test-alert.bat          # Run alert tests
echo   scripts\test-ingestion.bat      # Run ingestion tests
echo   scripts\test-enrichment.bat     # Run enrichment tests
echo   scripts\test-scoring.bat        # Run scoring tests

:end 