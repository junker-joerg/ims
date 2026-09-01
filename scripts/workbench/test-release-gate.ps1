[CmdletBinding()]
param(
    [string]$RepoRoot,
    [string]$WorkRoot
)

$ErrorActionPreference = "Stop"
if ([string]::IsNullOrWhiteSpace($RepoRoot)) {
    $RepoRoot = (Resolve-Path (Join-Path $PSScriptRoot "..\..")).Path
}
$resolvedRepoRoot = (Resolve-Path -LiteralPath $RepoRoot).Path
$ownsWorkRoot = [string]::IsNullOrWhiteSpace($WorkRoot)

if ($ownsWorkRoot) {
    $WorkRoot = Join-Path (
        [IO.Path]::GetTempPath()
    ) ("ims-pr70-" + [guid]::NewGuid().ToString("N"))
}

$resolvedWorkRoot = [IO.Path]::GetFullPath($WorkRoot)
$pytestTempRoot = Join-Path $resolvedWorkRoot "pytest-temp"
$pytestCacheRoot = Join-Path $resolvedWorkRoot "pytest-cache"
$zipPath = Join-Path $resolvedWorkRoot "ims-workbench-local.zip"
$portableRoot = Join-Path $resolvedWorkRoot "ims-workbench"
$userPackagePath = Join-Path $resolvedWorkRoot "IMS-Workbench-2026-Windows-Test.zip"
$previousPythonPath = $env:PYTHONPATH

function Assert-NativeSuccess {
    param([string]$Step)

    if ($LASTEXITCODE -ne 0) {
        throw "PR70 Windows release gate failed during ${Step}: exit code $LASTEXITCODE"
    }
}

function Assert-CleanWorkRoot {
    param([string]$Path)

    if (Test-Path -LiteralPath $Path) {
        if (-not (Test-Path -LiteralPath $Path -PathType Container)) {
            throw "PR70 Windows release gate work root is not a directory: $Path"
        }
        if (Get-ChildItem -LiteralPath $Path -Force | Select-Object -First 1) {
            throw "PR70 Windows release gate work root must be empty: $Path"
        }
        return
    }
    New-Item -ItemType Directory -Path $Path | Out-Null
}

function Remove-OwnedWorkRoot {
    param([string]$Path)

    if (-not $ownsWorkRoot -or -not (Test-Path -LiteralPath $Path)) {
        return
    }
    $resolvedPath = (Resolve-Path -LiteralPath $Path).Path
    $tempRoot = [IO.Path]::GetFullPath([IO.Path]::GetTempPath())
    $leaf = Split-Path -Leaf $resolvedPath
    if (
        -not $resolvedPath.StartsWith($tempRoot, [StringComparison]::OrdinalIgnoreCase) -or
        -not $leaf.StartsWith("ims-pr70-", [StringComparison]::OrdinalIgnoreCase)
    ) {
        throw "PR70 Windows release gate refuses cleanup outside its temp root: $resolvedPath"
    }
    Remove-Item -LiteralPath $resolvedPath -Recurse -Force
}

Assert-CleanWorkRoot -Path $resolvedWorkRoot

try {
    Push-Location $resolvedRepoRoot
    try {
        $env:PYTHONPATH = Join-Path $resolvedRepoRoot "python_port"

        python -m pytest -q `
            --basetemp $pytestTempRoot `
            -o "cache_dir=$pytestCacheRoot"
        Assert-NativeSuccess -Step "Python tests"

        npm.cmd run build --prefix .\frontend
        Assert-NativeSuccess -Step "frontend build"

        $reportJson = python -m ims.api.production_release_corpus_report --repo-root $resolvedRepoRoot
        Assert-NativeSuccess -Step "production corpus report"
        $report = $reportJson | ConvertFrom-Json
        if (
            $report.status -ne "blocked" -or
            $report.release_decision -ne "blocked_calculated_core_validation" -or
            $report.coverage_complete -ne $true -or
            $report.reference_count -ne 19 -or
            $report.covered_periods -ne 6300 -or
            $report.missing_calculated_export_count -ne 15 -or
            $report.production_release_approved -ne $false -or
            $report.writes_performed -ne $false -or
            $report.execution_performed -ne $false -or
            $report.simulation_performed -ne $false -or
            $report.historical_full_equality_claimed -ne $false
        ) {
            throw "PR70 Windows release gate rejects unexpected production corpus report state"
        }

        $bundleJson = python -m ims.api.workbench_bundle_build `
            --root $resolvedRepoRoot `
            --frontend-dist (Join-Path $resolvedRepoRoot "frontend\dist") `
            --out $zipPath
        Assert-NativeSuccess -Step "bundle build"
        $bundle = $bundleJson | ConvertFrom-Json
        if ($bundle.archive_created -ne $true -or $bundle.execution_performed -ne $false) {
            throw "PR70 Windows release gate rejects bundle result"
        }

        $bundleSmokeJson = python -m ims.api.workbench_bundle_smoke --zip-path $zipPath
        Assert-NativeSuccess -Step "bundle smoke"
        $bundleSmoke = $bundleSmokeJson | ConvertFrom-Json
        if ($bundleSmoke.status -ne "ok" -or $bundleSmoke.execution_performed -ne $false) {
            throw "PR70 Windows release gate rejects bundle smoke result"
        }

        $stagingJson = python -m ims.api.workbench_portable_staging `
            --zip-path $zipPath `
            --out $portableRoot
        Assert-NativeSuccess -Step "portable staging"
        $staging = $stagingJson | ConvertFrom-Json
        if ($staging.status -ne "ok" -or $staging.execution_performed -ne $false) {
            throw "PR70 Windows release gate rejects portable staging result"
        }

        $stagingSmokeJson = python -m ims.api.workbench_portable_staging_smoke --root $portableRoot
        Assert-NativeSuccess -Step "portable staging smoke"
        $stagingSmoke = $stagingSmokeJson | ConvertFrom-Json
        if ($stagingSmoke.status -ne "ok" -or $stagingSmoke.execution_performed -ne $false) {
            throw "PR70 Windows release gate rejects portable staging smoke result"
        }

        $portableReadinessJson = python -m ims.api.workbench_portable_readiness `
            --root $portableRoot `
            --layout portable
        Assert-NativeSuccess -Step "portable readiness"
        $portableReadiness = $portableReadinessJson | ConvertFrom-Json
        if (
            $portableReadiness.status -ne "ok" -or
            $portableReadiness.execution_enabled -ne $false
        ) {
            throw "PR70 Windows release gate rejects portable readiness result"
        }

        $releaseJson = python -m ims.api.workbench_release_smoke `
            --repo-root $resolvedRepoRoot `
            --zip-path $zipPath `
            --portable-root $portableRoot
        Assert-NativeSuccess -Step "release smoke"
        $release = $releaseJson | ConvertFrom-Json
        if (
            $release.release_ready -ne $true -or
            $release.artifact_scripts_match_repo -ne $true -or
            $release.pr66_demo_adapter_separated -ne $true -or
            $release.execution_performed -ne $false -or
            $release.simulation_performed -ne $false -or
            $release.historical_full_equality_claimed -ne $false
        ) {
            throw "PR70 Windows release gate rejects release smoke result"
        }

        $userPackageJson = & (Join-Path $resolvedRepoRoot "scripts\workbench\build-user-test-package.ps1") `
            -RepoRoot $resolvedRepoRoot `
            -OutPath $userPackagePath
        Assert-NativeSuccess -Step "user test package build"
        $userPackage = $userPackageJson | ConvertFrom-Json
        if (
            $userPackage.status -ne "ok" -or
            $userPackage.install_pages -ne 2 -or
            $userPackage.user_guide_pages -ne 10 -or
            $userPackage.target_requires_node -ne $false -or
            $userPackage.execution_performed -ne $false -or
            $userPackage.simulation_performed -ne $false -or
            $userPackage.historical_full_equality_claimed -ne $false
        ) {
            throw "PR70 Windows release gate rejects user test package"
        }

        & (Join-Path $portableRoot "check-workbench.cmd")
        Assert-NativeSuccess -Step "portable check script"

        [PSCustomObject]@{
            status = "ok"
            mode = "windows_release_gate"
            report_contract_version = $report.report_contract_version
            corpus_report_status = $report.status
            production_release_approved = $false
            missing_calculated_export_count = $report.missing_calculated_export_count
            release_ready = $release.release_ready
            user_test_package_ready = $true
            writes_performed = $false
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
    Remove-OwnedWorkRoot -Path $resolvedWorkRoot
}
