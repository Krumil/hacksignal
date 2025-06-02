@echo off
echo Running Tweet Fetching Tests...
cd /d "%~dp0.."
python test_runner.py tweet %* 