@echo off
echo Running Alert Module Tests...
cd /d "%~dp0.."
python test_runner.py alert %* 