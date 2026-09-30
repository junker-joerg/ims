[CmdletBinding()]
param([string]$Destination = (Join-Path $PSScriptRoot '..\..\build\inno'))
$ErrorActionPreference = 'Stop'
$toolRoot = [IO.Path]::GetFullPath($Destination)
New-Item -ItemType Directory -Force -Path $toolRoot | Out-Null
$download = Join-Path $toolRoot 'innosetup-6.7.3.exe'
Invoke-WebRequest -Uri 'https://github.com/jrsoftware/issrc/releases/download/is-6_7_3/innosetup-6.7.3.exe' -OutFile $download
$expectedHash = '9c73c3bae7ed48d44112a0f48e66742c00090bdb5bef71d9d3c056c66e97b732'
if ((Get-FileHash -LiteralPath $download -Algorithm SHA256).Hash.ToLowerInvariant() -ne $expectedHash) {
    throw 'Inno Setup SHA-256 mismatch'
}
if ((Get-AuthenticodeSignature -LiteralPath $download).Status -ne 'Valid') {
    throw 'Inno Setup signature is not valid'
}
$process = Start-Process -FilePath $download -ArgumentList '/VERYSILENT','/SUPPRESSMSGBOXES','/NORESTART','/CURRENTUSER',"/DIR=`"$toolRoot\compiler`"" -WindowStyle Hidden -Wait -PassThru
if ($process.ExitCode -ne 0) { throw "Inno Setup installation failed: $($process.ExitCode)" }
Write-Output (Join-Path $toolRoot 'compiler\ISCC.exe')
