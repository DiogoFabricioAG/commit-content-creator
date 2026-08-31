import Link from "next/link";
import {
  ArrowRight,
  Check,
  CheckCircle2,
  ChevronRight,
  BriefcaseBusiness,
  GitBranch,
  GitPullRequest,
  LockKeyhole,
  MessageCircle,
  MousePointerClick,
  ScanSearch,
  ShieldCheck,
  Sparkles,
  WandSparkles,
} from "lucide-react";

import { LandingVisitorCount } from "../components/landing-visitor-count";

const steps = [
  {
    number: "01",
    icon: GitPullRequest,
    title: "Conecta tu trabajo",
    description: "Elige los repositorios que cuentan lo que estás construyendo.",
  },
  {
    number: "02",
    icon: ScanSearch,
    title: "Detectamos la historia",
    description: "Agrupamos cambios relacionados y encontramos el problema, la decisión y el aprendizaje.",
  },
  {
    number: "03",
    icon: MessageCircle,
    title: "Revísala en WhatsApp",
    description: "Aprueba, pausa o pide cambios en el canal que ya usas todos los días.",
  },
  {
    number: "04",
    icon: BriefcaseBusiness,
    title: "Publica con control",
    description: "Solo la versión que aprobaste llega a LinkedIn. Nada se publica por sorpresa.",
  },
];

const trustPoints = [
  "Tus repositorios permanecen aislados",
  "Cada afirmación conserva su evidencia",
  "La aprobación humana es obligatoria",
  "Tus credenciales nunca llegan al navegador",
];

function BrandMark({ compact = false }: { compact?: boolean }) {
  return (
    <span className="inline-flex items-center gap-2.5" aria-label="LaborIN">
      <span className="brand-mark" aria-hidden="true">
        <GitBranch className="size-4" strokeWidth={2.4} />
      </span>
      {!compact ? <span className="text-[15px] font-semibold tracking-[-0.02em]">LaborIN</span> : null}
    </span>
  );
}

export default function Home() {
  return (
    <main className="landing-shell overflow-hidden">
      <div className="landing-glow landing-glow-one" />
      <div className="landing-glow landing-glow-two" />

      <div className="system-strip" aria-hidden="true">
        <span>**** LaborIN BASIC V1 ****</span>
        <span>64K STORY MEMORY · 38911 CLAIMS FREE</span>
        <span>READY.</span>
      </div>

      <header className="relative z-20 mx-auto flex w-full max-w-[1180px] items-center justify-between px-5 py-5 sm:px-8 lg:px-10">
        <Link href="/" className="rounded-lg focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-[var(--accent)]">
          <BrandMark />
        </Link>

        <nav className="hidden items-center gap-7 text-sm text-[var(--landing-muted)] md:flex" aria-label="Navegación principal">
          <a className="nav-link" href="#como-funciona">Cómo funciona</a>
          <a className="nav-link" href="#seguridad">Seguridad</a>
          <a className="nav-link" href="#demo">Demo</a>
        </nav>

        <Link
          href="/dashboard"
          className="group inline-flex h-10 items-center gap-2 rounded-full border border-[var(--landing-line)] bg-white/[0.055] px-4 text-sm font-medium transition hover:border-white/25 hover:bg-white/[0.09] focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-[var(--accent)]"
        >
          RUN dashboard
          <ArrowRight className="size-3.5 transition-transform group-hover:translate-x-0.5" />
        </Link>
      </header>

      <section className="relative z-10 mx-auto grid min-h-[720px] w-full max-w-[1180px] items-center gap-14 px-5 pb-20 pt-16 sm:px-8 lg:grid-cols-[1.02fr_0.98fr] lg:px-10 lg:pb-28 lg:pt-20">
        <div className="min-w-0">
          <p className="basic-command">10 PRINT &quot;EVIDENCE BEFORE CONTENT&quot;</p>
          <div className="eyebrow">
            <span className="status-dot" />
            READY. Story intelligence para developers
          </div>

          <h1 className="mt-7 max-w-3xl text-[clamp(3.25rem,7.2vw,6.7rem)] font-semibold leading-[0.91] tracking-[-0.072em] text-[var(--landing-text)]">
            Tu código ya tiene una historia.
          </h1>
          <p className="mt-7 max-w-xl text-lg leading-8 text-[var(--landing-muted)] sm:text-xl">
            Convierte el trabajo real de GitHub en contenido técnico claro, sustentado y listo para LinkedIn — sin detenerte a redactarlo.
          </p>

          <div className="mt-9 flex flex-col gap-3 sm:flex-row">
            <Link href="/dashboard" className="primary-cta group">
              RUN explorar demo
              <ArrowRight className="size-4 transition-transform group-hover:translate-x-1" />
            </Link>
            <a href="#como-funciona" className="secondary-cta">
              GOTO cómo funciona
              <ChevronRight className="size-4" />
            </a>
          </div>

          <div className="mt-8 flex flex-wrap items-center gap-x-5 gap-y-2 text-xs text-[var(--landing-subtle)]">
            <span className="inline-flex items-center gap-1.5"><Check className="size-3.5 text-[var(--signal)]" /> Evidencia antes que contenido</span>
            <span className="inline-flex items-center gap-1.5"><Check className="size-3.5 text-[var(--signal)]" /> Tú apruebas cada publicación</span>
          </div>

          <div className="mt-7">
            <LandingVisitorCount />
          </div>
        </div>

        <div className="relative mx-auto min-w-0 w-full max-w-[540px] lg:mr-0">
          <div className="hero-orbit" aria-hidden="true" />
          <div className="product-window">
            <div className="window-bar">
              <div className="flex gap-1.5" aria-hidden="true">
                <span className="window-dot bg-[#e8e4d8]" />
                <span className="window-dot bg-[#77786f]" />
                <span className="window-dot bg-[#a6ff8f]" />
              </div>
              <span className="font-mono text-[10px] uppercase tracking-[0.18em] text-[var(--landing-subtle)]">Pipeline activo</span>
              <span className="flex items-center gap-1.5 text-[10px] text-[var(--signal)]"><span className="status-dot" /> Live</span>
            </div>

            <div className="space-y-3 p-4 sm:p-5">
              <div className="pipeline-event">
                <div className="event-icon"><GitPullRequest className="size-4" /></div>
                <div className="min-w-0 flex-1">
                  <p className="text-[11px] uppercase tracking-[0.12em] text-[var(--landing-subtle)]">GitHub push recibido</p>
                  <p className="mt-1 truncate font-mono text-xs text-[var(--landing-text)]">refactor: replace polling with websocket events</p>
                </div>
                <CheckCircle2 className="size-4 shrink-0 text-[var(--signal)]" />
              </div>

              <div className="ml-7 h-3 border-l border-dashed border-white/15" aria-hidden="true" />

              <div className="story-card">
                <div className="flex items-center justify-between gap-4">
                  <span className="inline-flex items-center gap-2 text-[11px] font-medium uppercase tracking-[0.14em] text-[var(--accent-soft)]">
                    <Sparkles className="size-3.5" /> Historia detectada
                  </span>
                  <span className="rounded-full bg-[var(--signal)]/10 px-2 py-1 text-[10px] font-medium text-[var(--signal)]">91% confianza</span>
                </div>
                <h2 className="mt-4 text-xl font-semibold leading-tight tracking-[-0.025em]">De polling constante a eventos en tiempo real</h2>
                <p className="mt-2 text-sm leading-6 text-[var(--landing-muted)]">
                  Tres cambios revelan una misma decisión técnica: reducir solicitudes duplicadas y simplificar el flujo de notificaciones.
                </p>
                <div className="mt-4 flex flex-wrap gap-2">
                  <span className="evidence-chip">3 commits</span>
                  <span className="evidence-chip">5 archivos</span>
                  <span className="evidence-chip">WebSockets</span>
                </div>
              </div>

              <div className="ml-7 h-3 border-l border-dashed border-white/15" aria-hidden="true" />

              <div className="pipeline-event border-[var(--accent)]/25 bg-[var(--accent)]/[0.065]">
                <div className="event-icon bg-[#25d366]/10 text-[#6ee7a0]"><MessageCircle className="size-4" /></div>
                <div className="flex-1">
                  <p className="text-xs font-medium">Borrador enviado a WhatsApp</p>
                  <p className="mt-1 text-[11px] text-[var(--landing-muted)]">Esperando tu aprobación antes de publicar</p>
                </div>
                <span className="rounded-full border border-amber-300/20 bg-amber-300/10 px-2 py-1 text-[9px] uppercase tracking-wider text-amber-200">Pendiente</span>
              </div>
            </div>
          </div>

          <div className="floating-proof hidden sm:block">
            <ShieldCheck className="size-4 text-[var(--signal)]" />
            <div>
              <p className="text-xs font-semibold">Publicación protegida</p>
              <p className="mt-0.5 text-[10px] text-[var(--landing-subtle)]">Requiere aprobación explícita</p>
            </div>
          </div>
        </div>
      </section>

      <section className="protocol-strip relative z-10 border-y border-[var(--landing-line)] bg-white/[0.018]">
        <div className="mx-auto flex w-full max-w-[1180px] flex-col items-center justify-between gap-5 px-5 py-6 sm:px-8 md:flex-row lg:px-10">
          <p className="text-xs uppercase tracking-[0.18em] text-[var(--landing-subtle)]">Del trabajo a la publicación, en un solo flujo</p>
          <div className="flex flex-wrap items-center justify-center gap-x-8 gap-y-4 text-sm font-medium text-[var(--landing-muted)]">
            <span className="integration-item"><GitPullRequest className="size-4" /> GitHub</span>
            <span className="integration-arrow">→</span>
            <span className="integration-item"><WandSparkles className="size-4" /> Story AI</span>
            <span className="integration-arrow">→</span>
            <span className="integration-item"><MessageCircle className="size-4" /> WhatsApp</span>
            <span className="integration-arrow">→</span>
            <span className="integration-item"><BriefcaseBusiness className="size-4" /> LinkedIn</span>
          </div>
        </div>
      </section>

      <section id="como-funciona" className="relative z-10 mx-auto w-full max-w-[1180px] scroll-mt-16 px-5 py-24 sm:px-8 lg:px-10 lg:py-32">
        <div className="max-w-2xl">
          <p className="section-kicker">Cómo funciona</p>
          <h2 className="section-title mt-4">Sigue construyendo.<br />Nosotros conectamos los puntos.</h2>
          <p className="section-copy mt-5">LaborIN observa señales verificables, encuentra una narrativa coherente y te deja la última palabra.</p>
        </div>

        <div className="step-grid mt-14 grid gap-px overflow-hidden rounded-[28px] border border-[var(--landing-line)] bg-[var(--landing-line)] md:grid-cols-2 lg:grid-cols-4">
          {steps.map((step) => {
            const Icon = step.icon;
            return (
              <article key={step.number} className="step-card">
                <div className="flex items-start justify-between">
                  <div className="step-icon"><Icon className="size-5" /></div>
                  <span className="font-mono text-xs text-[var(--landing-subtle)]">{step.number}</span>
                </div>
                <h3 className="mt-12 text-lg font-semibold tracking-[-0.02em]">{step.title}</h3>
                <p className="mt-3 text-sm leading-6 text-[var(--landing-muted)]">{step.description}</p>
              </article>
            );
          })}
        </div>
      </section>

      <section id="demo" className="relative z-10 mx-auto grid w-full max-w-[1180px] scroll-mt-16 gap-14 px-5 pb-24 sm:px-8 lg:grid-cols-[0.82fr_1.18fr] lg:items-center lg:px-10 lg:pb-32">
        <div>
          <p className="section-kicker">Una revisión que sí se siente natural</p>
          <h2 className="section-title mt-4">Tu criterio no se automatiza.</h2>
          <p className="section-copy mt-5">
            Conversa con el borrador desde WhatsApp. Pide una versión más corta, cambia el inicio o déjalo pendiente. Publicar siempre requiere un sí claro.
          </p>
          <div className="mt-7 inline-flex items-center gap-2 rounded-full border border-[var(--signal)]/20 bg-[var(--signal)]/[0.06] px-3 py-2 text-xs text-[var(--signal)]">
            <ShieldCheck className="size-3.5" /> Un mensaje ambiguo nunca publica
          </div>
        </div>

        <div className="conversation-panel">
          <div className="flex items-center gap-3 border-b border-[var(--landing-line)] px-5 py-4">
            <div className="flex size-9 items-center justify-center rounded-full bg-[#25d366]/15 text-[#6ee7a0]"><MessageCircle className="size-4" /></div>
            <div>
              <p className="text-sm font-semibold">LaborIN</p>
              <p className="text-[10px] text-[var(--signal)]">en línea · aprobación segura</p>
            </div>
          </div>
          <div className="space-y-4 p-5 sm:p-7">
            <div className="chat-bubble chat-incoming">
              <p className="text-[11px] font-semibold text-[var(--accent-soft)]">Nueva historia · Borrador V1</p>
              <p className="mt-2 text-sm leading-6">Dejamos de preguntar “¿hay algo nuevo?” cada pocos segundos. Ahora el servidor nos avisa justo cuando importa...</p>
              <p className="mt-3 text-[10px] text-[var(--landing-subtle)]">Basado en 3 commits · 5 archivos</p>
            </div>
            <div className="chat-bubble chat-outgoing">Está bueno, pero hazlo más corto.</div>
            <div className="chat-bubble chat-incoming">
              <p className="text-[11px] font-semibold text-[var(--signal)]">Listo · Borrador V2</p>
              <p className="mt-2 text-sm leading-6">Reemplazamos polling por WebSockets: menos ruido en el cliente y un flujo de notificaciones más directo.</p>
            </div>
            <div className="chat-bubble chat-outgoing">Sí, ahora sí. Publícalo.</div>
            <div className="flex items-center gap-2 pl-2 text-xs text-[var(--signal)]"><CheckCircle2 className="size-4" /> V2 aprobada · publicando en LinkedIn</div>
          </div>
        </div>
      </section>

      <section id="seguridad" className="relative z-10 border-y border-[var(--landing-line)] bg-[#0d121c]">
        <div className="mx-auto grid w-full max-w-[1180px] gap-14 px-5 py-24 sm:px-8 lg:grid-cols-2 lg:items-center lg:px-10 lg:py-28">
          <div className="security-visual" aria-hidden="true">
            <div className="security-ring security-ring-one" />
            <div className="security-ring security-ring-two" />
            <div className="security-core"><LockKeyhole className="size-8" /></div>
            <div className="security-label security-label-one">Evidencia</div>
            <div className="security-label security-label-two">Tu aprobación</div>
            <div className="security-label security-label-three">Versión vigente</div>
          </div>
          <div>
            <p className="section-kicker">Confianza por diseño</p>
            <h2 className="section-title mt-4">Automatiza el trabajo pesado, no la decisión.</h2>
            <p className="section-copy mt-5">El contenido se construye sobre cambios observables y la publicación se mantiene bajo tu control.</p>
            <ul className="mt-8 grid gap-4 sm:grid-cols-2">
              {trustPoints.map((point) => (
                <li key={point} className="flex items-start gap-3 text-sm leading-6 text-[var(--landing-muted)]">
                  <span className="mt-1 flex size-5 shrink-0 items-center justify-center rounded-full bg-[var(--signal)]/10 text-[var(--signal)]"><Check className="size-3" /></span>
                  {point}
                </li>
              ))}
            </ul>
          </div>
        </div>
      </section>

      <section className="relative z-10 mx-auto w-full max-w-[1180px] px-5 py-24 sm:px-8 lg:px-10 lg:py-32">
        <div className="cta-panel">
          <div className="cta-grid" aria-hidden="true" />
          <div className="relative z-10 max-w-2xl">
            <div className="eyebrow border-white/10 bg-black/10 text-white/65">
              <MousePointerClick className="size-3.5 text-[var(--signal)]" /> RUN &quot;DEMO PRIVADA&quot;
            </div>
            <h2 className="mt-6 text-4xl font-semibold leading-[1.02] tracking-[-0.055em] sm:text-6xl">Haz visible el trabajo que ya estás haciendo.</h2>
            <p className="mt-5 max-w-xl text-base leading-7 text-white/65">Explora el recorrido actual de texto para LinkedIn, con evidencia técnica y aprobación por WhatsApp.</p>
            <Link href="/dashboard" className="primary-cta mt-8 bg-white text-[#11141b] hover:bg-white/90">
              RUN dashboard <ArrowRight className="size-4" />
            </Link>
          </div>
        </div>
      </section>

      <footer className="relative z-10 border-t border-[var(--landing-line)]">
        <div className="mx-auto flex w-full max-w-[1180px] flex-col gap-5 px-5 py-8 text-xs text-[var(--landing-subtle)] sm:flex-row sm:items-center sm:justify-between sm:px-8 lg:px-10">
          <BrandMark />
          <p>READY. De evidencia real a contenido que sí suena a ti.</p>
          <p>© 2026 · 64K STORY SYSTEM</p>
        </div>
      </footer>
    </main>
  );
}
