param(
    [string]$Server = "2.24.64.161",
    [string]$User = "root",
    [string]$KeyPath = (Join-Path $env:USERPROFILE ".ssh\facturaya_hostinger_ed25519"),
    [string]$RemoteDir = "/opt/laborin"
)

$ErrorActionPreference = "Stop"

if (-not (Test-Path -LiteralPath $KeyPath -PathType Leaf)) {
    throw "No se encontró la llave SSH: $KeyPath"
}

$remoteScriptLocal = Join-Path $PSScriptRoot "set-webhook-secret.remote.sh"
if (-not (Test-Path -LiteralPath $remoteScriptLocal -PathType Leaf)) {
    throw "No se encontró el script remoto: $remoteScriptLocal"
}

if ($RemoteDir -notmatch "^[A-Za-z0-9._/-]+$") {
    throw "RemoteDir solo puede contener caracteres seguros de ruta Unix."
}

$sshArgs = @(
    "-o", "IdentitiesOnly=yes",
    "-o", "BatchMode=yes",
    "-i", $KeyPath,
    "$User@$Server"
)

$remoteScriptName = "laborin-set-webhook-secret-$([Guid]::NewGuid().ToString('N')).sh"
$remoteScriptPath = "/tmp/$remoteScriptName"
$remoteScriptTarget = "$User@$Server`:$remoteScriptPath"
$uploaded = $false
$secretSecure = Read-Host "Webhook secret nuevo (no se mostrará)" -AsSecureString
$secretPointer = [IntPtr]::Zero
$secret = $null

try {
    $secretPointer = [Runtime.InteropServices.Marshal]::SecureStringToBSTR($secretSecure)
    $secret = [Runtime.InteropServices.Marshal]::PtrToStringBSTR($secretPointer)

    if ([string]::IsNullOrWhiteSpace($secret)) {
        throw "El webhook secret no puede estar vacío."
    }

    if ($secret.Contains("`r") -or $secret.Contains("`n")) {
        throw "El webhook secret debe estar en una sola línea."
    }

    & scp @(
        "-o", "IdentitiesOnly=yes",
        "-o", "BatchMode=yes",
        "-i", $KeyPath,
        $remoteScriptLocal,
        $remoteScriptTarget
    )
    if ($LASTEXITCODE -ne 0) {
        throw "No se pudo transferir el script temporal al VPS (scp exitó con $LASTEXITCODE)."
    }
    $uploaded = $true

    $secret | & ssh @sshArgs "bash $remoteScriptPath $RemoteDir"
    if ($LASTEXITCODE -ne 0) {
        throw "No se pudo actualizar el webhook secret en el VPS (ssh exitó con $LASTEXITCODE)."
    }
}
finally {
    if ($uploaded) {
        & ssh @sshArgs "rm -f $remoteScriptPath" *> $null
    }

    if ($secretPointer -ne [IntPtr]::Zero) {
        [Runtime.InteropServices.Marshal]::ZeroFreeBSTR($secretPointer)
    }
    $secret = $null
    $secretSecure = $null
}
