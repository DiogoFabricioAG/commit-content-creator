# Despliegue de Laborin

Esta receta despliega la primera rebanada en el VPS `2.24.64.161` sin publicar puertos nuevos al exterior. Web y Backend se unen a la red Docker existente `facturaya-ai_default`; el Caddy central termina HTTPS y enruta por hostname/path.

## DNS

En la zona DNS de `meowlab.tech`:

```text
Tipo: A
Host: laborin
Valor: 2.24.64.161
TTL: automático
```

No agregues un `AAAA` para `laborin` salvo que exista un IPv6 válido configurado en el VPS. Si usas Cloudflare, deja el registro como DNS-only durante la emisión inicial del certificado de Caddy.

## URLs para la GitHub App

```text
Homepage URL:  https://laborin.meowlab.tech/
Webhook URL:   https://laborin.meowlab.tech/webhooks/github
Redirect URI:  https://laborin.meowlab.tech/auth/github/callback
```

El webhook ya corresponde a una ruta implementada. El callback OAuth queda reservado en Caddy para M1; no se debe tratar como flujo OAuth completo hasta que la validación de `state` y el intercambio de código estén implementados.

## Variables del VPS

Copiar `deploy/.env.production.example` a `deploy/.env.production` y completar `CONVEX_URL`, `NEXT_PUBLIC_CONVEX_URL` y `GITHUB_WEBHOOK_SECRET` fuera de Git. La URL de Convex no es un secreto, pero el secreto del webhook sí.

Para actualizar todos los secretos de producción (Kapso, OpenAI, GitHub, LinkedIn) en el VPS desde Windows de forma segura e interactiva:

```powershell
.\deploy\set-production-secrets.ps1
```

O si deseas actualizar únicamente el secreto de GitHub:

```powershell
.\deploy\set-webhook-secret.ps1
```

Los scripts solicitan los valores como entradas ocultas, transfieren un script temporal sin secretos, actualizan `/opt/laborin/deploy/.env.production`, recrean solo `laborin-backend` y esperan a que `/health` esté disponible. Si PowerShell bloquea la ejecución por la política local, usar:

```powershell
powershell -ExecutionPolicy Bypass -File .\deploy\set-production-secrets.ps1
```


## Comandos de despliegue

Desde `/opt/laborin` en el VPS:

```bash
git fetch origin
git checkout main
git pull --ff-only origin main
docker compose --env-file deploy/.env.production -f deploy/compose.yaml build
docker compose --env-file deploy/.env.production -f deploy/compose.yaml up -d
```

Después de validar que ambos contenedores están saludables, añadir el contenido de `deploy/Caddyfile.laborin` al Caddyfile central, validar la configuración y recargar solo el contenedor Caddy. El orden evita dejar el hostname apuntando a un upstream inexistente.

## Verificación

```bash
docker compose --env-file deploy/.env.production -f deploy/compose.yaml ps
curl -fsS https://laborin.meowlab.tech/health
curl -fsS https://laborin.meowlab.tech/
```

El endpoint webhook debe probarse con una firma HMAC real de GitHub; no se debe enviar un POST sin firma como prueba de disponibilidad.
