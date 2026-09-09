$ErrorActionPreference = "Stop"
$env:PYTHONUTF8 = "1"
$work = Join-Path $PSScriptRoot "cold"
$op = Join-Path $PSScriptRoot "operator"
$claude = "C:\Users\cik61\.local\bin\claude.exe"
# Start closed. The user opens the document manually later in the demonstration.
$started = Get-Date
@{started_at=$started.ToUniversalTime().ToString("o");workspace=$work;mode="FULL_PRODUCT_COLD_FILMING";benchmark=$false} | ConvertTo-Json | Set-Content -Encoding utf8 (Join-Path $op "capture-start.json")
Set-Location $work
& $claude
$agentExit = $LASTEXITCODE
# Claude raw session logs remain operator-only; inspect before sharing.
$projectKey = $work -replace '[^a-zA-Z0-9]', '-'
$projectLogs = Join-Path (Join-Path $env:USERPROFILE '.claude\projects') $projectKey
$copyFolder = Join-Path $op ('private-logs-' + (Get-Date -Format 'yyyyMMdd-HHmmss'))
$copied = @()
if (Test-Path -LiteralPath $projectLogs) {
    New-Item -ItemType Directory -Path $copyFolder | Out-Null
    Get-ChildItem -LiteralPath $projectLogs -Filter '*.jsonl' -File | Where-Object LastWriteTime -ge $started | ForEach-Object {
        Copy-Item -LiteralPath $_.FullName -Destination $copyFolder
        $copied += $_.Name
    }
}
@{finished_at=(Get-Date).ToUniversalTime().ToString('o');exit_code=$agentExit;copied_logs=$copied;raw_log_source=$projectLogs;review_status='UNREVIEWED_DO_NOT_PUBLISH'} | ConvertTo-Json | Set-Content -Encoding utf8 (Join-Path $op 'capture-end.json')
Write-Host "촬영 세션 종료. 로그는 operator 폴더에 보관되며 공개 전 확인이 필요합니다."
if ($copied.Count -eq 0) { Write-Host "로그 자동 수집 없음. capture-end.json의 원본 경로를 확인하세요." }
