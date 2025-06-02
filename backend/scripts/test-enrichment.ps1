# Enrichment Module Tests Shortcut
Write-Host "Running Enrichment Module Tests..." -ForegroundColor Magenta
$rootDir = Split-Path -Parent $PSScriptRoot
$testRunner = Join-Path $rootDir "test_runner.py"
& python $testRunner enrichment @args 