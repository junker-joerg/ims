[CmdletBinding()]
param([string]$IsccPath, [string]$Version = '2.0.0-alpha.1', [string]$FileVersion = '2.0.0.1')
$ErrorActionPreference = 'Stop'
$repo = (Resolve-Path (Join-Path $PSScriptRoot '..\..')).Path
$python = Join-Path $repo '.venv\Scripts\python.exe'
if (-not (Test-Path -LiteralPath $python)) { throw 'Create this checkout''s .venv first.' }
if (-not $IsccPath) { $IsccPath = Join-Path $repo 'build\inno\compiler\ISCC.exe' }
if (-not (Test-Path -LiteralPath $IsccPath)) { throw 'Run install-build-tools.ps1 first or supply -IsccPath.' }
$timer = [Diagnostics.Stopwatch]::StartNew()
Push-Location $repo
try {
    npm.cmd ci --prefix frontend
    if ($LASTEXITCODE -ne 0) { throw 'npm ci failed' }
    npm.cmd run build --prefix frontend
    if ($LASTEXITCODE -ne 0) { throw 'Frontend build failed' }
    & $python scripts/installer/stage_resources.py
    if ($LASTEXITCODE -ne 0) { throw 'Resource staging failed' }
    # Fixed inputs and hash seed; no claim of bit-identical unsigned PE output.
    $env:PYTHONHASHSEED = '0'
    & $python -m PyInstaller --noconfirm --clean scripts/installer/ims.spec
    if ($LASTEXITCODE -ne 0) { throw 'PyInstaller failed' }
    & $IsccPath "/DRepoRoot=$repo" "/DAppVersion=$Version" "/DFileVersion=$FileVersion" scripts/installer/ims.iss
    if ($LASTEXITCODE -ne 0) { throw 'Inno Setup failed' }
    $artifact = Join-Path $repo "dist\installer\IMS-Setup-$Version-win-x64.exe"
    $hash = (Get-FileHash -LiteralPath $artifact -Algorithm SHA256).Hash.ToLowerInvariant()
    "$hash  $(Split-Path -Leaf $artifact)" | Set-Content -LiteralPath "$artifact.sha256" -Encoding utf8NoBOM
    $timer.Stop()
    [ordered]@{ artifact = (Split-Path -Leaf $artifact); sha256 = $hash;
        bytes = (Get-Item -LiteralPath $artifact).Length; build_seconds = $timer.Elapsed.TotalSeconds;
        commit = (git rev-parse HEAD); version = $Version; inno = '6.7.3';
        python = (& $python -c 'import platform;print(platform.python_version())');
        signed = $false; clean_windows_acceptance = 'pending' } |
        ConvertTo-Json | Set-Content dist/installer/build-evidence.json -Encoding utf8NoBOM
    Copy-Item build/installer-resources/resource-inventory.json dist/installer/
    Write-Output $artifact
} finally { Pop-Location }
