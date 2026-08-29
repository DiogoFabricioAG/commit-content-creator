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

    if ($RemoteDir -notmatch "^[A-Za-z0-9._/-]+$") {
        throw "RemoteDir solo puede contener caracteres seguros de ruta Unix."
    }

    $remoteDirQuoted = '"' + $RemoteDir + '"'
    $remoteCommand = @'
set -euo pipefail

IFS= read -r GITHUB_WEBHOOK_SECRET
GITHUB_WEBHOOK_SECRET="${GITHUB_WEBHOOK_SECRET%$'\r'}"
if [ -z "$GITHUB_WEBHOOK_SECRET" ]; then
  echo "El webhook secret recibido está vacío." >&2
  exit 1
fi
export GITHUB_WEBHOOK_SECRET

remote_dir=__REMOTE_DIR__
env_file="$remote_dir/deploy/.env.production"
compose_file="$remote_dir/deploy/compose.yaml"

if [ ! -f "$env_file" ]; then
  echo "No existe $env_file en el VPS." >&2
  exit 1
fi

tmp_file="$(mktemp)"
cleanup() {
  rm -f "$tmp_file"
}
trap cleanup EXIT

awk '
  BEGIN { updated = 0 }
  /^GITHUB_WEBHOOK_SECRET=/ {
    print "GITHUB_WEBHOOK_SECRET=" ENVIRON["GITHUB_WEBHOOK_SECRET"]
    updated = 1
    next
  }
  { print }
  END {
    if (!updated) print "GITHUB_WEBHOOK_SECRET=" ENVIRON["GITHUB_WEBHOOK_SECRET"]
  }
' "$env_file" > "$tmp_file"

chmod 600 "$tmp_file"
mv "$tmp_file" "$env_file"
unset GITHUB_WEBHOOK_SECRET

docker compose --env-file "$env_file" -f "$compose_file" up -d --no-deps --force-recreate backend
docker compose --env-file "$env_file" -f "$compose_file" ps backend

healthy=""
for attempt in $(seq 1 20); do
  healthy="$(docker inspect --format '{{.State.Health.Status}}' laborin-backend 2>/dev/null || true)"
  if [ "$healthy" = "healthy" ]; then
    break
  fi
  sleep 2
done

if [ "$healthy" != "healthy" ]; then
  echo "laborin-backend no llegó a estado healthy." >&2
  docker logs --tail 80 laborin-backend >&2 || true
  exit 1
fi

curl --fail --silent --show-error --retry 5 --retry-delay 1 --retry-connrefused https://laborin.meowlab.tech/health
printf '\nWebhook secret actualizado y backend reiniciado.\n'
'@
    $remoteCommand = $remoteCommand.Replace("__REMOTE_DIR__", $remoteDirQuoted)

    $sshArgs = @(
        "-o", "IdentitiesOnly=yes",
        "-o", "BatchMode=yes",
        "-i", $KeyPath,
        "$User@$Server"
    )

    $secret | & ssh @sshArgs $remoteCommand
    if ($LASTEXITCODE -ne 0) {
        throw "No se pudo actualizar el webhook secret en el VPS (ssh exitó con $LASTEXITCODE)."
    }
}
finally {
    if ($secretPointer -ne [IntPtr]::Zero) {
        [Runtime.InteropServices.Marshal]::ZeroFreeBSTR($secretPointer)
    }
    $secret = $null
    $secretSecure = $null
}
