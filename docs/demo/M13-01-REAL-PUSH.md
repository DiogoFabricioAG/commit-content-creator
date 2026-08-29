# M13-01 · Real push probe

Este archivo existe como evidencia deliberada de la primera entrega real de GitHub hacia Laborin.

La aceptación de M13-01 requiere comprobar que el push llega firmado a `https://laborin.meowlab.tech/webhooks/github`, recibe `202 Accepted` y se persiste una sola vez en Convex usando `X-GitHub-Delivery` como clave de idempotencia.

La GitHub App quedó instalada en el repositorio para ejecutar esta validación con una entrega real.

## Resultado · 2026-08-29

- Commit disparador: `8813e7f8829d9cb5f2da5e94bedfb9293bc30e0a`.
- Backend: dos `POST /webhooks/github` con `202 Accepted` observados en el VPS.
- Convex: una sola fila para el delivery `2725ab5c-a3e2-11f1-8cd7-5c1db85fd27a`, con `eventType=push` y `status=received`.
- Pipeline: commit `fetched`, historia `detected`, post `awaiting_approval` y solicitud WhatsApp `pending`.

M13-01 queda aceptado. La siguiente validación se ejecutó con `DEMO_MODE=false` y abrió la prueba real de Kapso.

## Resultado · 2026-08-29 · Kapso real

- Corrección desplegada: endpoint Meta WhatsApp `v24.0`, autenticación `X-API-Key` y payload compatible con WhatsApp Cloud API.
- Commit disparador: `618f6` (`test(live): verify Kapso delivery after endpoint fix`).
- Backend: `POST /webhooks/github` respondió `202 Accepted`; el contenedor quedó `healthy`.
- Convex: la aprobación más reciente quedó `pending` con `kapsoOutboundMessageId` `wamid...`, evidencia de aceptación por el proveedor y no de simulación.
- Protección: el contrato está cubierto por `apps/backend/tests/test_kapso_client.py`; `pnpm check` pasó con 18 pruebas backend.

M13-03 queda parcialmente validado para salida: falta comprobar la recepción de un mensaje entrante de Kapso y el ciclo de revisión/aprobación humana.
