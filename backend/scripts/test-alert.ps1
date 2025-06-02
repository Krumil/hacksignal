# Alert Module Tests Shortcut
Write-Host "Running Alert Module Tests..." -ForegroundColor Yellow
$rootDir = Split-Path -Parent $PSScriptRoot
$testRunner = Join-Path $rootDir "test_runner.py"
& python $testRunner alert @args 