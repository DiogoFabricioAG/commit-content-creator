param(
    [string]$Server = "2.24.64.161",
    [string]$User = "root",
    [string]$KeyPath = (Join-Path $env:USERPROFILE ".ssh\facturaya_hostinger_ed25519"),
    [string]$RemoteDir = "/opt/laborin"
)

$ErrorActionPreference = "Stop"

if (-not (Test-Path -LiteralPath $KeyPath -PathType Leaf)) {
    throw "No se encontro la llave SSH: $KeyPath"
}

Write-Host "==========================================================" -ForegroundColor Cyan
Write-Host "  CONFIGURACION SEGURA DE SECRETOS EN VPS ($Server)" -ForegroundColor Cyan
Write-Host "==========================================================" -ForegroundColor Cyan
Write-Host "Presiona ENTER en cualquier campo que desees mantener sin cambios." -ForegroundColor Gray
Write-Host ""

function Read-SecureSecret([string]$Prompt) {
    $sec = Read-Host "$Prompt (oculto)" -AsSecureString
    if ($null -eq $sec -or $sec.Length -eq 0) { return "" }
    $bstr = [Runtime.InteropServices.Marshal]::SecureStringToBSTR($sec)
    try {
        return [Runtime.InteropServices.Marshal]::PtrToStringBSTR($bstr)
    }
    finally {
        [Runtime.InteropServices.Marshal]::ZeroFreeBSTR($bstr)
    }
}

# 1. Kapso WhatsApp
Write-Host "--- [1] Credenciales de Kapso (WhatsApp) ---" -ForegroundColor Yellow
$kapsoApiKey = Read-SecureSecret "KAPSO_API_KEY"
$kapsoPhoneId = Read-Host "KAPSO_PHONE_NUMBER_ID"
$kapsoWebhookSec = Read-SecureSecret "KAPSO_WEBHOOK_SECRET"
$defaultPhone = Read-Host "DEFAULT_USER_PHONE (ej: +51999888777)"

# 2. GitHub & OpenAI
Write-Host "`n--- [2] GitHub & OpenAI ---" -ForegroundColor Yellow
$githubWebhookSec = Read-SecureSecret "GITHUB_WEBHOOK_SECRET"
$openaiApiKey = Read-SecureSecret "OPENAI_API_KEY"

# 3. LinkedIn & Encryption
Write-Host "`n--- [3] LinkedIn & Cifrado (Opcional) ---" -ForegroundColor Yellow
$linkedinClientId = Read-Host "LINKEDIN_CLIENT_ID"
$linkedinClientSec = Read-SecureSecret "LINKEDIN_CLIENT_SECRET"
$linkedinRedirectUri = Read-Host "LINKEDIN_REDIRECT_URI (ej: https://laborin.meowlab.tech/auth/linkedin/callback)"
$encryptionKey = Read-SecureSecret "TOKEN_ENCRYPTION_KEY"

# Build update payload
$updates = [System.Collections.Generic.Dictionary[string, string]]::new()
if ($kapsoApiKey) { $updates["KAPSO_API_KEY"] = $kapsoApiKey }
if ($kapsoPhoneId) { $updates["KAPSO_PHONE_NUMBER_ID"] = $kapsoPhoneId }
if ($kapsoWebhookSec) { $updates["KAPSO_WEBHOOK_SECRET"] = $kapsoWebhookSec }
if ($defaultPhone) { $updates["DEFAULT_USER_PHONE"] = $defaultPhone }
if ($githubWebhookSec) { $updates["GITHUB_WEBHOOK_SECRET"] = $githubWebhookSec }
if ($openaiApiKey) { $updates["OPENAI_API_KEY"] = $openaiApiKey }
if ($linkedinClientId) { $updates["LINKEDIN_CLIENT_ID"] = $linkedinClientId }
if ($linkedinClientSec) { $updates["LINKEDIN_CLIENT_SECRET"] = $linkedinClientSec }
if ($linkedinRedirectUri) { $updates["LINKEDIN_REDIRECT_URI"] = $linkedinRedirectUri }
if ($encryptionKey) { $updates["TOKEN_ENCRYPTION_KEY"] = $encryptionKey }

if ($updates.Count -eq 0) {
    Write-Host "`nNo se ingreso ningun valor nuevo. Operacion cancelada." -ForegroundColor Yellow
    exit 0
}

Write-Host "`nVariables a actualizar en el VPS: $($updates.Keys -join ', ')" -ForegroundColor Cyan

# Encode updates as JSON base64
$jsonPayload = $updates | ConvertTo-Json -Compress
$jsonBase64 = [System.Convert]::ToBase64String([System.Text.Encoding]::UTF8.GetBytes($jsonPayload))

$remoteDirQuoted = "'" + $RemoteDir.Replace("'", "'\\''") + "'"
$remoteCommand = @'
set -euo pipefail

JSON_UPDATES=$(printf '%s' '__JSON_BASE64__' | base64 -d)
if [ -z "$JSON_UPDATES" ]; then
  echo "El payload de secretos recibido esta vacio." >&2
  exit 1
fi
export JSON_UPDATES

remote_dir=__REMOTE_DIR__
env_file="$remote_dir/deploy/.env.production"
compose_file="$remote_dir/deploy/compose.yaml"

if [ ! -f "$env_file" ]; then
  echo "No existe $env_file en el VPS." >&2
  exit 1
fi

python3 - << 'PYEOF'
import json
import os
import sys

payload_str = os.environ.get("JSON_UPDATES", "{}")
updates = json.loads(payload_str)
env_path = "/opt/laborin/deploy/.env.production"

lines = []
existing_keys = set()

if os.path.exists(env_path):
    with open(env_path, "r", encoding="utf-8") as f:
        for line in f:
            stripped = line.strip()
            if stripped and not stripped.startswith("#") and "=" in stripped:
                k, _ = stripped.split("=", 1)
                k = k.strip()
                if k in updates:
                    lines.append(f"{k}={updates[k]}\n")
                    existing_keys.add(k)
                else:
                    lines.append(line)
            else:
                lines.append(line)

# Append new keys that were not in file
for k, v in updates.items():
    if k not in existing_keys:
        lines.append(f"{k}={v}\n")

tmp_path = env_path + ".tmp"
with open(tmp_path, "w", encoding="utf-8") as f:
    f.writelines(lines)

os.chmod(tmp_path, 0o600)
os.replace(tmp_path, env_path)
print(f"Actualizadas {len(updates)} variables en {env_path}")
PYEOF

docker compose --env-file "$env_file" -f "$compose_file" up -d --no-deps --force-recreate backend
docker compose --env-file "$env_file" -f "$compose_file" ps backend
curl -fsS https://laborin.meowlab.tech/health
printf '\nBackend reiniciado exitosamente con los nuevos secretos.\n'
'@
$remoteCommand = $remoteCommand.Replace("__REMOTE_DIR__", $remoteDirQuoted).Replace("__JSON_BASE64__", $jsonBase64)

$scriptBytes = [System.Text.Encoding]::UTF8.GetBytes($remoteCommand)
$base64Script = [System.Convert]::ToBase64String($scriptBytes)

$sshArgs = @(
    "-o", "IdentitiesOnly=yes",
    "-o", "BatchMode=yes",
    "-i", $KeyPath,
    "$User@$Server"
)

Write-Host "Enviando secretos de forma segura al VPS..." -ForegroundColor Cyan

& ssh @sshArgs "echo $base64Script | base64 -d | bash"

if ($LASTEXITCODE -ne 0) {
    throw "Fallo la actualizacion de secretos en el VPS (exit code $LASTEXITCODE)."
}

Write-Host "`nSecretos actualizados y servicio backend verificado en https://laborin.meowlab.tech/health" -ForegroundColor Green


