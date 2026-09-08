param(
    [Parameter(Mandatory=$true)][string]$Destination,
    [string]$Python = 'python'
)
$ErrorActionPreference = 'Stop'
$repoRoot = Split-Path -Parent $PSScriptRoot
$productPython = Join-Path $repoRoot '.venv\Scripts\python.exe'
if (Test-Path -LiteralPath $Destination) {
    throw 'Use a new work directory; existing work is never overwritten.'
}
if (-not (Test-Path -LiteralPath $productPython)) {
    & $Python -m venv (Join-Path $repoRoot '.venv')
    if ($LASTEXITCODE -ne 0) { throw 'Product venv creation failed.' }
}
& $productPython -m pip install -e $repoRoot
if ($LASTEXITCODE -ne 0) { throw 'Declared product dependency installation failed.' }
& $productPython (Join-Path $repoRoot 'tests\prepare_p0_work.py') $Destination
if ($LASTEXITCODE -ne 0) { throw 'Synthetic work preparation failed.' }
Write-Host "Prepared: $Destination"
Write-Host 'Start Claude Code in that folder and request installation from requirements.txt.'
