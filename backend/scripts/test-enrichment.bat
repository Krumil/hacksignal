@echo off
echo Running Enrichment Module Tests...
cd /d "%~dp0.."
python test_runner.py enrichment %* 