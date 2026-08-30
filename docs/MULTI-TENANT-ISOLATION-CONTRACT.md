# Multi-Tenant Isolation & Authorization Contract

Este documento describe las garantías arquitectónicas, el modelo de datos, la capa de autenticación con cookies firmadas (`laborin_session`) y los contratos de autorización implementados en Convex y FastAPI para asegurar el aislamiento total entre usuarios (multi-inquilino) en LaborIN.

---

## 1. Principios de Aislamiento y Autenticación Criptográfica

1. **Aislamiento por `userId` & Sesión `laborin_session`:**
   - La identidad del usuario activo se administra mediante una cookie de sesión firmada criptográficamente con HMAC-SHA256 (`laborin_session`, `HttpOnly`, `SameSite=Lax`).
   - Las operaciones sensibles de mutación (crear/eliminar repositorios, actualizar perfil, guardar preferencias editoriales) se canalizan obligatoriamente a través del backend FastAPI (`/api/portal/*`), donde el `userId` se deriva **exclusivamente de la sesión verificada**, imposibilitando que un cliente manipule o inyecte el ID de otra cuenta.

2. **Validación de Identidad en Convex:**
   - Ninguna mutación permite crear o registrar recursos asociados a un `userId` arbitrario o inexistente sin validación previa (`ctx.db.get(args.userId)`).

3. **Asociación de Repositorios Multi-Usuario:**
   - Los repositorios se indexan por `by_user_full_name: ["userId", "fullName"]`.
   - Dos usuarios distintos pueden vincular el mismo repositorio u organización de GitHub (`growthrockstar/repo`); cada usuario mantiene su propio registro independiente, configuración editorial y aprobaciones sin colisión de permisos.

---

## 2. API Gateway Autenticada del Backend (`/api/portal/*`)

Todas las rutas del portal validan la sesión antes de delegar a Convex:

| Endpoint | Método | Descripción | Regla de Autorización |
| :--- | :--- | :--- | :--- |
| `/api/portal/profile` | `GET` | Obtiene el perfil del usuario autenticado | Requiere `laborin_session`. Devuelve 401 si no hay sesión o si fue alterada. |
| `/api/portal/profile` | `PATCH` | Actualiza nombre o teléfono WhatsApp | Actualiza únicamente la cuenta del `userId` extraído de la sesión. |
| `/api/portal/preferences` | `GET` | Obtiene voz editorial y preferencias | Devuelve la configuración del usuario de la sesión. |
| `/api/portal/preferences` | `PUT` | Persiste voz editorial y reglas anti-hype | Guarda las preferencias asociadas al `userId` de la sesión. |
| `/api/portal/repositories` | `GET` | Lista repositorios vinculados | Filtra por el `userId` de la sesión. |
| `/api/portal/repositories` | `POST` | Vincula un repositorio (`owner/repo`) | Crea la asociación scoped al `userId` de la sesión. |
| `/api/portal/repositories/{id}` | `DELETE` | Deshabilita la asociación del repositorio | Valida que el repositorio pertenezca al `userId` de la sesión; devuelve 403 si pertenece a otro inquilino. |
| `/api/portal/social-accounts` | `GET` | Obtiene estado de conexión de LinkedIn | Devuelve metadatos seguros (sin exponer tokens cifrados de acceso). |
| `/api/portal/activity` | `GET` | Historial de eventos en vivo | Filtrado por el `userId` de la sesión. |

---

## 3. Webhooks & Automatización Backend

1. **Resolución Segura de Repositorio en GitHub Push (`GitHubEventProcessor`):**
   - Al recibir un evento push de `usuario/repo`, el procesador consulta `repositories:getByFullName`.
   - Si el repositorio está registrado y activo, resuelve el `userId` legítimo y su número de WhatsApp correspondiente (`user_phone`).
   - Aplica las preferencias de voz personalizadas del autor para redactar el borrador y encola la aprobación a su teléfono.
   - **Salvaguarda de Producción:** Si el repositorio no está registrado por ningún inquilino en Convex, el evento se omite (`status: skipped`) sin crear cuentas fantasmas ni filtrar datos de otros usuarios.

2. **Propagación de Sesión en OAuth (GitHub / LinkedIn):**
   - Las rutas OAuth requieren la cookie de sesión firmada `laborin_session`.
   - El backend genera un `state` firmado con usuario, proveedor, nonce y expiración. El nonce se conserva en una cookie `HttpOnly` de un solo uso.
   - El callback valida la sesión, firma, proveedor, expiración y nonce antes de asociar los tokens al `userId` correcto y redirigir al Dashboard.

---

## 4. Pruebas de Seguridad y Aislamiento Negativo

Las suites de pruebas automatizadas ejecutan verificaciones tanto unitarias como en rutas reales HTTP:

1. **Pruebas en Rutas Reales con `TestClient` ([`apps/backend/tests/test_portal_session_auth.py`](file:///D:/Proyectos2026/commit-content-creator/apps/backend/tests/test_portal_session_auth.py)):**
   - `test_portal_routes_reject_unauthenticated_requests`: Rechaza con `401 Unauthorized` cualquier petición sin cookie de sesión a `/api/portal/*`.
   - `test_portal_routes_reject_forged_or_tampered_cookie`: Rechaza con `401 Unauthorized` cookies con firmas inválidas o alteradas.
   - `test_cross_tenant_repository_deletion_rejected_on_live_route`: Inquilino B autenticado intenta eliminar un repositorio del Inquilino A -> Recibe `403 Forbidden` (`Unauthorized: You do not own this repository`).
   - `test_authenticated_user_only_receives_own_repositories`: Inquilino A solo recibe sus propios repositorios y nunca los proyectos privados de otros usuarios.

2. **Pruebas de Funciones Convex ([`apps/backend/tests/test_cross_tenant_isolation.py`](file:///D:/Proyectos2026/commit-content-creator/apps/backend/tests/test_cross_tenant_isolation.py)):**
   - Rechazo a la lectura cruzada de repositorios y posts.
   - Rechazo a mutaciones con `userId`s inexistentes.
