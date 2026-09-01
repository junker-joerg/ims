[CmdletBinding()]
param(
    [string]$RepoRoot,
    [string]$OutPath,
    [switch]$Force
)

$ErrorActionPreference = "Stop"
if ([string]::IsNullOrWhiteSpace($RepoRoot)) {
    $RepoRoot = (Resolve-Path (Join-Path $PSScriptRoot "..\..")).Path
}
$resolvedRepoRoot = (Resolve-Path -LiteralPath $RepoRoot).Path
if ([string]::IsNullOrWhiteSpace($OutPath)) {
    $OutPath = Join-Path $resolvedRepoRoot "dist\IMS-Workbench-2026-Windows-Test.zip"
}
$resolvedOutPath = [IO.Path]::GetFullPath($OutPath)
$outParent = Split-Path -Parent $resolvedOutPath
$frontendIndex = Join-Path $resolvedRepoRoot "frontend\dist\index.html"
$installPdf = Join-Path $resolvedRepoRoot "output\pdf\IMS-Installation-Windows.pdf"
$guidePdf = Join-Path $resolvedRepoRoot "output\pdf\IMS-Bedienungsanleitung.pdf"

foreach ($requiredPath in @($frontendIndex, $installPdf, $guidePdf)) {
    if (-not (Test-Path -LiteralPath $requiredPath -PathType Leaf)) {
        throw "IMS user test package requires file: $requiredPath"
    }
}

if (-not (Test-Path -LiteralPath $outParent -PathType Container)) {
    New-Item -ItemType Directory -Path $outParent | Out-Null
}
if (Test-Path -LiteralPath $resolvedOutPath) {
    if (-not $Force) {
        throw "IMS user test package already exists; use -Force to replace it: $resolvedOutPath"
    }
    if (-not (Test-Path -LiteralPath $resolvedOutPath -PathType Leaf)) {
        throw "IMS user test package output is not a file: $resolvedOutPath"
    }
    Remove-Item -LiteralPath $resolvedOutPath -Force
}

$tempRoot = [IO.Path]::GetFullPath([IO.Path]::GetTempPath())
$workRoot = Join-Path $tempRoot ("ims-user-test-package-" + [guid]::NewGuid().ToString("N"))
$bundlePath = Join-Path $workRoot "ims-workbench-repo-bundle.zip"
$portableRoot = Join-Path $workRoot "IMS-Workbench-2026"
$previousPythonPath = $env:PYTHONPATH

function Assert-NativeSuccess {
    param([string]$Step)
    if ($LASTEXITCODE -ne 0) {
        throw "IMS user test package failed during ${Step}: exit code $LASTEXITCODE"
    }
}

New-Item -ItemType Directory -Path $workRoot | Out-Null

try {
    Push-Location $resolvedRepoRoot
    try {
        $env:PYTHONPATH = Join-Path $resolvedRepoRoot "python_port"

        $bundleJson = python -m ims.api.workbench_bundle_build `
            --root $resolvedRepoRoot `
            --frontend-dist (Join-Path $resolvedRepoRoot "frontend\dist") `
            --out $bundlePath
        Assert-NativeSuccess -Step "repo bundle build"
        $bundle = $bundleJson | ConvertFrom-Json
        if ($bundle.status -eq "error" -or $bundle.archive_created -ne $true) {
            throw "IMS user test package rejected the repo bundle"
        }

        $stagingJson = python -m ims.api.workbench_portable_staging `
            --zip-path $bundlePath `
            --out $portableRoot
        Assert-NativeSuccess -Step "portable staging"
        $staging = $stagingJson | ConvertFrom-Json
        if ($staging.status -ne "ok" -or $staging.execution_performed -ne $false) {
            throw "IMS user test package rejected portable staging"
        }

        $documentationRoot = Join-Path $portableRoot "Dokumentation"
        New-Item -ItemType Directory -Path $documentationRoot | Out-Null
        Copy-Item -LiteralPath $installPdf -Destination (Join-Path $documentationRoot "INSTALLATION.pdf")
        Copy-Item -LiteralPath $guidePdf -Destination (Join-Path $documentationRoot "BEDIENUNGSANLEITUNG.pdf")

        $smokeJson = python -m ims.api.workbench_portable_staging_smoke --root $portableRoot
        Assert-NativeSuccess -Step "portable staging smoke"
        $smoke = $smokeJson | ConvertFrom-Json
        if ($smoke.status -ne "ok" -or $smoke.execution_performed -ne $false) {
            throw "IMS user test package rejected the portable smoke"
        }

        Add-Type -AssemblyName System.IO.Compression.FileSystem
        [IO.Compression.ZipFile]::CreateFromDirectory(
            $portableRoot,
            $resolvedOutPath,
            [IO.Compression.CompressionLevel]::Optimal,
            $true
        )

        $requiredEntries = @(
            "IMS-Workbench-2026/BITTE-ZUERST-LESEN.txt",
            "IMS-Workbench-2026/install-workbench.cmd",
            "IMS-Workbench-2026/check-workbench.cmd",
            "IMS-Workbench-2026/start-workbench.cmd",
            "IMS-Workbench-2026/app/frontend/dist/index.html",
            "IMS-Workbench-2026/app/python_port/pyproject.toml",
            "IMS-Workbench-2026/app/python_port/requirements-web.txt",
            "IMS-Workbench-2026/Dokumentation/INSTALLATION.pdf",
            "IMS-Workbench-2026/Dokumentation/BEDIENUNGSANLEITUNG.pdf"
        )
        $archive = [IO.Compression.ZipFile]::OpenRead($resolvedOutPath)
        try {
            $entryNames = @($archive.Entries | ForEach-Object { $_.FullName.Replace("\", "/") })
            foreach ($entry in $requiredEntries) {
                if ($entryNames -notcontains $entry) {
                    throw "IMS user test package is missing ZIP entry: $entry"
                }
            }
        }
        finally {
            $archive.Dispose()
        }

        $hash = (Get-FileHash -Algorithm SHA256 -LiteralPath $resolvedOutPath).Hash.ToLowerInvariant()
        [PSCustomObject]@{
            status = "ok"
            mode = "workbench_user_test_package_build"
            out_path = $resolvedOutPath
            zip_bytes = (Get-Item -LiteralPath $resolvedOutPath).Length
            zip_sha256 = $hash
            install_pages = 2
            user_guide_pages = 8
            target_requires_python = "3.12+"
            target_requires_node = $false
            target_requires_git = $false
            execution_performed = $false
            simulation_performed = $false
            historical_full_equality_claimed = $false
        } | ConvertTo-Json -Compress
    }
    finally {
        Pop-Location
        $env:PYTHONPATH = $previousPythonPath
    }
}
finally {
    if (Test-Path -LiteralPath $workRoot) {
        $resolvedWorkRoot = (Resolve-Path -LiteralPath $workRoot).Path
        $leaf = Split-Path -Leaf $resolvedWorkRoot
        if (
            -not $resolvedWorkRoot.StartsWith($tempRoot, [StringComparison]::OrdinalIgnoreCase) -or
            -not $leaf.StartsWith("ims-user-test-package-", [StringComparison]::OrdinalIgnoreCase)
        ) {
            throw "IMS user test package refuses cleanup outside its temporary root: $resolvedWorkRoot"
        }
        Remove-Item -LiteralPath $resolvedWorkRoot -Recurse -Force
    }
}
