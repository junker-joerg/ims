[CmdletBinding()]
param([string]$IsccPath)
$ErrorActionPreference = 'Stop'
$repo = (Resolve-Path (Join-Path $PSScriptRoot '..\..')).Path
$python = Join-Path $repo '.venv\Scripts\python.exe'
if (-not (Test-Path -LiteralPath $python)) { throw 'Create this checkout''s .venv first.' }
& $python -c 'import struct,sys; assert sys.version_info[:3] == (3,12,10) and struct.calcsize("P") == 8, "Build requires CPython 3.12.10 x64"'
if ($LASTEXITCODE -ne 0) { throw 'Unexpected Python build runtime' }
$release = & $python (Join-Path $PSScriptRoot 'release_metadata.py')
if ($LASTEXITCODE -ne 0) { throw 'Release versions are inconsistent.' }
$release = $release | ConvertFrom-Json
$Version = $release.version
$FileVersion = $release.file_version
if (-not $IsccPath) { $IsccPath = Join-Path $repo 'build\inno\compiler\ISCC.exe' }
if (-not (Test-Path -LiteralPath $IsccPath)) { throw 'Run install-build-tools.ps1 first or supply -IsccPath.' }
$timer = [Diagnostics.Stopwatch]::StartNew()
$previousHashSeed = $env:PYTHONHASHSEED
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
    $artifact = Join-Path $repo "dist\installer\$($release.artifact)"
    $hash = (Get-FileHash -LiteralPath $artifact -Algorithm SHA256).Hash.ToLowerInvariant()
    "$hash  $(Split-Path -Leaf $artifact)" | Set-Content -LiteralPath "$artifact.sha256" -Encoding utf8NoBOM
    $timer.Stop()
    [ordered]@{ artifact = (Split-Path -Leaf $artifact); sha256 = $hash;
        bytes = (Get-Item -LiteralPath $artifact).Length; build_seconds = $timer.Elapsed.TotalSeconds;
        commit = (git rev-parse HEAD); version = $Version; file_version = $FileVersion; inno = '6.7.3';
        dirty = [bool](git status --porcelain); node = (node --version);
        python = (& $python -c 'import platform;print(platform.python_version())');
        signed = $false; clean_windows_acceptance = 'pending' } |
        ConvertTo-Json | Set-Content dist/installer/build-evidence.json -Encoding utf8NoBOM
    Copy-Item build/installer-resources/resource-inventory.json dist/installer/
    Write-Output $artifact
} finally { $env:PYTHONHASHSEED = $previousHashSeed; Pop-Location }
