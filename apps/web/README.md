# Laborin · Web & Landing Page Guide

Guía completa de la aplicación web de **Laborin**: arquitectura actual, integración reactiva con Convex y el blueprint de diseño de la landing pública.

---

## 📌 1. ¿Qué es Laborin y qué hace la página actual?

**Laborin** es una *Content Machine* para desarrolladores de software que transforma el trabajo técnico real (`git push`) en historias de alto impacto para LinkedIn, solicitando aprobación previa en lenguaje natural a través de **WhatsApp (Kapso)**.

### Flujo de Valor Central:
1. **GitHub Ingestion:** Escucha eventos `push` autenticados con HMAC SHA-256 y extrae los diffs limpios (omitiendo lockfiles y binarios).
2. **Story Intelligence:** Analiza los commits y detecta arcos narrativos (*Problema → Intentos → Solución → Aprendizaje clave → Impacto*).
3. **Draft Generation:** Redacta publicaciones para LinkedIn basadas estrictamente en evidencia real (sin números inventados ni alucinaciones).
4. **WhatsApp Approval (Human-in-the-loop):** Envía el borrador por WhatsApp. El desarrollador puede pedir revisiones en lenguaje natural (*"hazlo más corto"*, *"cambia el inicio"*) o aprobarlo (*"Ta bueno, publícalo noma"*).
5. **LinkedIn Publishing:** Publica automáticamente en el perfil del desarrollador mediante la API oficial de LinkedIn y almacena el URN de trazabilidad.

---

## 🏗️ 2. Arquitectura de la Aplicación Web (`apps/web`)

La aplicación web está construida con:
- **Framework:** [Next.js 16](https://nextjs.org/) con App Router y Turbopack.
- **Runtimes & UI:** React 19, TypeScript 5.9, Tailwind CSS v4, Lucide Icons.
- **Conexión en Tiempo Real:** [Convex React Client](https://docs.convex.dev/quick-start#set-up-convex-in-your-react-app) mediante WebSockets persistentes (`useQuery`).

### Componentes Principales Actuales:
- [`app/page.tsx`](app/page.tsx): Layout principal y orquestador del dashboard.
- [`app/providers.tsx`](app/providers.tsx): Proveedor de contexto para `ConvexProvider`.
- [`components/live-activity-stream.tsx`](components/live-activity-stream.tsx): Timeline en vivo de eventos (`activityEvents`) que se actualiza instantáneamente ante cada webhook, commit, análisis o mensaje de WhatsApp.
- [`components/story-draft-viewer.tsx`](components/story-draft-viewer.tsx): Visor interactivo de las historias detectadas, desglose técnico y previsualización del borrador con su estado de aprobación y enlace directo a LinkedIn.

---

## 🎨 3. Blueprint de Diseño: Landing Page estilo Vercel / Monochrome

Para transformar esta vista en una **Landing Page de nivel internacional**, aplicaremos la estética minimalista y de alta precisión de **Vercel, Linear y Raycast**.

### 🌟 Sistema de Diseño & Estética

#### 1. Tipografía: **Poppins + JetBrains Mono**
- **Fuente Principal:** `Poppins` (Google Fonts: pesos 300, 400, 500, 600, 700, 800) para títulos limpios, headings geométricos y copy moderno.
- **Fuente de Código / Datos:** `JetBrains Mono` o `Geist Mono` para commits, diffs, JSONs, URNs y badges técnicos.

#### 2. Paleta de Color: **Monochrome de Alto Contraste (Black & White)**
- **Fondo Primario:** `#000000` (Pure Pitch Black).
- **Fondo Secundario / Cards:** `#09090b` (Zinc 950) y `#121215` con bordes sutiles `border-white/10`.
- **Texto Principal:** `#ffffff` (Blanco puro).
- **Texto Secundario:** `#a1a1aa` (Zinc 400) y `#71717a` (Zinc 500).
- **Acentos de Estado:**
  - `Emerald (#10b981 / #34d399)`: Eventos completados, Convex live, WhatsApp aprobado.
  - `Sky (#0284c7 / #38bdf8)`: Análisis en curso, revisiones V2.
  - `Amber (#f59e0b)`: En espera de aprobación humana.
- **Efectos de Luz:** Resplandores radiales sutiles en el fondo (`radial-gradient`) y gradientes de borde en hover.

---

## 📐 4. Estructura de Secciones de la Landing Page

```
┌──────────────────────────────────────────────────────────────┐
│  1. HEADER / NAVBAR (Logo Laborin, Live Status Pill, CTA)    │
├──────────────────────────────────────────────────────────────┤
│  2. HERO SECTION                                             │
│     - Glowing Badge: "Evidence before content"               │
│     - H1 (Poppins Bold): "Tu código ya tiene una historia.   │
│                          Laborin la encuentra."              │
│     - Subtitle + CTAs: [Conectar GitHub] [Ver Demo en Vivo]  │
│     - Mockup Interactivo: Terminal -> AI -> WhatsApp         │
├──────────────────────────────────────────────────────────────┤
│  3. METRICS & TRUST BAR (0 Alucinaciones, 100% Control)      │
├──────────────────────────────────────────────────────────────┤
│  4. THE 4-STEP PIPELINE (Bento Grid Interactivo)             │
│     [1. Git Push Filter]        [2. Story Intelligence]      │
│     [3. WhatsApp NLU Chatbot]   [4. One-Click LinkedIn API]  │
├──────────────────────────────────────────────────────────────┤
│  5. LIVE INTERACTIVE PLAYGROUND (Dashboard Realtime Convex)  │
├──────────────────────────────────────────────────────────────┤
│  6. BEFORE & AFTER (Post genérico de IA vs Post Grounded)    │
├──────────────────────────────────────────────────────────────┤
│  7. SECURITY & INTEGRATIONS (Fernet Encrypted, HMAC SHA-256) │
├──────────────────────────────────────────────────────────────┤
│  8. BOTTOM CTA BANNER ("Convierte tus commits en portafolio")│
├──────────────────────────────────────────────────────────────┤
│  9. MINIMAL FOOTER                                           │
└──────────────────────────────────────────────────────────────┘
```

---

## 💻 5. Código de Integración de la Fuente Poppins (Next.js)

En `apps/web/app/layout.tsx`:

```tsx
import { Poppins, JetBrains_Mono } from "next/font/google";
import "./globals.css";

const poppins = Poppins({
  subsets: ["latin"],
  weight: ["300", "400", "500", "600", "700", "800"],
  variable: "--font-poppins",
  display: "swap",
});

const jetbrainsMono = JetBrains_Mono({
  subsets: ["latin"],
  weight: ["400", "500", "600"],
  variable: "--font-mono",
  display: "swap",
});

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="es" className={`${poppins.variable} ${jetbrainsMono.variable} dark`}>
      <body className="bg-black text-white font-sans antialiased selection:bg-white selection:text-black">
        {children}
      </body>
    </html>
  );
}
```

---

## 🛠️ 6. Comandos para Desarrollo y Verificación

```bash
# Iniciar frontend en local (puerto 3000)
pnpm dev:web

# Verificar linter, tipos y build de producción
pnpm lint:web
pnpm typecheck:web
pnpm build:web

# Verificación integral del monorepo
pnpm check
```
