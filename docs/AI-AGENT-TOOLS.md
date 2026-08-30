# Agente natural y tools visuales

## Objetivo

Los mensajes libres de WhatsApp no se interpretan con detectores locales de palabras clave. Cuando el usuario escribe una instrucción, `ApprovalAgent` la envía a GPT junto con el borrador actual y el estado de la conversación.

Los botones de Kapso (`Publicar`, `Revisar` y `Descartar`) siguen siendo acciones deterministas porque representan una decisión explícita del usuario. Cualquier texto escrito por el usuario pasa por el agente.

## Tool disponible

El agente puede llamar a `request_visual_asset` cuando entiende que el usuario quiere crear, incluir o adjuntar un recurso visual. La tool usa un esquema estricto y devuelve:

- `kind`: `image`, `infographic`, `architecture_diagram` o `flow_diagram`.
- `instruction`: la solicitud completa del usuario, conservando su intención y detalles.
- `attach_to_draft`: indica si el recurso debe adjuntarse al borrador actual.

Ejemplos que deben funcionar sin una frase exacta:

> Quiero que esto se entienda de un vistazo; acompáñalo con una pieza que explique el problema, el cambio y el resultado.

> Convierte la solución en una lámina con los componentes, sus relaciones y un texto breve para cada uno.

> Haz una pieza visual con los aprendizajes de este cambio y adjúntala al post.

## Ejecución

1. `ApprovalAgent` clasifica el mensaje con GPT.
2. Si GPT llama `request_visual_asset`, el webhook ejecuta la acción en la misma ventana iniciada por el usuario.
3. `OpenAIImageGenerator.build_prompt()` transforma la instrucción estructurada junto con el contexto del story en un prompt visual.
4. El recurso se guarda en Convex y se reenvía el borrador a WhatsApp con el asset adjunto.
5. El usuario puede revisarlo o pulsar `Publicar`.

`build_prompt()` es el prompt de ejecución visual; no es un detector de intención. Si GPT no está disponible, el sistema no adivina una acción usando keywords: devuelve una aclaración segura (o conserva el feedback de revisión cuando la conversación está esperando cambios).

## Cambios futuros

- Añadir tools para video cuando exista un proveedor configurado.
- Persistir preferencias visuales del onboarding en el contexto del agente.
- Añadir una tool de regeneración que permita conservar una imagen y modificar solo una parte.
