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

**Evidencia:** documentación versionada en `docs/` y repositorio remoto vacío listo para recibir el bootstrap.

**Momento de demo:** todavía no hay demo funcional; esta etapa explica por qué el equipo puede trabajar en paralelo sin perder el hilo del producto.

**Siguiente paso:** M0-01, bootstrap reproducible del workspace.

### 2026-08-29 · Bootstrap técnico iniciado

**Qué buscamos demostrar:** que una persona nueva puede levantar los tres runtimes y encontrar el estado del sistema sin credenciales reales.

**En construcción:** monorepo pnpm, backend FastAPI, paquete Convex, pantalla inicial del dashboard, configuración segura y fixture local.

**Criterio de evidencia:** comandos reproducibles, `/health`, typecheck/lint/build y tests mínimos pasando.

**Momento de demo previsto:** abrir el dashboard y mostrar que el producto distingue entre entorno preparado y conexiones externas todavía no configuradas.

### 2026-08-29 · Dashboard base visible

**Qué cambió:** el equipo ya puede abrir un dashboard real de Next.js con una primera lectura del pipeline y sin datos inventados.

**Decisión de producto:** la interfaz comunica qué está preparado y qué conexión sigue pendiente. El provider de Convex se activa solo cuando existe su URL pública.

**Evidencia:** build, lint y typecheck de Web pasan; la pantalla muestra GitHub, inteligencia, aprobación y LinkedIn como etapas del pipeline.

**Momento de demo:** se puede enseñar la promesa del producto antes de conectar proveedores y explicar que publicar queda protegido por aprobación humana.

**Siguiente paso:** cerrar el modelo Convex inicial y conectar el estado persistente al primer vertical slice.

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
