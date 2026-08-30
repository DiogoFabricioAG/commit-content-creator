# Multi-Tenant Isolation & Authorization Contract

Este documento describe las garantías arquitectónicas, el modelo de datos y los contratos de autorización implementados en Convex y FastAPI para asegurar el aislamiento total entre usuarios (multi-inquilino) en LaborIN.

---

## 1. Principios de Aislamiento

1. **Aislamiento por `userId`:**
   - Cada entidad de usuario (`repositories`, `posts`, `stories`, `socialAccounts`, `userPreferences`, `activityEvents`, `approvalRequests`, `whatsappSessions`) almacena una referencia tipada `userId: v.id("users")`.
   - Las consultas (queries) del cliente filtran obligatoriamente por el índice `by_user` o `by_user_*` para evitar fugas de datos entre inquilinos.

2. **Validación de Identidad en Mutaciones:**
   - Ninguna mutación permite crear o registrar recursos asociados a un `userId` arbitrario o inexistente sin validación previa (`ctx.db.get(args.userId)`).

3. **Asociación de Repositorios Multi-Usuario:**
   - Los repositorios se indexan por `by_user_full_name: ["userId", "fullName"]`.
   - Dos usuarios distintos pueden vincular el mismo repositorio u organización de GitHub (`growthrockstar/repo`); cada usuario mantiene su propio registro independiente, configuración editorial y aprobaciones.

---

## 2. Contrato de Funciones en Convex

| Módulo Convex | Función | Tipo | Regla de Autorización / Aislamiento |
| :--- | :--- | :--- | :--- |
| `repositories` | `getOrCreateForUser` | Mutation | Valida existencia de `userId`. Utiliza el índice `by_user_full_name` para no sobreescribir ni compartir repositorios entre usuarios. |
| `repositories` | `listForUser` | Query | Devuelve únicamente repositorios activos cuyo `userId` coincide con el del cliente. |
| `repositories` | `getByIdForUser` | Query | Verifica que el repositorio pertenezca al `userId` solicitante; devuelve `null` si pertenece a otro usuario. |
| `repositories` | `removeForUser` | Mutation | Valida propiedad (`repo.userId === args.userId`) antes de deshabilitar la asociación. |
| `posts` | `listForUser` | Query | Devuelve borradores filtrados exclusivamente por `userId`. |
| `posts` | `getByIdForUser` | Query | Previene lectura horizontal de borradores de otros inquilinos. |
| `stories` | `listForUser` | Query | Devuelve historias detectadas indexadas por `userId`. |
| `preferences` | `getForUser` / `save` | Query / Mutation | Consulta y persiste la voz editorial y reglas anti-hype asociadas exclusivamente a la cuenta del usuario. |
| `socialAccounts` | `getByUserAndProvider` | Query | Recupera los tokens cifrados de LinkedIn únicamente para el `userId` autorizado. |
| `approvalRequests` | `listForUser` | Query | Lista solicitudes de aprobación de WhatsApp del usuario activo. |

---

## 3. Webhooks & Automatización Backend

1. **Resolución de Repositorio en GitHub Push (`GitHubEventProcessor`):**
   - Al recibir un evento push de `usuario/repo`, el procesador consulta `repositories:getByFullName`.
   - Resuelve el `userId` real del propietario registrado en Convex y su número de WhatsApp correspondiente (`user_phone`).
   - Aplica las preferencias de voz personalizadas del autor para redactar el borrador y encola la aprobación a su teléfono.

2. **Propagación de Sesión en OAuth (GitHub / LinkedIn):**
   - Las rutas OAuth requieren la cookie de sesión firmada `laborin_session`; ya no aceptan `userId` desde la URL.
   - El backend genera un `state` firmado con usuario, proveedor, nonce y expiración. El nonce se conserva en una cookie `HttpOnly` de un solo uso.
   - El callback valida la sesión, firma, proveedor, expiración y nonce antes de asociar los tokens al `userId` correcto y redirigir al Dashboard.

---

## 4. Pruebas de Seguridad y Aislamiento Negativo

Las pruebas unitarias y de integración en [`apps/backend/tests/test_cross_tenant_isolation.py`](file:///D:/Proyectos2026/commit-content-creator/apps/backend/tests/test_cross_tenant_isolation.py) verifican:
- Rechazo a la lectura de repositorios cruzados entre usuarios distintos.
- Rechazo a la modificación o eliminación de repositorios por parte de terceros no autorizados.
- Rechazo a la lectura de posts o borradores privados de otros inquilinos.
- Rechazo a la creación de registros con `userId`s falsos o manipulados.
