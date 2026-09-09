param(
    [Parameter(Mandatory=$true)][ValidateRange(1,3)][int]$Round,
    [Parameter(Mandatory=$true)][string]$SetupRoot,
    [switch]$CheckOnly
)
$ErrorActionPreference = 'Stop'
$env:PYTHONUTF8 = '1'
$SetupRoot = (Resolve-Path -LiteralPath $SetupRoot).Path
$manifest = Get-Content -LiteralPath (Join-Path $SetupRoot 'rounds.json') -Raw -Encoding utf8 | ConvertFrom-Json
$permissionMode = $manifest.permission_mode
if ($permissionMode -and $permissionMode -notin @('manual','auto')) {
    throw 'Unsupported preparation permission mode; no bypass fallback.'
}
$run = @($manifest.rounds | Where-Object { $_.round -eq $Round })[0]
$work = $run.workspace
$preflightCode = @'
import json,sys,hashlib
from pathlib import Path
w=Path(sys.argv[1]); c=json.loads((w/'skillloop-work.json').read_text(encoding='utf-8-sig'))
s=json.loads(Path(c['store']).read_text(encoding='utf-8-sig')); u=json.loads(Path(c['usage']).read_text(encoding='utf-8-sig'))
p1=[d for d in s['skills'].values() if d.get('procedure',{}).get('action')=='file-access']
f=w/sys.argv[2]
ok=not p1 and not u.get('counts') and not u.get('events') and not u.get('seen_run_ids')
ok=ok and hashlib.sha256(f.read_bytes()).hexdigest()==sys.argv[3]
print(json.dumps({'cold':ok,'p1_skills':len(p1),'branch':c.get('branch'),'xlsx_sha256':hashlib.sha256(f.read_bytes()).hexdigest()}))
raise SystemExit(0 if ok else 2)
'@
$preflight = & $manifest.product_python -c $preflightCode $work $manifest.filename $manifest.input_sha256
if ($LASTEXITCODE -ne 0) { throw 'Not a fresh Cold workspace. Preserve this run and use the next prepared round.' }
$remoteTip = & git ls-remote --heads $manifest.remote ('refs/heads/' + $run.branch)
if ($LASTEXITCODE -ne 0 -or -not $remoteTip -or (($remoteTip -split '\s+')[0] -ne $manifest.baseline_sha)) {
    throw 'Remote branch changed or unavailable. Do not start as Cold; preserve existing results.'
}
if ($CheckOnly) {
    Write-Output $preflight
    Write-Output 'COLD_READY_CHECK_ONLY: no Claude process started.'
    exit 0
}
$started = Get-Date
$attempt = Join-Path (Join-Path $SetupRoot 'operator') ('round-' + $Round + '-' + $started.ToString('yyyyMMdd-HHmmss-fff'))
New-Item -ItemType Directory -Path $attempt | Out-Null
$sessionId = [guid]::NewGuid().ToString()
$metadata = @{round=$Round;session_id=$sessionId;workspace=$work;branch=$run.branch;
    mode='FULL_PRODUCT_COLD_MANUAL';model=$manifest.model;effort=$manifest.effort;
    input_sha256=$manifest.input_sha256;source_sha=$manifest.source_sha;
    started_at=$started.ToUniversalTime().ToString('o');preflight=($preflight | ConvertFrom-Json);
    permission_mode=$(if ($permissionMode) { $permissionMode } else { 'inherited' })}
$metadata | ConvertTo-Json -Depth 10 | Set-Content -LiteralPath (Join-Path $attempt 'start.json') -Encoding utf8
Copy-Item -LiteralPath (Join-Path $work '.skillloop/store.json') -Destination (Join-Path $attempt 'store-before.json')
Copy-Item -LiteralPath (Join-Path $work '.skillloop/usage.json') -Destination (Join-Path $attempt 'usage-before.json')
Write-Host "P1 Cold round $Round. Start screen recording, then enter the task."
Write-Host 'After the task, capture /cost and exit with /exit. Open only this round workbook when needed.'
$exitCode = $null
$oldLocation = Get-Location
$oldAfkTimeout = [Environment]::GetEnvironmentVariable('CLAUDE_AFK_TIMEOUT_MS', 'Process')
try {
    Set-Location -LiteralPath $work
    $launchArgs = @('--model', $manifest.model, '--effort', $manifest.effort, '--session-id', $sessionId)
    if ($permissionMode) { $launchArgs += @('--permission-mode', $permissionMode) }
    if ($permissionMode) {
        # Auto tool permissions do not authorize candidate publication.
        $questionSettings = Join-Path $attempt 'question-settings.json'
        '{"askUserQuestionTimeout":"never"}' | Set-Content -LiteralPath $questionSettings -Encoding utf8
        $launchArgs += @('--settings', (Resolve-Path -LiteralPath $questionSettings).Path)
        [Environment]::SetEnvironmentVariable('CLAUDE_AFK_TIMEOUT_MS', $null, 'Process')
    }
    & $manifest.claude @launchArgs
    $exitCode = $LASTEXITCODE
}
finally {
    [Environment]::SetEnvironmentVariable('CLAUDE_AFK_TIMEOUT_MS', $oldAfkTimeout, 'Process')
    Set-Location $oldLocation
    $finished = Get-Date
    $copied = @()
    $logRoot = Join-Path $env:USERPROFILE '.claude/projects'
    if (Test-Path -LiteralPath $logRoot) {
        foreach ($dir in (Get-ChildItem -LiteralPath $logRoot -Directory)) {
            $source = Join-Path $dir.FullName ($sessionId + '.jsonl')
            if (Test-Path -LiteralPath $source) {
                Copy-Item -LiteralPath $source -Destination (Join-Path $attempt ($sessionId + '.jsonl'))
                $copied += $source
                $sessionFolder = Join-Path $dir.FullName $sessionId
                if (Test-Path -LiteralPath $sessionFolder) {
                    Copy-Item -LiteralPath $sessionFolder -Destination (Join-Path $attempt 'session-details') -Recurse
                }
            }
        }
    }
    Copy-Item -LiteralPath (Join-Path $work '.skillloop/store.json') -Destination (Join-Path $attempt 'store-after.json')
    Copy-Item -LiteralPath (Join-Path $work '.skillloop/usage.json') -Destination (Join-Path $attempt 'usage-after.json')
    @{finished_at=$finished.ToUniversalTime().ToString('o');exit_code=$exitCode;
      session_elapsed_seconds=($finished-$started).TotalSeconds;includes_human_wait=$true;
      native_log_sources=$copied;tokens=$null;task_success='UNREVIEWED';
      publication_success='UNREVIEWED';privacy='OPERATOR_ONLY_REVIEW_BEFORE_SHARING'} |
        ConvertTo-Json -Depth 6 | Set-Content -LiteralPath (Join-Path $attempt 'end.json') -Encoding utf8
    Write-Host "Session evidence: $attempt"
    if ($copied.Count -eq 0) { Write-Warning 'Native session log missing. Keep the video and /cost screenshot; do not report tokens as zero.' }
}
