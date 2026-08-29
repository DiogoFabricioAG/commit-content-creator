# Contratos de arquitectura

Este documento fija los límites mínimos para que varias personas o agentes puedan trabajar en paralelo. Si la implementación descubre que un contrato no alcanza, se actualiza primero este documento y luego el código que dependa de él.

## Fuente de verdad

Convex es la fuente de verdad de estado, persistencia e información reactiva. FastAPI coordina webhooks, integraciones externas y workers de inteligencia. Next.js presenta estado y configuración; no decide si se publica un post.

```text
Proveedor externo
      ↓ webhook/API
FastAPI: validar → normalizar → encolar/procesar
      ↓ Convex Python Client
Convex: estado persistente + consultas reactivas
      ↓ suscripción React
Next.js: visibilidad, configuración y fallback manual
```

## Límites por capa

| Capa | Puede hacer | No debe hacer |
|---|---|---|
| `apps/web` | Mostrar actividad, configurar conexiones, consultar Convex | Guardar secretos, publicar en LinkedIn, procesar webhooks, llamar directamente a Kapso/OpenAI |
| `apps/backend` | Validar payloads, verificar firmas, llamar APIs, ejecutar inteligencia, mutar Convex | Confiar en payloads sin validar, mantener estado crítico solo en memoria, publicar sin aprobación explícita |
| `convex/` | Persistir dominio, imponer filtros por usuario, exponer queries/mutations/actions pequeñas | Guardar secretos en texto plano, acoplarse a HTTP externo, convertirse en un blob JSON sin índices |
| Proveedores | Entregar eventos o ejecutar una acción autorizada | Ser la fuente de verdad del estado de LaborIN |

## Primera rebanada vertical

### Flujo nominal

```text
GitHub push
  → FastAPI verifica X-Hub-Signature-256
  → FastAPI usa X-GitHub-Delivery como idempotency key
  → Convex guarda githubEvent(status = received)
  → procesamiento obtiene commit y lo normaliza
  → Convex guarda commit(status = fetched)
  → activityEvents alimenta el dashboard
```

El endpoint de webhook debe responder rápido. Las llamadas a GitHub, Convex o LLM que puedan tardar no deben bloquear el camino de recepción más de lo necesario.

### Contrato conceptual de `githubEvents`

```ts
{
  deliveryId: string,       // único por entrega de GitHub
  eventType: "push" | "pull_request",
  repositoryId?: Id<"repositories">,
  status: "received" | "processing" | "processed" | "failed",
  receivedAt: number,
  processedAt?: number,
  error?: string,
  metadata: {                // normalizada; sin payload completo ilimitado
    repositoryFullName?: string,
    branch?: string,
    commitShas?: string[],
    action?: string,
  },
}
```

El payload original no se usa como modelo de dominio. Si hace falta conservar una parte para auditoría, debe tener tamaño acotado y excluir secretos.

### Contrato conceptual de `commits`

```ts
{
  repositoryId: Id<"repositories">,
  sha: string,
  author: string,
  message: string,
  committedAt: number,
  branch?: string,
  additions: number,
  deletions: number,
  changedFiles: number,
  files: Array<{
    path: string,
    status: string,
    additions: number,
    deletions: number,
    patch?: string,
  }>,
  status: "fetched" | "analyzing" | "analyzed" | "ignored" | "failed",
  createdAt: number,
}
```

La clave lógica de deduplicación de un commit es `repositoryId + sha`. Los parches deben normalizarse y limitarse; lockfiles, artefactos generados, vendor y cambios de formato pueden marcarse como ignorados/depriorizados.

## Convenciones de estado

- Los estados representan hechos observables, no intenciones futuras.
- Una transición debe ser idempotente: repetirla no crea un segundo evento, commit o publicación.
- Los errores persistidos son concisos y aptos para diagnóstico; nunca incluyen tokens completos, secretos o payloads sensibles.
- El estado visible del dashboard sale de Convex, no de un cache local del frontend.

## Identidad y aislamiento

- Toda consulta/mutación de dominio recibe o deriva un `userId` confiable.
- Un `repositoryId` solo puede usarse si pertenece al usuario de la operación.
- La futura aprobación de WhatsApp debe comprobar tanto el teléfono E.164 como la solicitud pendiente.
- Un mensaje sin solicitud de aprobación coincidente nunca puede llegar al publisher.

## Reglas de integración externa

- Firmas: verificar sobre el cuerpo raw antes de parsear JSON y usar comparación en tiempo constante.
- Idempotencia: persistir las claves de entrega (`X-GitHub-Delivery` / equivalente Kapso) en Convex.
- Secretos: solo backend/entorno seguro; nunca Next.js client, localStorage ni logs.
- SDK/API: comprobar la documentación oficial vigente antes de fijar endpoints, scopes, headers o versiones.
- Proveedores: envolver cada integración detrás de un módulo propio para que fixtures y tests no requieran red.

## Contrato de delegación entre módulos

Cada PR que cambie un contrato debe incluir:

- qué campo, estado o endpoint cambia;
- qué consumidores deben actualizarse;
- cómo se mantiene compatibilidad con fixtures;
- qué test demuestra el cambio;
- si requiere credencial, configuración manual o documentación externa vigente.

## Decisiones no negociables heredadas del prompt maestro

- Un commit es evidencia; no equivale automáticamente a un post.
- Nunca publicar ante aprobación ambigua.
- Cada revisión produce un `postVersion` nuevo.
- Solo la versión vigente y explícitamente aprobada puede publicarse.
- LinkedIn es el único destino del MVP.
