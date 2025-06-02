# Scoring Module Tests Shortcut
Write-Host "Running Scoring Module Tests..." -ForegroundColor Blue
$rootDir = Split-Path -Parent $PSScriptRoot
$testRunner = Join-Path $rootDir "test_runner.py"
& python $testRunner scoring @args 