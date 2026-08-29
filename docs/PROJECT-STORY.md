# LaborIN · Historia del proyecto

Esta bitácora conserva la historia que luego se contará en la demo final. Cada entrada debe conectar una necesidad del producto con una decisión técnica, una evidencia comprobable y un momento visible para quien vea la presentación.

## Tesis para la demo

LaborIN convierte trabajo real de desarrollo en una historia publicable, sin obligar al desarrollador a detenerse para redactarla. La confianza del producto se demuestra en el recorrido completo:

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

**Momento de demo:** el juez entiende en segundos qué observa LaborIN y en qué punto el humano conserva el control.

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

### 2026-08-29 · LaborIN sale a internet

**Qué cambió:** desplegamos Web y Backend en `2.24.64.161` bajo `laborin.meowlab.tech`, usando Docker en la red interna existente y Caddy como terminación HTTPS y reverse proxy.

**Decisión:** el hostname público queda separado de las aplicaciones existentes del VPS. Caddy enruta `/health`, `/webhooks/github` y el callback reservado al Backend; el resto llega al dashboard Web.

**Evidencia:** el certificado TLS de Let’s Encrypt se obtuvo correctamente; Homepage responde `200`; `/health` responde `200` con `convex_configured=true`; el webhook responde `405 Allow: POST` ante GET, confirmando que alcanza FastAPI sin enviar un evento real.

**Momento de demo:** ya podemos abrir LaborIN desde una URL pública y conectar la GitHub App con un endpoint estable.

**Pendiente explícito:** `https://laborin.meowlab.tech/auth/github/callback` está reservado en el proxy, pero devuelve `404` hasta implementar OAuth GitHub con validación de `state` e intercambio seguro del código.

**Siguiente paso:** implementar el callback OAuth GitHub y crear la App usando Homepage `https://laborin.meowlab.tech/` y Webhook `https://laborin.meowlab.tech/webhooks/github`.

### 2026-08-29 · Production Readiness: el sistema ya tiene una URL pública

**Qué cambió:** el frente de despliegue quedó operativo con Web y Backend detrás de Caddy, healthcheck con espera de arranque y configuración de secretos fuera de Git. El proxy público también deja preparados los webhooks de GitHub/Kapso y las rutas de autenticación.

**Decisión:** separar “pipeline implementado” de “demo validada con proveedores reales”. Un health `200` prueba disponibilidad, pero no sustituye un evento GitHub firmado ni una aprobación humana por WhatsApp.

**Evidencia:** `pnpm check` pasa con 17 tests de backend, typecheck de Web/Convex/Python y build de Next.js; el VPS responde `healthy` y `https://laborin.meowlab.tech/health` responde `200`.

**Momento de demo:** ya se puede abrir LaborIN desde internet y conectar la GitHub App con un endpoint estable, sin interrumpir las aplicaciones existentes del VPS.

**Siguiente paso:** ejecutar M13-01 con un push real, conservar la entrega y comprobar que Convex muestra la actividad sin duplicarla.

### 2026-08-29 · Primer push real: GitHub ya alimenta LaborIN

**Qué cambió:** después de instalar la GitHub App, un push real al repositorio llegó al endpoint público firmado y recorrió el pipeline de ingestión hasta crear una historia y un borrador.

**Evidencia:** el VPS registró dos respuestas `POST /webhooks/github` con `202 Accepted`; Convex conservó una sola entrega (`2725ab5c-a3e2-11f1-8cd7-5c1db85fd27a`) para el commit `8813e7f`. También quedaron `commit=fetched`, `story=detected`, `post=awaiting_approval` y `approval_request=pending`.

**Decisión:** mantener `DEMO_MODE=true` mientras se verifica el borde GitHub. Así el primer push no envía mensajes reales ni publica en LinkedIn; la salida Kapso observada es `kapso_sim` y no debe presentarse como WhatsApp real.

**Momento de demo:** por primera vez podemos enseñar el recorrido real `git push → webhook → Convex → historia → borrador` con trazabilidad completa y sin duplicar entregas.

**Siguiente paso:** decidir explícitamente el cambio a `DEMO_MODE=false` para validar Kapso/WhatsApp con credenciales reales y luego probar aprobación y publicación.

### 2026-08-29 · Primer mensaje real: LaborIN cruza el borde de Kapso

**Qué cambió:** al pasar `DEMO_MODE=false`, el primer intento reveló en el tail que el cliente estaba llamando una ruta antigua de Kapso y recibía `404`. Corregimos el endpoint Meta de WhatsApp, la cabecera `X-API-Key` y el payload estándar de mensajes de texto.

**Evidencia:** el commit de prueba `618f6` llegó firmado a `POST /webhooks/github` y respondió `202`. Convex registró una nueva solicitud de aprobación con un identificador real `wamid...`; dejó de aparecer el prefijo `kapso_sim_`. El backend quedó `healthy` y `/health` respondió `200` en `laborin.meowlab.tech`.

**Decisión:** conservar la prueba de contrato de Kapso en `apps/backend/tests/test_kapso_client.py` para fijar URL, autenticación, versión de API y cuerpo enviado. La aceptación de la API confirma el envío al proveedor; la entrega al teléfono y la respuesta entrante todavía requieren validación manual.

**Momento de demo:** por primera vez el borrador cruza el límite del modo simulado y queda listo para llegar a WhatsApp, manteniendo la aprobación humana como siguiente barrera.

**Siguiente paso:** redeliver/probar un `POST` entrante de Kapso, responder "hazlo más corto" y verificar que la revisión V2 se guarda y se devuelve por WhatsApp.

### 2026-08-29 · Segunda piedra: de demo de un usuario a plataforma configurable

**Qué necesitamos ahora:** el pipeline ya cruza GitHub, Convex, Kapso y LinkedIn, pero todavía depende de un usuario por defecto, un estilo implícito y mensajes demasiado técnicos para una conversación cotidiana.

**Decisión:** abrir una nueva fase por frentes paralelos. Identidad, aislamiento y preferencias son el camino crítico; media, bot, landing y calidad pueden avanzar con contratos y fixtures sin bloquearse entre sí.

**Evidencia de planificación:** `docs/ROADMAP-NEXT-PHASE.md` define M14–M19 con prioridades 1–5, dependencias, responsables sugeridos y criterios de aceptación.

**Momento de demo previsto:** una persona crea su workspace, conecta GitHub/LinkedIn, define su voz, recibe un borrador claro por WhatsApp, lo revisa con lenguaje natural o botones y publica el formato elegido.

**Siguiente paso:** cerrar la decisión `users` vs `workspaces` y comenzar M14-01, M14-02 y M15-01 en paralelo.

### 2026-08-29 · La demo necesita dos actos

**Qué queremos demostrar:** primero, que el producto puede leer la historia completa del repositorio y convertirla en una sola publicación adaptada a la voz del usuario; después, que el último `git commit -m "final"` cierra la historia con una revisión y publicación final trazables.

**Decisión:** el digest histórico se ejecutará como una operación agregada, no como una repetición de cada commit. Así la demo no inunda WhatsApp ni genera publicaciones fragmentadas. El commit `final` queda reservado como última acción de la corrida y conserva la barrera de aprobación humana.

**Evidencia de planificación:** `docs/demo/LIVE-DEMO-PLAN.md` define preparación, acciones, criterios de aceptación, evidencia y TODO M20–M21.

**Momento de demo:** desde la landing se configuran preferencias, se ve el rango completo de commits, se revisa el borrador por WhatsApp, se publica en LinkedIn y se cierra con la confirmación del commit final.

**Siguiente paso:** implementar M20-01/M20-02 y la acción de digest en la landing antes de preparar el commit final.

### 2026-08-29 · La historia también necesita una vista de arquitectura

**Qué añadimos a la demo:** el digest podrá acompañar el texto con enlaces, imágenes, video y un diagrama de arquitectura generado a partir de la evidencia real del repositorio.

**Decisión:** arquitectura será un asset versionado junto al draft, no una ilustración decorativa separada. Cada nodo, relación y claim deberá conservar su fuente; el sistema generará también alt text y un fallback textual para canales que no puedan mostrar la imagen.

**Regla de confianza:** ningún secreto, URL interna, payload personal o componente no observado puede llegar al diagrama. Si el render no se puede validar, la aprobación debe mostrar el problema y no publicar silenciosamente una versión incompleta.

**Siguiente paso:** ejecutar M16-05 y coordinarlo con M20-08/M20-09 para que la Prueba 1 y el commit `final` revisen el paquete multimedia completo.

### 2026-08-29 · WhatsApp empieza por el usuario

**Cambio real:** GitHub ya no dispara un mensaje saliente de aprobación. El borrador queda en cola y el primer mensaje del usuario abre la conversación; recién entonces LaborIN entrega el texto y los botones de Kapso. La imagen queda bajo demanda.

**Decisión:** mantener el control humano y evitar mensajes proactivos fuera de la ventana de conversación. Los botones `Revisar`, `Publicar` y `Descartar` producen acciones deterministas; el lenguaje natural queda como fallback.

**Evidencia:** el backend, los contratos de Kapso, el parser de respuestas interactivas, Convex Storage y el upload de imágenes a LinkedIn pasan las pruebas automatizadas; el flujo de imagen está reservado para una orden explícita dentro de la ventana activa.

### 2026-08-29 · WhatsApp responde primero con texto

**Qué descubrimos:** el webhook entrante sí llegaba a FastAPI, pero la primera respuesta intentaba generar/subir una imagen y después enviaba un cuerpo demasiado grande como mensaje interactivo. Convex no tenía la función de media en el deployment usado por el VPS y Kapso devolvía `400`, dejando la conversación sin respuesta visible.

**Decisión:** la primera entrega solo envía el borrador como texto y un menú compacto. La generación de imagen se activa únicamente con un comando explícito del usuario; si Kapso rechaza los botones, el backend entrega instrucciones equivalentes en texto y conserva el flujo operativo.

**Evidencia:** `pnpm check` pasa con el caso explícito de generación de imagen; el tail de producción identificó el `POST /webhooks/kapso` aceptado y el error posterior de proveedor.

**Momento de demo:** el usuario recibe el borrador sin esperar una imagen y decide cuándo agregarla, evitando gasto y fallos silenciosos.

### 2026-08-29 · La historia obtiene una puerta de entrada pública

**Qué cambió:** la raíz de la web dejó de mezclar el mensaje público con el panel operativo. Ahora presenta la tesis del producto, el recorrido GitHub → historia → WhatsApp → LinkedIn, la aprobación humana y los límites de la demo; el panel reactivo se conserva en `/dashboard`.

**Decisión:** completar M18-01 con contratos mock sustentados en el recorrido real y mantener fuera del copy las funciones multimedia y multiusuario que todavía están en backlog. La landing no simula autenticación ni afirma que esas capacidades estén disponibles.

**Evidencia:** `lint`, TypeScript y el build de producción pasan; `/` y `/dashboard` prerenderizan correctamente. La revisión visual cubrió escritorio y un viewport móvil de 390 × 844 px, incluyendo una corrección al ancho mínimo del pipeline para eliminar recortes horizontales.

**Momento de demo:** en menos de 30 segundos se entiende qué observa el producto, cómo crea una historia sustentada y por qué nada llega a LinkedIn sin un sí explícito.

**Siguiente paso:** implementar M18-02 y M18-03 cuando estén disponibles los estados reales de onboarding, conexiones y confianza.
### 2026-08-29 · LaborIN adopta el lenguaje visual del evento

**Qué cambió:** la landing y el dashboard ahora comparten una dirección retro-terminal inspirada en The Next Craft: crema sobre negro verdoso, retícula técnica, scanlines, comandos BASIC, marcos CRT y componentes rectangulares. El contenido, las marcas y los assets siguen siendo propios de LaborIN.

**Decisión:** tomar el sistema visual como referencia, no copiar la página. La computadora, logotipos, tipografías propietarias y textos del evento no se reutilizan; el pipeline real de GitHub → Story AI → WhatsApp → LinkedIn ocupa el centro de la composición.

**Evidencia:** la landing y `/dashboard` se revisaron visualmente en escritorio y en un viewport móvil de 390 × 844 px sin desborde horizontal. Lint, TypeScript, build de producción y typecheck de Convex pasan.

**Momento de demo:** el proyecto se siente parte del universo del hackathon desde el primer vistazo, pero conserva una identidad funcional propia y comunica el recorrido del producto en segundos.

### 2026-08-29 · Tercera piedra: el historial se convierte en un digest

**Qué vimos:** el pipeline actual guardaba una historia y un post por commit. Eso demuestra ingestión, pero no sirve para el acto principal de la demo: contar todo el proyecto como una sola evolución.

**Qué construimos:** `HistoricalDigestBuilder` filtra cambios operativos cuando existe evidencia útil, conserva los commits descartados para auditoría y compone una sola `StoryDetectionResult` con un único `LinkedInDraftResult`. El generador recibe las preferencias editoriales sin acoplarse a la landing.

**Decisión:** el digest no elimina ni reescribe la historia granular ya almacenada. Produce una vista agregada e idempotente que después podrá persistirse como una ejecución propia y conectarse a la acción autenticada de la plataforma.

**Evidencia:** tres pruebas cubren agrupación de commits, filtrado de lockfiles y fallback cuando un repositorio contiene únicamente cambios operativos.

**Siguiente paso:** exponerlo mediante un servicio autenticado, persistir la ejecución en Convex y asociar una sola aprobación al digest.

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
