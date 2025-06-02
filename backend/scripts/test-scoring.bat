@echo off
echo Running Scoring Module Tests...
cd /d "%~dp0.."
python test_runner.py scoring %* 