# Tweet Fetching Tests Shortcut
Write-Host "Running Tweet Fetching Tests..." -ForegroundColor Cyan
$rootDir = Split-Path -Parent $PSScriptRoot
$testRunner = Join-Path $rootDir "test_runner.py"
& python $testRunner tweet @args 