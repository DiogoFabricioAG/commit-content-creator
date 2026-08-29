# Proof of Work · Documentación del equipo

Esta carpeta convierte el prompt maestro en un plan de ejecución compartido. El objetivo no es duplicar la especificación del producto, sino dejar claro qué se construye primero, cómo se divide el trabajo y qué debe entregar cada persona o agente.

## Orden de lectura

1. [Milestone 0 — Foundation](./MILESTONE-0-FOUNDATION.md): primera piedra ejecutable y tareas delegables.
2. [Contratos de arquitectura](./ARCHITECTURE-CONTRACTS.md): límites entre Web, FastAPI, Convex y proveedores externos.
3. [Flujo de trabajo del equipo](./TEAM-WORKFLOW.md): ramas, handoffs, revisión y definición de terminado.
4. [Tablero de trabajo](./TASK-BOARD.md): estado actual y siguiente trabajo disponible.
5. [Historia del proyecto](./PROJECT-STORY.md): bitácora de decisiones, evidencia y guion de demo.

La especificación funcional completa sigue siendo [_MConverter.eu_Proof_of_Work_Prompt_Maestro_Codex.md](../_MConverter.eu_Proof_of_Work_Prompt_Maestro_Codex.md).

## Estado actual

**Fase:** preparación de Milestone 0.

**Realidad del proyecto al 29 de agosto de 2026:** existe el prompt maestro y esta primera documentación; todavía no hay código funcional, configuración de pnpm/uv, esquema Convex, tests ni repositorio Git inicializado.

**Consecuencia:** el primer encargo es bootstrap técnico. No se deben delegar todavía tareas de inteligencia, OAuth o publicación como si existieran contratos implementados.

## Cómo usar esta documentación

- Cada tarea tiene un identificador estable (`M0-xx`) para usarlo en ramas, commits, issues y handoffs.
- Una tarea se puede delegar cuando sus dependencias están en `Done` y su criterio de aceptación es verificable.
- Si una decisión cambia el alcance, el modelo de datos o un proveedor externo, se documenta antes de implementarla.
- Si una tarea descubre que falta una credencial o un paso manual de terceros, se marca `Blocked` con evidencia y una alternativa local segura.

## Regla de oro

La demo debe avanzar por rebanadas verticales. La primera rebanada objetivo es:

```text
GitHub push → FastAPI webhook → Convex → commit persistido → dashboard reactivo
```

Todo trabajo que no acerque a esa rebanada o a la siguiente parte del flujo debe esperar, salvo que sea necesario para desbloquearla.
