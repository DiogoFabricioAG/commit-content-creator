# Roadmap siguiente fase · Onboarding, multiusuario y contenido rico

Este documento convierte las próximas mejoras de Laborin en tareas delegables y paralelizables. El objetivo es pasar de una demo funcional de un usuario a una plataforma configurable, multiusuario y lista para producir contenido de calidad por texto, enlaces, imágenes y videos.

## Escala de prioridad

| Prioridad | Significado | Regla |
|---|---|---|
| **5** | Crítica / bloqueante | Sin esto se rompe seguridad, aislamiento de usuarios o el recorrido principal |
| **4** | Crítica de producto | Necesaria para que la promesa principal funcione de forma confiable |
| **3** | Importante | Mejora la experiencia y debe entrar antes de la demo pública final |
| **2** | No tan crítica | Aporta calidad, pero no bloquea el flujo principal |
| **1** | Polish | Se puede dejar para después de validar el producto |

## Camino crítico recomendado

```text
identidad y tenancy (5)
        ↓
onboarding + preferencias (5)
        ↓
contenido configurable y aprobación segura (4)
        ↓
demo multiusuario con texto/media (3)
```

Los trabajos de landing, copy y diseño visual pueden avanzar en paralelo con contratos mock. El trabajo de media puede comenzar con fixtures antes de que termine el onboarding, pero no debe publicar contenido real hasta que exista aislamiento por usuario y aprobación explícita.

## Frentes de trabajo en paralelo

### Frente A · Identidad, seguridad y multiusuario

#### [ ] M14-01 · Modelo de tenancy y aislamiento — Prioridad 5 · Backend/Data

**Objetivo:** eliminar la dependencia del usuario por defecto y hacer que cada dato pertenezca a un usuario o workspace.

**Tareas:**

- Definir `users`, `workspaces` y `workspaceMembers` o documentar por qué el primer corte usa solo `users`.
- Asociar GitHub installations, repositorios, historias, posts, approvals y social accounts al propietario correcto.
- Sustituir `get_or_create_default_user()` por identidad proveniente de la sesión.
- Revisar cada query/mutation Convex para impedir lecturas cruzadas entre usuarios.
- Añadir índices por propietario y pruebas negativas de autorización.

**Aceptación:** dos usuarios de prueba ven datos distintos; un usuario sin sesión o de otro workspace recibe rechazo; no queda ningún flujo productivo que use el usuario fijo.

#### [ ] M14-02 · Sesión y OAuth de GitHub — Prioridad 5 · Backend/Auth

**Objetivo:** autenticar al usuario que instala o vincula GitHub y conservar una sesión segura.

**Tareas:**

- Implementar `state` firmado, con expiración y uso único.
- Completar intercambio de código y vincular instalación/repositorio al usuario autenticado.
- Definir cookie de sesión segura (`HttpOnly`, `Secure`, `SameSite`) o proveedor de sesión equivalente.
- Manejar revocación, expiración y errores de instalación.

**Aceptación:** login, callback, logout y sesión expirada funcionan; un callback con `state` incorrecto no vincula ninguna cuenta.

#### [ ] M14-03 · Vinculación OAuth de LinkedIn por usuario — Prioridad 5 · Backend/Auth

**Objetivo:** mantener el token LinkedIn cifrado y asociado al usuario correcto, no a una cuenta global.

**Tareas:**

- Guardar y recuperar `authorUrn`, scopes y expiración por usuario/workspace.
- Validar `state` de LinkedIn y evitar reutilización de callbacks.
- Añadir renovación/reautorización y estado visible de conexión.
- Mantener la clave Fernet únicamente fuera de Git y documentar rotación.

**Aceptación:** cada usuario publica con su propio `authorUrn`; revocar una cuenta no afecta a otra; tokens nunca aparecen en logs o respuestas web.

#### [ ] M14-04 · Matriz de permisos y auditoría — Prioridad 5 · Security/QA

**Objetivo:** hacer verificable el aislamiento multiusuario antes de abrir el onboarding.

**Aceptación:** existe una matriz de permisos para dashboard, repositorios, drafts, approvals, conexiones y publicación; cada regla tiene al menos una prueba positiva y una negativa; los cambios sensibles dejan actividad auditable.

### Frente B · Onboarding y configuración de estilo

#### [ ] M15-01 · Contrato de preferencias editoriales — Prioridad 5 · Product/Data

**Objetivo:** persistir cómo quiere comunicarse cada persona.

**Campos iniciales:** idioma, tono, persona/voz, audiencia, nivel técnico, longitud, palabras a evitar, CTA, hashtags, frecuencia y formatos permitidos.

**Aceptación:** hay defaults seguros, validación de valores, versionado de preferencias y un preview que usa exactamente esa configuración.

#### [ ] M15-02 · Wizard de onboarding — Prioridad 5 · Web/Product

**Objetivo:** llevar a una persona desde cero hasta su primera historia configurada.

**Pasos sugeridos:**

1. Crear perfil y workspace.
2. Conectar GitHub.
3. Seleccionar repositorios.
4. Conectar LinkedIn.
5. Conectar/confirmar WhatsApp.
6. Elegir voz y formatos.
7. Generar preview y terminar.

**Aceptación:** el flujo se puede pausar y retomar; muestra qué conexión falta; no expone secretos; al terminar existe un perfil listo para generar un borrador.

#### [ ] M15-03 · Pantalla de configuración editable — Prioridad 4 · Web

**Objetivo:** permitir cambiar estilo, formatos y conexiones después del onboarding.

**Aceptación:** guardar, cancelar y restaurar defaults funcionan; el preview cambia antes de guardar; el estado de GitHub, LinkedIn y WhatsApp es visible y accionable.

#### [ ] M15-04 · Selector de formatos por plataforma — Prioridad 4 · Product/Web

**Objetivo:** expresar qué puede producir y publicar cada usuario.

**Opciones iniciales:** texto, texto con enlace, imagen con texto, video con texto y solo borrador.

**Aceptación:** las preferencias llegan al backend y el generador; una opción no soportada por LinkedIn se bloquea con explicación clara, no falla al final del pipeline.

### Frente C · Contenido, texto y media

#### [ ] M16-01 · Contratos de contenido rico — Prioridad 4 · Backend/Data

**Objetivo:** dejar de tratar todos los posts como un string y modelar texto, links, imágenes y videos.

**Contrato mínimo:** `contentType`, `body`, `title`, `links`, `media[]`, `altText`, `thumbnail`, `duration`, `claims` y restricciones de plataforma.

**Aceptación:** Convex versiona el contenido sin romper los posts de texto actuales; cada tipo tiene validación y fixture.

#### [ ] M16-02 · Pipeline de assets — Prioridad 4 · Integrations/Backend

**Objetivo:** almacenar, validar y transportar imágenes/videos de forma segura.

**Tareas:**

- Elegir almacenamiento (Convex Storage u otro proveedor explícito).
- Validar MIME, tamaño, duración, dimensiones y extensión real.
- Crear estados `pending`, `ready`, `failed` y URLs con expiración cuando aplique.
- Limpiar assets huérfanos y evitar descargar URLs arbitrarias sin límites.

**Aceptación:** un fixture de imagen y uno de video recorren upload → validación → draft; un archivo inválido falla con mensaje útil y no llega a LinkedIn.

#### [ ] M16-03 · Publicación LinkedIn de imagen y video — Prioridad 4 · Integrations

**Objetivo:** completar el publisher más allá del texto.

**Tareas:**

- Implementar registro/upload del asset y creación del post.
- Manejar polling de procesamiento de video, timeout, retry e idempotencia.
- Mostrar errores de permisos/producto de LinkedIn de manera accionable.

**Aceptación:** texto, imagen y video tienen pruebas de contrato; solo la versión aprobada publica; el dashboard y WhatsApp reciben el resultado real o el fallo explicado.

#### [ ] M16-04 · Render de mensajes de WhatsApp — Prioridad 4 · Product/UX

**Objetivo:** que el borrador enviado se lea bien en móvil y no llegue como información rara.

**Tareas:**

- Separar encabezado, resumen, cuerpo, evidencia, opciones y estado.
- Reducir markdown incompatible y controlar longitud por mensaje.
- Mostrar preview por tipo de formato y links legibles.
- Añadir versión, nombre de historia y acción siguiente claramente visibles.

**Aceptación:** un usuario entiende qué se propone, qué evidencia lo sustenta y qué puede responder sin leer un bloque confuso.

### Frente D · Bot de WhatsApp natural y accionable

#### [ ] M17-01 · Botones/acciones de aprobación — Prioridad 4 · Integrations

**Objetivo:** ofrecer botones para aprobar, revisar, rechazar y pausar, manteniendo texto libre como fallback.

**Aceptación:** botones y respuestas textuales producen la misma intención; una acción desconocida nunca publica; se conserva el contexto de la versión aprobada.

#### [ ] M17-02 · Router conversacional con GPT — Prioridad 4 · AI/Backend

**Objetivo:** entender lenguaje natural sin delegar decisiones críticas al modelo.

**Tareas:**

- Usar salida estructurada para `approve`, `revise`, `reject`, `hold`, `clarify`.
- Enviar solo contexto mínimo y redactado al modelo.
- Definir timeout, reintento, límite de coste y fallback determinista.
- Mantener aprobación explícita como regla de negocio fuera de GPT.
- Registrar intención, confianza, modelo y latencia sin guardar secretos.

**Aceptación:** frases como “dale”, “publícalo nomás”, “hazlo más corto” y “déjalo pendiente” se entienden; una frase ambigua pide aclaración; GPT nunca salta la autorización humana.

#### [ ] M17-03 · Memoria conversacional acotada — Prioridad 3 · AI/Backend

**Objetivo:** que el bot conozca la historia y versión activa sin mezclar conversaciones o usuarios.

**Aceptación:** una revisión V2 mantiene el contexto correcto; mensajes de otra persona no pueden modificar la aprobación; existe límite de historial y política de retención.

#### [ ] M17-04 · Pruebas de conversación — Prioridad 3 · QA

**Aceptación:** matriz con respuestas afirmativas, negativas, ambiguas, correcciones, emojis, mayúsculas, faltas ortográficas, mensajes repetidos y eventos duplicados; todos tienen resultado esperado.

### Frente E · Landing y experiencia pública

#### [ ] M18-01 · Nueva landing orientada a conversión — Prioridad 3 · Frontend/Design

**Secciones:** tesis en una frase, cómo funciona en cuatro pasos, evidencia de seguridad, ejemplo WhatsApp → LinkedIn, integraciones, CTA de onboarding y estado de demo.

**Aceptación:** la landing explica el valor en menos de 30 segundos, funciona en móvil, tiene CTA real y no promete funciones no disponibles.

#### [ ] M18-02 · Sistema visual y responsive polish — Prioridad 2 · Frontend/Design

**Aceptación:** estados de carga/error/vacío, foco de teclado, contraste, navegación móvil y componentes reutilizables pasan revisión visual y accesible.

#### [ ] M18-03 · Página pública de confianza — Prioridad 2 · Product/Frontend

**Objetivo:** mostrar privacidad, aprobación humana, integraciones conectadas y límites del producto de forma comprensible.

### Frente F · Operación, calidad y demo

#### [ ] M19-01 · Observabilidad del pipeline — Prioridad 4 · Platform/Backend

**Aceptación:** cada ejecución tiene correlation ID; se puede seguir `incoming → draft → approval → publish → confirmation`; errores de proveedor aparecen sin tokens ni cuerpos sensibles.

#### [ ] M19-02 · E2E multiusuario con proveedores reales — Prioridad 4 · QA/Integrations

**Aceptación:** dos usuarios completan onboarding, cada uno recibe su borrador, uno revisa y otro publica; la publicación y confirmación se atribuyen correctamente.

#### [ ] M19-03 · Fixtures y sandbox para media/GPT — Prioridad 3 · QA/DX

**Aceptación:** el equipo puede probar formatos, botones y respuestas del bot sin enviar contenido real ni gastar API innecesariamente.

#### [ ] M19-04 · Guion de demo final — Prioridad 3 · Demo/QA

**Recorrido:** registro → GitHub → preferencias → historia real → preview → revisión por WhatsApp → aprobación → LinkedIn → confirmación → dashboard.

**Aceptación:** guion reproducible, evidencia versionada y datos de prueba limpiables.

## Distribución inmediata para agentes/equipo

| Persona/agente | Puede empezar ya | Depende de |
|---|---|---|
| Backend/Data | M14-01, M14-04, M15-01, M16-01 | Decisión de tenancy |
| Backend/Auth | M14-02, M14-03 | Contrato de sesión y URLs OAuth |
| Frontend/Product | M15-02 en mock, M15-03, M18-01 | Contrato M15-01 para integrar |
| AI/Backend | M17-02 en sandbox, M17-03 | Contrato de mensajes y preferencias |
| Integrations | M16-02 spike, M16-03 contrato LinkedIn | Permisos y almacenamiento |
| QA/DX | M17-04, M19-03, matriz de permisos | Contratos iniciales |

## Orden de ejecución sugerido

1. Cerrar la decisión de `users` vs `workspaces` y publicar el contrato.
2. Implementar aislamiento y sesiones antes de ampliar el acceso.
3. Diseñar onboarding y landing con datos mock mientras Backend termina OAuth.
4. Integrar preferencias al generador y normalizar el formato de WhatsApp.
5. Añadir botones y GPT con fallback determinista.
6. Completar media y permisos de LinkedIn.
7. Ejecutar E2E multiusuario y actualizar la historia de la demo.

## Definition of Done para cada tarea

- Código y tests incluidos en el mismo cambio.
- Criterios de aceptación verificables y evidencia en la descripción del handoff.
- Sin secretos, tokens ni payloads sensibles en Git o logs.
- `pnpm check` pasa o la excepción queda documentada.
- Cambios desplegados solo si la tarea está lista para producción.
- La historia del proyecto se actualiza cuando el cambio modifica el recorrido visible.
