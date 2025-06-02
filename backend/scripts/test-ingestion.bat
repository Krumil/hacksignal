@echo off
echo Running Ingestion Module Tests...
cd /d "%~dp0.."
python test_runner.py ingestion %* 