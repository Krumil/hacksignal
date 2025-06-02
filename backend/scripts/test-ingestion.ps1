# Ingestion Module Tests Shortcut
Write-Host "Running Ingestion Module Tests..." -ForegroundColor Green  
$rootDir = Split-Path -Parent $PSScriptRoot
$testRunner = Join-Path $rootDir "test_runner.py"
& python $testRunner ingestion @args 