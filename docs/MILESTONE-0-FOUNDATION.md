# Milestone 0 · Foundation

## Propósito

Dejar un proyecto arrancable, verificable y delegable. Al cerrar este milestone, cualquier miembro del equipo debe poder clonar el repositorio, configurar variables locales seguras, levantar Web + Backend + Convex y ejecutar los checks básicos sin conocer decisiones implícitas.

Este milestone prepara el terreno; no intenta resolver todavía GitHub, LinkedIn, Kapso ni la inteligencia de historias.

## Resultado esperado

```text
apps/web       ─┐
apps/backend   ─┼─ contratos iniciales y comandos reproducibles
convex/        ─┘
```

Debe existir una base funcional para que Milestone 1 pueda recibir un webhook de GitHub y persistirlo en Convex.

## Alcance

### Incluido

- Monorepo de pnpm para el dashboard web y el código Convex.
- Proyecto Python de FastAPI gestionado con uv.
- Configuración de TypeScript, Tailwind, shadcn/ui y calidad mínima del frontend.
- Esqueleto FastAPI con `/health` y configuración validada.
- Esquema Convex inicial, con los índices necesarios para idempotencia futura.
- Variables de entorno documentadas sin secretos reales.
- Tests mínimos y comandos de desarrollo escritos en el README.
- Fixture local de salud/demo que no publique ni llame a proveedores reales.

### Fuera de alcance

- OAuth real de GitHub o LinkedIn.
- Recepción de webhooks reales.
- Llamadas a OpenAI, Kapso o LinkedIn.
- Story detection, aprobación natural y publicación.
- Autenticación multiusuario, RBAC, billing o despliegue productivo.

## Estado inicial registrado

Este bloque conserva el punto de partida previo al bootstrap. No debe leerse como el estado actual del repositorio.

- [ ] No hay estructura de monorepo.
- [ ] No existe `package.json`, `pnpm-workspace.yaml` ni `pyproject.toml`.
- [ ] No existe `convex/schema.ts`.
- [ ] No existe frontend ni backend.
- [ ] No existe control de versiones Git local.

El último punto fue un bloqueo operativo para ramas y PRs y quedó resuelto al inicializar `main` y conectar `origin` con el repositorio de GitHub.

## Estado actual

- [x] M0-01 Bootstrap del workspace.
- [x] M0-02 Esqueleto Web.
- [x] M0-03 Esqueleto FastAPI.
- [x] M0-04 Modelo Convex inicial: schema, funciones, codegen y deployment de desarrollo verificados.
- [x] M0-05 Contratos y configuración.
- [x] M0-06 Quality gate y fixture local: checks completos y smoke de idempotencia ejecutado.

## Desglose delegable

### M0-01 · Bootstrap del workspace

**Responsable sugerido:** Tech Lead / Bootstrap.

**Dependencias:** ninguna.

**Entregables:** estructura de carpetas, `package.json`, `pnpm-workspace.yaml`, `pyproject.toml`, `.gitignore`, README raíz y comandos comunes.

**Criterios de aceptación:**

- `pnpm install` termina sin error desde la raíz.
- El entorno Python se crea con uv y puede instalar dependencias.
- Los comandos de web, backend, Convex, tests y checks están documentados.
- No se escriben secretos en archivos versionados.
- La estructura coincide con la especificación del prompt maestro.

### M0-02 · Esqueleto Web

**Responsable sugerido:** Frontend.

**Dependencias:** M0-01.

**Entregables:** `apps/web` con Next.js + TypeScript + Tailwind + shadcn/ui; layout inicial de Laborin; cliente/configuración de Convex preparada para suscripciones.

**Criterios de aceptación:**

- El servidor de desarrollo arranca con el comando documentado.
- La pantalla inicial identifica el estado de configuración y no simula datos reales.
- La configuración de Convex usa una variable pública únicamente para la URL pública.
- `lint`, typecheck y build pasan.

### M0-03 · Esqueleto FastAPI

**Responsable sugerido:** Backend.

**Dependencias:** M0-01.

**Entregables:** `apps/backend/app/main.py`, configuración por entorno, router `/health`, manejo base de errores y estructura de módulos del prompt.

**Criterios de aceptación:**

- FastAPI arranca con el comando documentado.
- `GET /health` devuelve estado JSON y no expone secretos.
- Pydantic valida la configuración obligatoria al iniciar.
- Ruff, Pyright/mypy y pytest pasan.
- La integración con Convex queda aislada detrás de un módulo cliente, aunque las credenciales reales aún no estén configuradas.

### M0-04 · Modelo Convex inicial

**Responsable sugerido:** Data / Backend.

**Dependencias:** M0-01.

**Entregables:** `convex/convex/schema.ts`, funciones mínimas de consulta/mutación y tipos compartidos para `users`, `repositories`, `githubEvents`, `commits` y `activityEvents`.

**Criterios de aceptación:**

- El esquema se valida con Convex.
- Los bindings oficiales existen en `convex/convex/_generated` y `typecheck:generated` pasa.
- `githubEvents.deliveryId` tiene un índice que permita deduplicación.
- El modelo no mezcla datos de usuarios sin un `userId` o relación explícita.
- Un evento y un commit pueden representar estados de procesamiento sin usar blobs opacos como sustituto del modelo.
- Las funciones no aceptan acceso arbitrario a datos de otro usuario.

### M0-05 · Contratos y configuración compartida

**Responsable sugerido:** Tech Lead + Backend.

**Dependencias:** M0-01.

**Entregables:** `.env.example`, convenciones de nombres, tipos/DTOs iniciales, contrato de errores y [contratos de arquitectura](./ARCHITECTURE-CONTRACTS.md) actualizado si aparecen decisiones nuevas.

**Criterios de aceptación:**

- Cada variable tiene propósito y dueño documentados.
- Las variables de frontend están separadas de secretos del backend.
- Los payloads externos se validarán en el borde, no dentro del dominio.
- Los estados de pipeline y los nombres de eventos no divergen entre capas.

### M0-06 · Quality gate y fixture local

**Responsable sugerido:** QA / Developer Experience.

**Dependencias:** M0-02, M0-03, M0-04 y M0-05.

**Entregables:** comandos de CI/local checks, fixture de evento/commit no sensible, pruebas de smoke para Web + FastAPI + Convex y guía de diagnóstico.

**Criterios de aceptación:**

- Un miembro nuevo puede ejecutar el smoke test siguiendo solo el README.
- El fixture no contiene tokens, teléfonos reales ni datos privados.
- Un fallo de configuración muestra un mensaje accionable.
- El pipeline local falla si lint, typecheck o tests fallan.
- El smoke de Convex confirma persistencia y deduplicación por `deliveryId`.

## Orden recomendado y paralelización

```text
M0-01 Bootstrap
   ├── M0-02 Web ──────────┐
   ├── M0-03 FastAPI ──────┼── M0-06 Quality gate
   ├── M0-04 Convex ───────┘
   └── M0-05 Contratos/configuración
```

M0-02, M0-03, M0-04 y M0-05 pueden avanzar en paralelo después de M0-01, siempre que respeten los contratos de [ARCHITECTURE-CONTRACTS.md](./ARCHITECTURE-CONTRACTS.md). M0-06 integra y verifica; no debe convertirse en una segunda implementación de cada módulo.

## Evidencia de cierre

```text
pnpm check                                      ✓
pnpm --filter @proof-of-work/convex typecheck:generated  ✓
uv run python apps/backend/scripts/convex_smoke.py       ✓
```

El smoke test se ejecutó contra el deployment de desarrollo configurado por el CLI y no imprime la URL ni ningún valor del entorno.

## Definition of Done del milestone

- [x] Estructura de monorepo creada.
- [x] Web, backend y Convex tienen arranque documentado.
- [x] `/health` funciona localmente.
- [x] Esquema Convex valida y tiene índices iniciales.
- [x] Cliente Python de Convex está preparado para el primer vertical slice.
- [x] `.env.example` no contiene valores sensibles.
- [x] Tests, lint, typecheck y build pasan.
- [x] Una persona nueva puede reproducir el entorno desde cero.
- [x] Las tareas M0 están enlazadas en [TASK-BOARD.md](./TASK-BOARD.md).

## Handoff de cierre

El responsable de M0 debe dejar en el PR:

1. comandos exactos de instalación, desarrollo y validación;
2. captura o salida textual de los checks principales;
3. variables que siguen faltando y cómo obtenerlas sin compartir secretos;
4. lista de decisiones tomadas y contratos modificados;
5. siguiente tarea recomendada: **M1-01 — webhook GitHub con firma e idempotencia**.
