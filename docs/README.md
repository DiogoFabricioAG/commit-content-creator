# Proof of Work · Documentación del equipo

Esta carpeta convierte el prompt maestro en un plan de ejecución compartido. El objetivo no es duplicar la especificación del producto, sino dejar claro qué se construye primero, cómo se divide el trabajo y qué debe entregar cada persona o agente.

## Orden de lectura

1. [Milestone 0 — Foundation](./MILESTONE-0-FOUNDATION.md): primera piedra ejecutable y tareas delegables.
2. [Contratos de arquitectura](./ARCHITECTURE-CONTRACTS.md): límites entre Web, FastAPI, Convex y proveedores externos.
3. [Flujo de trabajo del equipo](./TEAM-WORKFLOW.md): ramas, handoffs, revisión y definición de terminado.
4. [Tablero de trabajo](./TASK-BOARD.md): estado actual y siguiente trabajo disponible.
5. [Historia del proyecto](./PROJECT-STORY.md): bitácora de decisiones, evidencia y guion de demo.
6. [Roadmap siguiente fase](./ROADMAP-NEXT-PHASE.md): TODO multiusuario, onboarding, contenido rico, bot y landing.

La especificación funcional completa sigue siendo [_MConverter.eu_Proof_of_Work_Prompt_Maestro_Codex.md](../_MConverter.eu_Proof_of_Work_Prompt_Maestro_Codex.md).

## Estado actual

**Fase:** Milestones 0–13 en validación; M14–M19 cubren onboarding, multiusuario, contenido rico, bot humanizado y landing.

**Realidad del proyecto al 29 de agosto de 2026:** existe bootstrap reproducible, pipeline M1–M12 implementado, Convex conectado, Web y Backend desplegados en `laborin.meowlab.tech`, HTTPS activo, secretos de producción cargados fuera de Git y quality gate completo.

**Consecuencia:** el equipo puede trabajar sobre un vertical slice completo. Lo que sigue es evidencia de producción: una entrega real de GitHub, la conexión de Kapso, la validación de OAuth y el ensayo de la demo.

El tablero tiene un espejo remoto en el [milestone M0 - Foundation de GitHub](https://github.com/DiogoFabricioAG/commit-content-creator/milestone/1), con una issue por tarea delegable.

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
