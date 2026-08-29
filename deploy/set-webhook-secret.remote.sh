#!/usr/bin/env bash
set -euo pipefail

remote_dir="${1:?remote directory is required}"
env_file="$remote_dir/deploy/.env.production"
compose_file="$remote_dir/deploy/compose.yaml"

IFS= read -r GITHUB_WEBHOOK_SECRET || true
GITHUB_WEBHOOK_SECRET="${GITHUB_WEBHOOK_SECRET%$'\r'}"
if [ -z "$GITHUB_WEBHOOK_SECRET" ]; then
  echo "El webhook secret recibido está vacío." >&2
  exit 1
fi
export GITHUB_WEBHOOK_SECRET

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
