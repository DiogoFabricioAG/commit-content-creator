# Convex

Este paquete contiene el schema y las funciones persistentes de Proof of Work.

## Configuración del deployment

Desde la raíz del repositorio:

1. Ejecutar pnpm dev:convex.
2. Completar el login de Convex y crear o seleccionar el proyecto de desarrollo.
3. Dejar que el CLI genere convex/_generated.
4. Copiar la URL de deployment a CONVEX_URL y NEXT_PUBLIC_CONVEX_URL en el entorno local.
5. Ejecutar pnpm --filter @proof-of-work/convex typecheck:generated.

El typecheck normal valida el schema sin deployment. El typecheck:generated valida también las queries y mutations una vez que Convex haya producido sus bindings oficiales. Los archivos generados deben versionarse.
