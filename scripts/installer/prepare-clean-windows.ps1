[CmdletBinding()]
param([string]$Destination = (Join-Path $PSScriptRoot '..\..\.tmp-pr-ap1\clean-windows-kit'))
$ErrorActionPreference = 'Stop'
$repo = (Resolve-Path (Join-Path $PSScriptRoot '..\..')).Path
$kit = [IO.Path]::GetFullPath($Destination)
New-Item -ItemType Directory -Force -Path $kit | Out-Null
Copy-Item -LiteralPath (Join-Path $repo 'dist\installer\IMS-Setup-2.0.0-alpha.1-win-x64.exe') -Destination $kit
Copy-Item -LiteralPath (Join-Path $repo 'dist\installer\IMS-Setup-2.0.0-alpha.1-win-x64.exe.sha256') -Destination $kit
Copy-Item -LiteralPath (Join-Path $repo 'dist\installer\IMS-Setup-2.0.0-alpha.0-win-x64.exe') -Destination $kit
Copy-Item -LiteralPath (Join-Path $repo 'docs\reports\ims_ap1_clean_windows_acceptance.md') -Destination $kit
$escapedKit = [Security.SecurityElement]::Escape($kit)
@"
<Configuration>
  <Networking>Disable</Networking>
  <MappedFolders>
    <MappedFolder><HostFolder>$escapedKit</HostFolder><SandboxFolder>C:\IMS-Abnahme</SandboxFolder><ReadOnly>true</ReadOnly></MappedFolder>
  </MappedFolders>
</Configuration>
"@ | Set-Content -LiteralPath (Join-Path $kit 'IMS-Clean-Windows.wsb') -Encoding utf8NoBOM
Write-Output "Abnahmekit vorbereitet: $kit (Sandbox nicht gestartet; Abnahme weiterhin offen)."
