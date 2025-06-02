# PowerShell Test Runner for HackSignal
# Usage: .\scripts\test.ps1 [test_name] [options]

param(
  [Parameter(Position = 0)]
  [string]$TestName = "",
    
  [Alias("v")]
  [switch]$VerboseOutput,
    
  [Alias("f")]
  [switch]$FailFast,
    
  [Alias("h")]
  [switch]$Help
)

function Show-Help {
  Write-Host @"
HackSignal Test Runner
======================

Usage: .\scripts\test.ps1 [test_name] [options]

Available tests:
  tweet       - Run tweet fetching tests
  ingestion   - Run ingestion module tests  
  alert       - Run alert module tests
  enrichment  - Run enrichment module tests
  scoring     - Run scoring module tests
  all         - Run all tests

Options:
  -v, -VerboseOutput  Verbose output
  -f, -FailFast       Stop on first failure
  -h, -Help           Show this help

Examples:
  .\scripts\test.ps1 tweet              # Run tweet tests
  .\scripts\test.ps1 alert -v           # Run alert tests with verbose output
  .\scripts\test.ps1 all -f             # Run all tests, stop on first failure
  .\scripts\test.ps1 -h                 # Show this help

Direct shortcuts also available:
  .\scripts\test-tweet.ps1              # Run tweet tests
  .\scripts\test-alert.ps1              # Run alert tests
  .\scripts\test-ingestion.ps1          # Run ingestion tests
  .\scripts\test-enrichment.ps1         # Run enrichment tests
  .\scripts\test-scoring.ps1            # Run scoring tests
"@
}

function Run-Test {
  param(
    [string]$Name,
    [bool]$VerboseOutputFlag = $false,
    [bool]$FailFastFlag = $false
  )
    
  $args = @($Name)
  if ($VerboseOutputFlag) { $args += "-v" }
  if ($FailFastFlag) { $args += "-f" }
    
  # Find the test_runner.py in the parent directory
  $rootDir = Split-Path -Parent $PSScriptRoot
  $testRunner = Join-Path $rootDir "test_runner.py"
    
  & python $testRunner @args
}

# Main execution
if ($Help -or $TestName -eq "") {
  Show-Help
  exit 0
}

try {
  Run-Test -Name $TestName -VerboseOutputFlag $VerboseOutput -FailFastFlag $FailFast
}
catch {
  Write-Host "❌ Error running test: $_" -ForegroundColor Red
  exit 1
} 