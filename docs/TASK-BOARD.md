# Tablero de trabajo

Este tablero es la lista operativa para delegar trabajo. El estado inicial refleja que el repositorio aún no tiene bootstrap técnico.

## Estados

`Backlog` → `In progress` → `Review` → `Done`

Usar `Blocked` cuando exista una dependencia externa o decisión material que no pueda resolverse localmente. Toda tarea bloqueada debe incluir evidencia y una acción concreta para desbloquearla.

## Milestone 0 · Foundation

| ID | Tarea | Dependencias | Responsable sugerido | Estado | Entrega |
|---|---|---|---|---|---|
| M0-01 | Bootstrap del workspace | — | Tech Lead | **In progress** | Monorepo, comandos, Git inicial/remoto definido |
| M0-02 | Esqueleto Web | M0-01 | Frontend | Backlog | Next.js arrancable, layout base, checks |
| M0-03 | Esqueleto FastAPI | M0-01 | Backend | Backlog | `/health`, config Pydantic, checks |
| M0-04 | Modelo Convex inicial | M0-01 | Data/Backend | Backlog | Schema, índices, queries/mutations mínimas |
| M0-05 | Contratos y configuración | M0-01 | Tech Lead + Backend | Backlog | `.env.example`, DTOs, contratos |
| M0-06 | Quality gate y fixture local | M0-02, M0-03, M0-04, M0-05 | QA/DX | Backlog | Smoke test reproducible |

## Siguiente milestone preparado

Estas tareas no comienzan hasta cerrar M0, pero ya tienen una secuencia clara:

| ID | Tarea | Dependencias | Estado |
|---|---|---|---|
| M1-01 | Endpoint GitHub `push` con firma `X-Hub-Signature-256` | M0 | Backlog |
| M1-02 | Idempotencia por `X-GitHub-Delivery` | M1-01, M0-04 | Backlog |
| M1-03 | Persistencia de `githubEvent` y actividad | M1-02, M0-04 | Backlog |
| M1-04 | Procesador fuera del request path | M1-03, M0-03 | Backlog |

## Plantilla de asignación

Copiar este bloque a una issue, mensaje o tarea de agente:

```md
### [ID] Nombre corto

Objetivo:

Contexto:
- Leer: docs/MILESTONE-0-FOUNDATION.md
- Respetar: docs/ARCHITECTURE-CONTRACTS.md

Dependencias:

Entregables:

Criterios de aceptación:
-

Fuera de alcance:
-

Checks esperados:
-

Handoff:
- Archivos cambiados:
- Decisiones:
- Riesgos/bloqueos:
- Siguiente tarea sugerida:
```

## Orden de asignación recomendado

1. Asignar M0-01 a una sola persona/agente para evitar tres bootstraps incompatibles.
2. En cuanto M0-01 esté revisado, asignar M0-02, M0-03, M0-04 y M0-05 en paralelo.
3. Reservar M0-06 para integrar; no asignarlo antes de que existan los tres runtimes.
4. No abrir trabajo de publicación real antes de tener contratos, fixtures y pruebas de aprobación segura.
