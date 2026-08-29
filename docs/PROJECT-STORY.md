# Proof of Work · Historia del proyecto

Esta bitácora conserva la historia que luego se contará en la demo final. Cada entrada debe conectar una necesidad del producto con una decisión técnica, una evidencia comprobable y un momento visible para quien vea la presentación.

## Tesis para la demo

Proof of Work convierte trabajo real de desarrollo en una historia publicable, sin obligar al desarrollador a detenerse para redactarla. La confianza del producto se demuestra en el recorrido completo:

```text
trabajo real → evidencia → historia explicable → borrador → aprobación humana → publicación
```

La aprobación ocurre por WhatsApp y la publicación solo puede suceder ante una aprobación explícita del borrador vigente.

## Línea de tiempo

### 2026-08-29 · Primera piedra: coordinación antes de integración

**Qué necesitábamos:** transformar el prompt maestro en trabajo repartible sin inventar módulos ni dependencias ocultas.

**Qué construimos:** milestone documental, tablero M0, contratos entre Web/FastAPI/Convex, reglas de handoff y criterios de terminado.

**Decisión:** avanzar por rebanadas verticales. La primera es GitHub → FastAPI → Convex → dashboard reactivo.

**Evidencia:** documentación versionada en `docs/`, repositorio remoto conectado y primer commit publicado.

**Momento de demo:** todavía no hay demo completa; esta etapa explica por qué el equipo puede trabajar en paralelo sin perder el hilo del producto.

**Siguiente paso:** validar el bootstrap técnico y comenzar el borde GitHub.

### 2026-08-29 · Bootstrap técnico reproducible

**Qué buscamos demostrar:** que una persona nueva puede levantar los tres runtimes y encontrar el estado del sistema sin credenciales reales.

**Resultado:** monorepo pnpm, backend FastAPI, paquete Convex, pantalla inicial del dashboard, configuración segura y fixture local.

**Criterio de evidencia:** comandos reproducibles, `/health`, typecheck/lint/build y tests mínimos pasando.

**Momento de demo previsto:** abrir el dashboard y mostrar que el producto distingue entre entorno preparado y conexiones externas todavía no configuradas.

### 2026-08-29 · Dashboard base visible

**Qué cambió:** el equipo ya puede abrir un dashboard real de Next.js con una primera lectura del pipeline y sin datos inventados.

**Decisión de producto:** la interfaz comunica qué está preparado y qué conexión sigue pendiente. El provider de Convex se activa solo cuando existe su URL pública.

**Evidencia:** build, lint y typecheck de Web pasan; la pantalla muestra GitHub, inteligencia, aprobación y LinkedIn como etapas del pipeline.

**Momento de demo:** se puede enseñar la promesa del producto antes de conectar proveedores y explicar que publicar queda protegido por aprobación humana.

**Siguiente paso:** cerrar el modelo Convex inicial y conectar el estado persistente al primer vertical slice.

### 2026-08-29 · Backend de salud y configuración segura

**Qué cambió:** FastAPI ya tiene un arranque mínimo, configuración por entorno, CORS explícito y un endpoint de salud.

**Decisión:** las credenciales de proveedores no son requisito para validar el runtime. Convex se expone mediante un gateway que se configura de forma perezosa cuando existe la variable CONVEX_URL.

**Evidencia:** Ruff, Pyright y pytest pasan; el test confirma que el endpoint de salud funciona sin secretos de GitHub, OpenAI, Kapso o LinkedIn.

**Momento de demo:** mostrar que el backend está vivo y preparado antes de conectar servicios externos.

**Siguiente paso:** usar el cliente Python de Convex en el procesamiento de eventos.

### 2026-08-29 · Primer contrato persistente en Convex

**Qué cambió:** el esquema inicial modela usuarios, instalaciones y repositorios de GitHub, eventos idempotentes, commits y actividad.

**Decisión:** deliveryId identifica una entrega de GitHub y repositoryId + sha identifica lógicamente un commit. Los índices dejan preparada la reanudación segura después de reinicios.

**Evidencia:** el schema pasa typecheck con Convex 1.45.0 y el fixture conserva la historia de tres commits relacionados sin depender de red.

**Momento de demo previsto:** un push podrá alimentar el pipeline sin crear duplicados y la actividad podrá reflejarse en el dashboard.

**Siguiente paso:** añadir queries/mutations Convex y el webhook GitHub de M1.

### 2026-08-29 · Dirección visual del dashboard

**Qué decidimos:** tratar el dashboard como una herramienta de evidencia, no como una landing genérica. La tesis ocupa el primer plano y el pipeline vertical muestra el orden real del producto.

**Firma visual:** una columna de etapas conectadas, con estado honesto cuando todavía no hay datos. La tipografía editorial de la tesis contrasta con etiquetas monoespaciadas de sistema.

**Evidencia:** la pantalla es responsive, tiene estados vacíos explícitos, foco visible en botones y no depende de datos simulados.

**Momento de demo:** el juez entiende en segundos qué observa Proof of Work y en qué punto el humano conserva el control.

**Siguiente paso:** conectar el estado real de Convex sin perder esta lectura clara del pipeline.

### 2026-08-29 · Primer borde seguro de GitHub

**Qué cambió:** FastAPI verifica la firma SHA-256 sobre el cuerpo raw, normaliza eventos push y pull_request y prepara la persistencia asíncrona hacia Convex.

**Decisión:** si falta la firma, el secreto o la URL de Convex, el endpoint no acepta el evento como procesado. La respuesta rápida no significa perder la trazabilidad: el evento se enviará a la mutation idempotente cuando esté desplegada.

**Evidencia:** cuatro pruebas puras y dos pruebas HTTP cubren firma, normalización, eventos no soportados y bloqueo seguro sin Convex; Ruff, Pyright y pytest pasan.

**Momento de demo previsto:** un push autenticado será reconocido por el sistema antes de que empiece el procesamiento lento.

**Siguiente paso:** generar las funciones Convex y conectar deliveryId con la deduplicación persistente.

### 2026-08-29 · El plan se vuelve delegable

**Qué cambió:** el plan M0 dejó de ser solo documentación local y se convirtió en un milestone de GitHub con seis issues trazables.

**Estado:** cuatro tareas están cerradas con evidencia en commits; M0-04 queda abierto para completar funciones Convex y M0-06 para integrar el smoke test.

**Momento de demo:** podemos mostrar no solo el producto, sino cómo el equipo convierte una idea compleja en trabajo coordinado y auditable.

**Siguiente paso:** resolver la configuración manual de Convex y conectar la primera mutación real.

### 2026-08-29 · Funciones Convex listas para codegen

**Qué cambió:** se añadieron mutations y queries para registrar eventos GitHub, commits y actividad, con deduplicación por deliveryId y repositoryId + sha.

**Decisión:** el repositorio no fabrica archivos _generated_. El CLI oficial debe crear esos bindings después del login y deployment de desarrollo; hasta entonces el schema tiene un check local separado.

**Bloqueo:** falta ejecutar pnpm dev:convex con una cuenta/proyecto Convex y copiar la URL al entorno local.

**Siguiente paso:** generar bindings oficiales, ejecutar typecheck:generated y cerrar M0-04.

### 2026-08-29 · Convex ready: primera persistencia real

**Qué cambió:** el CLI de Convex configuró el deployment de desarrollo, generó bindings oficiales y sincronizó schema, queries y mutations.

**Decisión:** la estructura del paquete usa `convex/convex/` como directorio de funciones reconocido por el CLI; los archivos `_generated` se versionan y los auxiliares locales del CLI quedan fuera del repositorio.

**Evidencia:** `typecheck:generated` pasa; `pnpm check` pasa; el smoke real insertó un evento fixture, repitió el mismo delivery ID y confirmó `duplicate=true` y `status=received`.

**Momento de demo:** por primera vez un evento entra al sistema, queda persistido y no se duplica ante un reintento.

### 2026-08-29 · Content Machine completa: de Git a LinkedIn vía WhatsApp

**Qué cambió:** Implementamos y verificamos la totalidad de los Milestones 1 a 12 del prompt maestro.
1. **GitHub Ingestion (M1 & M2):** Webhooks firmados con HMAC SHA-256, deduplicación por `deliveryId`, extracción de commits y normalización de diffs filtrando lockfiles y artefactos ruidosos.
2. **Commit Intelligence & Story Memory (M4 & M5-M6):** `CommitAnalyzer` estructurado con Pydantic y `StoryDetector` que agrupa múltiples commits relacionados en un arco narrativo explicable (ej. migración de Polling a WebSockets).
3. **LinkedIn Content Generation (M7 & M8):** `ContentGenerator` que produce borradores en formatos especializados (Problem→Solution, Before/After, Build Log) con claims sustentados en evidencia técnica real.
4. **WhatsApp Channel & Approval Agent (M9 & M10):** Integración con Kapso para envío de borradores y recepción de respuestas en lenguaje natural. `ApprovalAgent` clasifica intenciones con reglas de seguridad estrictas (`approve`, `revise`, `reject`, `clarify`, `hold`) y ejecuta el bucle de revisión V2/V3.
5. **Publicación en LinkedIn (M11):** `LinkedInPublisher` preparado para Posts API que solo publica borradores con aprobación explícita humana y almacena el URN externo.
6. **Dashboard Reactivo (M3):** Next.js suscrito en tiempo real a Convex para reflejar actividad (`activityEvents`), historias detectadas y estados de publicación sin recargas manuales.
7. **Demo End-to-End (M12):** Script `run_demo_pipeline.py` validado exitosamente contra el deployment de Convex Cloud.

**Evidencia:** `pnpm check` (17 tests en pytest, 0 errores en Pyright estricto, build de Next.js y typecheck de Convex) y ejecución completa del pipeline en `run_demo_pipeline.py`.

**Momento de demo:** Un desarrollador hace `git push` con 3 commits relacionados; el dashboard muestra la actividad en tiempo real, se detecta una sola historia, llega a WhatsApp, el usuario pide "hazlo más corto" recibiendo V2, luego responde "Ta bueno, publícalo noma", se publica en LinkedIn y recibe confirmación inmediata.

### 2026-08-29 · Laborin sale a internet

**Qué cambió:** desplegamos Web y Backend en `2.24.64.161` bajo `laborin.meowlab.tech`, usando Docker en la red interna existente y Caddy como terminación HTTPS y reverse proxy.

**Decisión:** el hostname público queda separado de las aplicaciones existentes del VPS. Caddy enruta `/health`, `/webhooks/github` y el callback reservado al Backend; el resto llega al dashboard Web.

**Evidencia:** el certificado TLS de Let’s Encrypt se obtuvo correctamente; Homepage responde `200`; `/health` responde `200` con `convex_configured=true`; el webhook responde `405 Allow: POST` ante GET, confirmando que alcanza FastAPI sin enviar un evento real.

**Momento de demo:** ya podemos abrir Proof of Work desde una URL pública y conectar la GitHub App con un endpoint estable.

**Pendiente explícito:** `https://laborin.meowlab.tech/auth/github/callback` está reservado en el proxy, pero devuelve `404` hasta implementar OAuth GitHub con validación de `state` e intercambio seguro del código.

**Siguiente paso:** implementar el callback OAuth GitHub y crear la App usando Homepage `https://laborin.meowlab.tech/` y Webhook `https://laborin.meowlab.tech/webhooks/github`.

## Hitos que debemos registrar


| Hito | Evidencia técnica | Momento narrativo |
|---|---|---|
| Foundation | Web, FastAPI y Convex arrancan localmente | El equipo puede colaborar sobre una base común |
| GitHub → Convex | Webhook firmado, evento idempotente y commit persistido | Un `git push` entra al producto de verdad |
| Live Activity | Eventos reactivos sin refresh manual | Se ve el pipeline mientras ocurre |
| Commit intelligence | `CommitAnalysis` estructurado y grounded | El sistema entiende qué cambió |
| Story memory/detection | Varios commits forman una Story explicable | No publica un post por commit |
| LinkedIn draft | Post versionado con claims soportados | La evidencia se convierte en contenido |
| WhatsApp approval | Aprobar, revisar, rechazar, aclarar y pausar | El humano mantiene el control en lenguaje natural |
| LinkedIn publishing | Solo publica la versión vigente aprobada | La historia llega a LinkedIn con trazabilidad |

## Formato para futuras entradas

Al cerrar cada milestone, añadir una sección con:

- fecha y nombre del hito;
- problema o riesgo que resolvimos;
- cambio técnico realizado;
- evidencia: tests, logs, captura o fixture;
- qué verá un juez o usuario;
- decisión pendiente o siguiente hito.

## Guion final provisional

1. Mostrar un repositorio conectado y un dashboard vacío pero listo.
2. Ejecutar un `git push` con tres commits relacionados.
3. Ver el pipeline avanzar en tiempo real.
4. Mostrar una sola historia: problema, intentos y solución.
5. Recibir el borrador en WhatsApp.
6. Pedir una revisión natural y recibir V2.
7. Aprobar V2 con una respuesta explícita.
8. Confirmar la publicación en LinkedIn y enseñar la trazabilidad de versiones.

La historia debe actualizarse junto con el código; no se redacta retrospectivamente al final.
