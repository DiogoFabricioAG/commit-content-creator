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

## Milestone 1 a 12 · Pipeline completo de LaborIN

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

## Milestone 13 · Production Readiness & Demo

Este milestone no agrega otra feature principal: convierte el pipeline implementado en una demo pública reproducible y deja explícitas las dependencias externas.

| ID | Tarea | Dependencias | Responsable | Estado | Entregable / Evidencia |
|---|---|---|---|---|---|
| M13-01 | Validar GitHub App e ingestión real | M1-M3 | Backend / QA | **Done** | Push firmado recibido en `laborin.meowlab.tech`, dos respuestas `202` y una sola fila Convex para `deliveryId` `2725ab5c…` |
| M13-02 | Completar OAuth de GitHub e identidad | M13-01 | Backend | **Backlog** | `/auth/github/callback` con `state`, intercambio de código y usuario vinculado |
| M13-03 | Validar Kapso + aprobación por WhatsApp | M7-M10 | Integrations / QA | **In progress** | Salida real aceptada por Kapso (`wamid...`) con `DEMO_MODE=false`; falta probar webhook entrante y revisión V2 |
| M13-04 | Validar LinkedIn OAuth y publicación | M8-M11 | Integrations / QA | **Ready** | Solo la versión vigente aprobada produce un URN de LinkedIn |
| M13-05 | Ensayar demo pública y capturar evidencia | M13-01, M13-03, M13-04 | QA / Demo | **Backlog** | Guion ejecutado, logs/capturas y bitácora final actualizada |


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

1. Ejecutar M13-01 con un repositorio de prueba y conservar el `deliveryId` como evidencia.
2. Abrir M13-02 en paralelo con una implementación aislada del callback OAuth.
3. Validar M13-03 y M13-04 solo con credenciales cargadas fuera del repositorio.
4. Reservar M13-05 para integrar el recorrido completo y actualizar la historia del proyecto.

## Milestones 14 a 19 · Plataforma configurable y multiusuario

El detalle delegable está en [Roadmap siguiente fase](./ROADMAP-NEXT-PHASE.md). La prioridad usa una escala de 1 a 5: 5 es crítica/bloqueante y 1 es polish.

| Milestone | Enfoque | Prioridad base | Estado | Dependencia principal |
|---|---|---:|---|---|
| M14 | Identidad, sesiones, OAuth y aislamiento multiusuario | **5** | **Backlog** | Decisión users vs workspaces |
| M15 | Onboarding y preferencias de estilo/formato | **5** | **Backlog** | M14-01, M14-02 |
| M16 | Texto, enlaces, imágenes, videos, diagramas de arquitectura y publisher rico | **4** | **Backlog** | M15-01; permisos externos |
| M17 | Bot WhatsApp natural, GPT, botones y memoria acotada | **4** | **In progress** | ventana 24h y batch de pendientes listos; falta GPT/memoria |
| M18 | Landing, confianza y polish responsive | **3** | **In progress** | M18-01 terminado; M18-02 y M18-03 pendientes |
| M19 | Observabilidad, E2E multiusuario y demo final | **4** | **Backlog** | M14–M18 |
| M20 | Digest histórico desde landing y preferencias | **5** | **In progress** | M14, M15; núcleo backend listo para integrar |
| M21 | Commit `final`, revisión y publicación final | **5** | **Backlog** | M20, M16, M17 |

### Primera tanda para delegar

- **M14-01**: modelo de tenancy y aislamiento.
- **M14-02**: sesión y OAuth de GitHub.
- **M15-01**: contrato de preferencias editoriales.
- **M16-01**: contratos de contenido rico.
- **M16-05**: generador de diagramas de arquitectura con evidencia y fallback textual.
- **M17-02**: router conversacional GPT en sandbox.
- **M18-01**: **Done** — landing de conversión responsive con recorrido y contratos mock.
- **M20-01**: integrar `HistoricalDigestBuilder` con el endpoint/acción autenticada del digest.

### Demo en vivo

El runbook de las dos pruebas está en [docs/demo/LIVE-DEMO-PLAN.md](./demo/LIVE-DEMO-PLAN.md). La implementación debe producir un solo digest histórico, mantener aprobación humana y reservar el commit exacto `final` para el último push de la corrida.
