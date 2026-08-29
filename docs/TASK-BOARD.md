# Tablero de trabajo

Este tablero es la lista operativa para delegar trabajo. El estado actual refleja que Foundation está cerrado y que el siguiente corte es el borde GitHub del primer vertical slice.

Milestone remoto: [M0 - Foundation](https://github.com/DiogoFabricioAG/commit-content-creator/milestone/1).

## Estados

`Backlog` → `In progress` → `Review` → `Done`

Usar `Blocked` cuando exista una dependencia externa o decisión material que no pueda resolverse localmente. Toda tarea bloqueada debe incluir evidencia y una acción concreta para desbloquearla.

## Milestone 0 · Foundation

| ID | Tarea | Dependencias | Responsable sugerido | Estado | Entrega |
|---|---|---|---|---|---|
| M0-01 | Bootstrap del workspace | — | Tech Lead | **Done** | Monorepo, comandos, Git inicial/remoto definido |
| M0-02 | Esqueleto Web | M0-01 | Frontend | **Done** | Next.js arrancable, layout base, checks |
| M0-03 | Esqueleto FastAPI | M0-01 | Backend | **Done** | health, config Pydantic, checks |
| M0-04 | Modelo Convex inicial | M0-01 | Data/Backend | **Done** | Schema, codegen, queries/mutations e idempotencia verificadas |
| M0-05 | Contratos y configuración | M0-01 | Tech Lead + Backend | **Done** | env.example, DTOs, contratos |
| M0-06 | Quality gate y fixture local | M0-02, M0-03, M0-04, M0-05 | QA/DX | **Done** | `pnpm check` y smoke Convex reproducible |

## Milestone 1 a 12 · Pipeline Completo (Proof of Work)

| ID | Milestone | Dependencias | Responsable | Estado | Entregable / Evidencia |
|---|---|---|---|---|---|
| M1 | GitHub → Convex Ingestion | M0 | Backend | **Done** | Webhook HMAC SHA-256, deduplicación `deliveryId`, persistencia |
| M2 | Commit Extraction & Normalizer | M1 | Backend | **Done** | Normalizador de diffs, filtrado de lockfiles/ruido, `commits:record` |
| M3 | Live Activity Dashboard | M2 | Frontend | **Done** | Componente reactivo Next.js + Convex sync en vivo |
| M4 | Commit Intelligence | M2 | AI / Backend | **Done** | `CommitAnalyzer` estructurado (Pydantic), tecnologías e impacto |
| M5-M6 | Story Memory & Detection | M4 | AI / Backend | **Done** | `StoryDetector` para agrupar commits en arcos narrativos explicables |
| M7-M8 | LinkedIn Draft Generation & OAuth | M5-M6 | AI / Backend | **Done** | `ContentGenerator` con claims grounded + OAuth 2.0 y cifrado Fernet |
| M9-M10 | WhatsApp (Kapso) & Approval Agent | M7-M8 | AI / Backend | **Done** | `ApprovalAgent` con NLU seguro (approve, revise, reject, clarify) + loop de revisión V2 |
| M11 | LinkedIn Posts API Publishing | M10 | Backend | **Done** | `LinkedInPublisher` validado solo ante versión aprobada + URN guardado |
| M12 | E2E Demo Script & Polish | M1-M11 | QA / Demo | **Done** | Script `run_demo_pipeline.py` verificado contra Convex Cloud |


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
