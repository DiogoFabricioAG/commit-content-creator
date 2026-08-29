# Flujo de trabajo del equipo

## Principios

- Trabajar por tareas pequeñas y verificables, no por áreas indefinidas.
- Un responsable por tarea; otros pueden revisar o desbloquear.
- Cada handoff debe permitir continuar sin una conversación privada adicional.
- El código y la documentación se entregan juntos cuando una decisión afecta a otro módulo.
- Los proveedores externos se integran detrás de adaptadores testeables con fixtures.

## Antes de comenzar una tarea

1. Leer el milestone y los contratos enlazados.
2. Confirmar dependencias y buscar cambios concurrentes en los archivos objetivo.
3. Escribir el criterio de aceptación en la issue/tarea si falta.
4. Declarar el supuesto que se va a usar si hay una ambigüedad menor.
5. Detenerse solo ante credenciales/manuales externos o decisiones que cambien materialmente el alcance.

## Ramas y commits

Cuando Git esté inicializado:

```text
main
└── feat/M0-01-bootstrap-workspace
└── feat/M0-03-fastapi-skeleton
└── fix/M1-02-github-idempotency
└── docs/team-workflow
```

Convención: `<tipo>/<id>-<slug>`, donde `tipo` puede ser `feat`, `fix`, `docs`, `test` o `chore`.

Los commits deben ser pequeños y describir una sola intención:

```text
feat(backend): add health endpoint
docs(team): define milestone 0 handoffs
test(convex): cover delivery idempotency index
```

No reescribir ni borrar trabajo ajeno. Si dos tareas necesitan el mismo archivo, acordar el contrato y secuenciar el cambio.

## Pull request / revisión

Una PR debe incluir:

- ID de tarea y resumen de resultado;
- archivos o módulos modificados;
- checks ejecutados y su resultado;
- captura o salida relevante si cambia la UI o el arranque;
- variables de entorno nuevas, sin valores sensibles;
- decisiones, riesgos y trabajo fuera de alcance;
- actualización de documentación si cambió un contrato.

La revisión valida primero criterios de aceptación, aislamiento de datos, manejo de errores e idempotencia. La estética y refactorizaciones menores van después.

## Handoff entre agentes o personas

Usar siempre este formato:

```md
## Handoff [ID]

Estado: Done | Review | Blocked

Hecho:
-

Archivos relevantes:
-

Checks:
- `comando` → OK / FAIL

Decisiones tomadas:
-

Pendiente o riesgo:
-

Siguiente paso recomendado:
-
```

Un `Blocked` útil dice qué se intentó, qué respuesta se obtuvo, qué no se debe repetir y cuál es la alternativa local.

## Definition of Done por tarea

- El criterio de aceptación se puede comprobar.
- Tests o smoke checks cubren el camino nuevo cuando aplica.
- Lint/typecheck/build relevantes pasan.
- No hay secretos, tokens ni datos reales en el diff.
- Los errores tienen un mensaje accionable.
- La tarea no introduce una segunda fuente de verdad.
- La documentación de contratos queda actualizada si hubo cambios.
- El handoff está escrito.

## Reglas para credenciales y proveedores

- Usar `.env.local`/entorno seguro; nunca commitear secretos.
- Usar mocks/fixtures para desarrollo y tests.
- Verificar documentación oficial vigente para Convex, LinkedIn y Kapso justo antes de implementar.
- Anotar scopes, URLs, headers y versiones en la documentación de integración, no en mensajes efímeros.
- No probar publicación real ni mensajería real sin una cuenta/número de demo explícitamente preparado.

## Qué hacer ante cambios de alcance

Si una propuesta agrega otra red social, otro sistema de colas, autenticación de equipos o publicación automática, no se incorpora silenciosamente. Se registra como decisión pendiente y se compara contra los no-goals del MVP del prompt maestro.

## Arranque para una persona nueva

1. Leer [docs/README.md](./README.md).
2. Consultar [docs/TASK-BOARD.md](./TASK-BOARD.md) y escoger una tarea `Backlog` sin bloquear.
3. Leer los contratos antes de tocar interfaces.
4. Ejecutar los comandos de setup del README raíz cuando M0-01 los haya creado.
5. Dejar el handoff en la PR y actualizar el estado de la tarea.
