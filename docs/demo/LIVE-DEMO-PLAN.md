# Plan de demo en vivo · Historia completa y cierre final

Este runbook define las dos pruebas que deben quedar listas antes de la presentación. La primera demuestra que Laborin puede convertir el historial completo del proyecto en una sola historia basada en las preferencias del onboarding. La segunda demuestra el cierre: el último cambio real se envía con `git commit -m "final"` y se publica únicamente después de aprobación humana.

## Reglas de la demo

- El actor de la demo es el usuario por defecto actual, pero el flujo debe usar su identidad y preferencias persistidas, no valores hardcodeados.
- `DEMO_MODE=false` y las cuentas reales de GitHub, LinkedIn y Kapso deben estar conectadas.
- El historial completo se compila en un digest: no se debe enviar un WhatsApp por cada commit ni publicar una historia por cada cambio.
- La publicación nunca se ejecuta automáticamente. Siempre requiere `publícalo`, un botón equivalente o una aprobación explícita.
- Cada prueba debe conservar commits fuente, preferencias usadas, versiones del borrador, decisión de WhatsApp, URN de LinkedIn y confirmación de Kapso.
- Después del commit final no se hace ningún push adicional; cualquier cambio posterior ya pertenece a otra demo.

## Prueba 1 · Digest histórico desde la landing

### Objetivo

Desde la landing/onboarding, el usuario configura su estilo y solicita una compilación de todos los commits de `DiogoFabricioAG/commit-content-creator`. Laborin genera una sola publicación de LinkedIn con la voz y formatos elegidos por el usuario.

### Preparación

- Entrar con el usuario demo.
- Completar onboarding: nombre/voz, idioma, tono, audiencia, longitud, CTA, hashtags y formatos permitidos.
- Conectar GitHub y seleccionar el repositorio del proyecto.
- Conectar LinkedIn y confirmar el `authorUrn`.
- Confirmar que Kapso apunta al WhatsApp del usuario.
- Revisar el preview de preferencias antes de ejecutar el digest.

### Acción de la landing

La landing debe ofrecer una acción claramente nombrada, por ejemplo **Construir historia completa** o **Generar resumen del proyecto**. Debe mostrar advertencia de que crea un único borrador histórico y pedir confirmación antes de llamar a proveedores reales.

### Comportamiento esperado

1. Obtener el historial completo paginado del repositorio.
2. Filtrar merges, lockfiles, artefactos y commits puramente operativos según las reglas del producto, sin perder evidencia importante.
3. Analizar commits por lotes y agruparlos en una línea narrativa coherente.
4. Generar un único draft usando las preferencias persistidas del usuario.
5. Mostrar en la landing: rango de commits, número procesado, historias detectadas, fuentes principales, formato, idioma y preview.
6. Enviar a WhatsApp una tarjeta legible con resumen, evidencia y botones `Revisar`, `Publicar` y `Descartar`; el texto libre sigue disponible.
7. Si el usuario revisa, generar V2 y conservar el vínculo con la historia completa.
8. Si el usuario aprueba, publicar en LinkedIn y enviar confirmación por Kapso.

### Criterios de aceptación

- Una ejecución produce exactamente un digest, un post y una solicitud de aprobación.
- El contenido cambia al cambiar las preferencias del onboarding.
- El draft identifica que resume el proyecto completo y no inventa una funcionalidad de un solo commit.
- El dashboard muestra la misma ejecución que WhatsApp.
- La publicación termina con un URN real y el mensaje de confirmación solo se envía después del éxito.
- Repetir el mismo digest no duplica la ejecución si conserva la misma clave de idempotencia/configuración.

### Evidencia que se guarda

| Evidencia | Ejemplo |
|---|---|
| Repo y branch | `DiogoFabricioAG/commit-content-creator` / `main` |
| Rango | SHA inicial → SHA final previo al cierre |
| Cobertura | commits considerados, filtrados y agrupados |
| Preferencias | snapshot sin secretos |
| Draft | versión, formato, claims y fuentes |
| Aprobación | mensaje/botón y timestamp |
| Publicación | URN real y estado LinkedIn |
| Confirmación | message ID de Kapso y timestamp |

## Prueba 2 · Commit final y publicación final

### Objetivo

Cerrar la demo con una evidencia revisable y un último cambio identificable. El commit exacto `final` dispara la última compilación/publicación de la historia completa, usando las preferencias ya confirmadas.

### Preparación antes del cierre

- Revisar en la landing el digest de la Prueba 1.
- Confirmar que onboarding, conexiones, estilos, formatos, bot y publicación están en estado demo-ready.
- Generar `docs/demo/FINAL-REVIEW.md` o una vista equivalente con la evidencia consolidada.
- Verificar que no hay cambios sin revisar y que el working tree contiene solo el paquete final.
- Ejecutar `pnpm check` y conservar el resultado.

### Última acción técnica

Estas son las últimas operaciones del desarrollo de la demo:

```bash
git add .
git commit -m "final"
git push origin main
```

Después de ese push no se deben hacer commits correctivos en la misma corrida. Si aparece un bug, se registra como incidente y se repite la demo en una nueva corrida.

### Comportamiento esperado

1. GitHub entrega el push final firmado.
2. Laborin reconoce el título exacto `final` como cierre de demo.
3. El backend consulta el historial completo, incluye el commit final y produce un único draft final.
4. La landing muestra el paquete final para revisión.
5. WhatsApp recibe la versión final con botones y texto natural.
6. El usuario responde `publícalo` o pulsa `Publicar`.
7. LinkedIn publica con el token y `authorUrn` reales.
8. WhatsApp recibe la confirmación con el URN.
9. `FINAL-REVIEW.md` se completa con el resultado sin guardar tokens ni payloads sensibles.

### Criterios de aceptación

- El commit `final` es el último commit de la corrida.
- La publicación final incluye el historial completo, no solo el diff del commit final.
- Solo existe una publicación final y está asociada al commit/digest correcto.
- Un rechazo o una revisión impide publicar hasta una nueva aprobación.
- El dashboard, Convex, LinkedIn y WhatsApp muestran estados consistentes.
- La historia final se puede presentar en menos de cinco minutos siguiendo el runbook.

## TODO de implementación para la demo

### Prioridad 5 · Crítica

- [ ] **M20-01 · Historical digest API:** listar commits paginados, agruparlos y crear una ejecución idempotente de digest.
- [ ] **M20-02 · Preferencias en generación:** cargar el perfil del usuario y aplicarlo a idioma, voz, longitud, formato, links y media.
- [ ] **M21-01 · Trigger `final`:** detectar el commit final y lanzar el digest histórico sin enviar mensajes por cada commit.
- [ ] **M21-02 · Aprobación final segura:** bloquear publicación hasta aprobación de la versión final vigente.

### Prioridad 4 · Crítica de producto

- [ ] **M20-03 · Acción en landing:** onboarding, preview de preferencias y botón de digest con estado de ejecución.
- [ ] **M20-04 · Contrato de ejecución demo:** estados `queued`, `analyzing`, `awaiting_review`, `approved`, `published`, `failed`.
- [ ] **M21-03 · Confirmación final:** mensaje Kapso estructurado con estado, URN, link y resumen de fuentes.
- [ ] **M21-04 · E2E real:** prueba con GitHub, Kapso, LinkedIn y Convex usando cuentas reales.

### Prioridad 3 · Importante

- [ ] **M20-05 · Paquete de revisión:** vista y `FINAL-REVIEW.md` con cobertura, claims y decisiones.
- [ ] **M20-06 · Mensaje WhatsApp legible:** separar contexto, resumen, evidencia y acciones; soportar botones y fallback textual.
- [ ] **M21-05 · Guion cronometrado:** recorrido ensayado de cinco minutos con puntos de recuperación.

### Prioridad 2–1 · No tan crítica / polish

- [ ] **M20-07 · Animaciones y estados visuales** para la ejecución histórica.
- [ ] **M21-06 · Capturas y métricas** de la demo final.
- [ ] **M21-07 · Copy final** y limpieza de textos técnicos internos.

## Datos que no se deben usar en la demo

- Tokens OAuth, claves Fernet, secretos de webhooks o API keys.
- Payloads completos de proveedores que contengan datos personales.
- Un commit vacío como historia principal.
- Una publicación demo (`pow_demo_...`) presentada como publicación real.
