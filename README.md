# Proof of Work

Proof of Work transforma trabajo real de desarrollo en historias publicables para LinkedIn. El producto observa evidencia del repositorio, agrupa trabajo relacionado, genera un borrador y espera aprobación humana por WhatsApp antes de publicar.

## Estado

Milestone 0 — Foundation listo; M1-01 es el siguiente corte de trabajo.

La primera rebanada funcional es:

GitHub push → FastAPI → Convex → commit persistido → dashboard reactivo.

La planificación y las reglas de colaboración están en docs/README.md.

## Requisitos locales

- Node.js 20.9 o superior
- pnpm 11
- Python 3.12 o superior
- uv
- Una cuenta/proyecto Convex para la conexión realtime; no es necesario para levantar el backend de salud

## Instalación

1. Copiar .env.example a .env y completar solo las variables disponibles.
2. Instalar JavaScript con pnpm install.
3. Crear el entorno Python con uv sync.
4. Ejecutar `pnpm dev:convex`; el CLI configura el deployment de desarrollo y genera los bindings en `convex/convex/_generated`.
5. Copiar la URL pública a `CONVEX_URL` y `NEXT_PUBLIC_CONVEX_URL` en el entorno local si se van a conectar Backend y Web.

## Desarrollo

- Web: pnpm dev:web → http://localhost:3000
- Backend: pnpm dev:backend → http://localhost:8000
- Salud: GET http://localhost:8000/health
- Convex: pnpm dev:convex

## Checks

- Todo: pnpm check
- Web lint: pnpm lint:web
- Web types: pnpm typecheck:web
- Backend lint: uv run ruff check apps/backend
- Backend types: uv run pyright apps/backend
- Backend tests: pnpm test:backend
- Convex bindings: pnpm --filter @proof-of-work/convex typecheck:generated
- Convex smoke: `CONVEX_URL=<deployment-url> uv run python apps/backend/scripts/convex_smoke.py`

El smoke test escribe un evento fixture en el deployment de desarrollo, repite la misma entrega y verifica que la segunda llamada sea deduplicada.

## Seguridad local

El bootstrap no activa GitHub, OpenAI, Kapso ni LinkedIn. Los fixtures son locales y no publican ni envían mensajes. No guardar secretos en el repositorio ni en variables NEXT_PUBLIC_*.
