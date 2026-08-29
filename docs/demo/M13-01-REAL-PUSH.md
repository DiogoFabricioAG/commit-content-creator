# M13-01 · Real push probe

Este archivo existe como evidencia deliberada de la primera entrega real de GitHub hacia Laborin.

La aceptación de M13-01 requiere comprobar que el push llega firmado a `https://laborin.meowlab.tech/webhooks/github`, recibe `202 Accepted` y se persiste una sola vez en Convex usando `X-GitHub-Delivery` como clave de idempotencia.

La GitHub App quedó instalada en el repositorio para ejecutar esta validación con una entrega real.
