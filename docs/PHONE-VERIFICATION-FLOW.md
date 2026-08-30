# Verificación de teléfono por WhatsApp

## Objetivo

`laborin_session` solo se emite después de demostrar que la persona controla el número de WhatsApp declarado. Escribir un teléfono en el formulario ya no inicia una sesión autenticada.

## Flujo de onboarding

1. La persona abre el chat de LaborIN y envía el primer mensaje.
2. El webhook de Kapso registra/actualiza la sesión de WhatsApp y abre la ventana gratuita de 24 horas.
3. En la landing, la persona ingresa su número y solicita el código.
4. El backend verifica que la ventana de 24 horas siga abierta, genera un código numérico de seis dígitos y lo envía por Kapso.
5. El código queda asociado a un challenge firmado, almacenado en una cookie `HttpOnly` con una vigencia de 10 minutos. El código nunca se guarda en texto plano.
6. La persona escribe el código en la landing. Solo entonces se crea la cookie `laborin_session` firmada por 7 días.

```text
WhatsApp inbound
      ↓
Ventana 24h abierta
      ↓
Landing solicita OTP ──┐
                       ├─ Kapso envía código
Landing verifica OTP ──┘
      ↓
laborin_session
```

## Endpoints

- `POST /auth/session/login`: crea o recupera el usuario y solicita un código. Devuelve `409` si todavía no existe una ventana WhatsApp abierta y `202` cuando el código fue enviado.
- `POST /auth/session/verify`: valida el código y emite la sesión autenticada.
- `GET /auth/session/me`: resuelve la sesión actual.
- `POST /auth/session/logout`: revoca la cookie de sesión en el navegador.

## Decisiones de seguridad

- La prueba de posesión se hace por el canal WhatsApp controlado por el usuario; no se confía en el texto del formulario.
- El envío se realiza únicamente dentro de la ventana iniciada por el mensaje entrante, por lo que el flujo de onboarding no depende de mensajes plantilla de pago.
- El challenge, el estado OAuth y la sesión usan firmas HMAC con `SESSION_SECRET` (o `TOKEN_ENCRYPTION_KEY` como compatibilidad).
- El GPT no interpreta el OTP: el código se compara exactamente como credencial de autenticación.
- En producción se debe configurar `SESSION_SECRET` con un valor fuerte y estable; no se debe depender del fallback local.

## Prueba manual de demo

1. Entra a `https://laborin.meowlab.tech/login`.
2. Pulsa **Hablar al +1 (208) 441-5504** y envía un mensaje.
3. Regresa a la landing y pulsa **Enviar código por WhatsApp**.
4. Copia el código recibido, pulsa **Verificar WhatsApp y Entrar** y conecta GitHub/LinkedIn.

Si el código no llega, revisar que `DEMO_MODE=false`, que Kapso tenga credenciales válidas y que el webhook haya recibido el primer mensaje entrante.
