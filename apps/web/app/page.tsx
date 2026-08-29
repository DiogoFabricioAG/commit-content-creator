import Link from "next/link";
import {
  Activity,
  ArrowRight,
  GitCommitHorizontal,
  LayoutDashboard,
  ShieldCheck,
  Sparkles,
  Wand2,
} from "lucide-react";


export default function LandingPortalPage() {
  return (
    <main className="min-h-screen bg-black text-white selection:bg-white selection:text-black">
      <div className="mx-auto flex min-h-screen w-full max-w-6xl flex-col justify-between px-6 py-10 lg:px-10">
        {/* Navbar */}
        <header className="flex items-center justify-between border-b border-white/10 pb-6">
          <div className="flex items-center gap-3">
            <div className="flex size-10 items-center justify-center rounded-xl bg-white text-black font-bold shadow-lg shadow-white/10">
              PoW
            </div>
            <div>
              <p className="text-sm font-semibold tracking-tight text-white">Proof of Work</p>
              <p className="text-xs text-zinc-400">Content Machine for Developers</p>
            </div>
          </div>

          <div className="flex items-center gap-4">
            <Link
              href="/dashboard"
              className="inline-flex items-center gap-2 rounded-xl border border-white/15 bg-white/5 px-4 py-2 text-xs font-semibold text-white hover:bg-white/10 transition"
            >
              <LayoutDashboard className="size-3.5" />
              Abrir Dashboard
            </Link>
          </div>
        </header>

        {/* Hero */}
        <section className="my-auto py-16 text-center sm:py-24">
          <div className="mx-auto inline-flex items-center gap-2 rounded-full border border-white/10 bg-white/[0.03] px-4 py-1.5 text-xs text-zinc-400">
            <span className="size-2 rounded-full bg-emerald-400 animate-pulse" />
            Evidence before content · Zero hallucination
          </div>

          <h1 className="mx-auto mt-6 max-w-4xl text-4xl font-bold tracking-tight text-white sm:text-6xl sm:leading-[1.1]">
            Tu código ya tiene una historia.
            <span className="block text-zinc-400">Proof of Work la encuentra y publica.</span>
          </h1>

          <p className="mx-auto mt-6 max-w-2xl text-base leading-relaxed text-zinc-400 sm:text-lg">
            Observa tus commits de Git, detecta narrativas técnicas sustentadas en código real, genera borradores para LinkedIn y pide aprobación directa por WhatsApp.
          </p>

          {/* Action CTAs */}
          <div className="mt-10 flex flex-wrap items-center justify-center gap-4">
            <Link
              href="/dashboard"
              className="inline-flex items-center gap-2 rounded-2xl bg-white px-6 py-3.5 text-sm font-bold text-black hover:bg-zinc-200 transition shadow-xl shadow-white/10"
            >
              <LayoutDashboard className="size-4" />
              Ir al Dashboard en Vivo
              <ArrowRight className="size-4" />
            </Link>

            <Link
              href="/dashboard"
              className="inline-flex items-center gap-2 rounded-2xl border border-white/15 bg-white/5 px-6 py-3.5 text-sm font-semibold text-white hover:bg-white/10 transition"
            >
              <Wand2 className="size-4 text-emerald-400" />
              Configurar Voz & Onboarding
            </Link>
          </div>

          {/* 4 Steps Bento Bar */}
          <div className="mx-auto mt-16 grid max-w-4xl gap-4 sm:grid-cols-2 lg:grid-cols-4 text-left">
            {[
              {
                step: "01",
                title: "Git Push",
                desc: "Filtra lockfiles y extrae diffs limpios.",
                icon: GitCommitHorizontal,
              },
              {
                step: "02",
                title: "Story AI",
                desc: "Detecta el problema, solución y aprendizaje.",
                icon: Sparkles,
              },
              {
                step: "03",
                title: "WhatsApp Chat",
                desc: "Revisa o aprueba en lenguaje natural.",
                icon: ShieldCheck,
              },
              {
                step: "04",
                title: "LinkedIn Post",
                desc: "Publicación con trazabilidad de versiones.",
                icon: Activity,
              },
            ].map((item) => {
              const Icon = item.icon;
              return (
                <div
                  key={item.step}
                  className="rounded-2xl border border-white/10 bg-zinc-950/60 p-4 backdrop-blur-sm"
                >
                  <div className="flex items-center justify-between">
                    <span className="font-mono text-xs text-zinc-500">{item.step}</span>
                    <Icon className="size-4 text-zinc-400" />
                  </div>
                  <p className="mt-3 text-sm font-semibold text-white">{item.title}</p>
                  <p className="mt-1 text-xs text-zinc-400 leading-snug">{item.desc}</p>
                </div>
              );
            })}
          </div>
        </section>

        {/* Footer */}
        <footer className="flex flex-col gap-2 border-t border-white/10 py-6 text-xs text-zinc-500 sm:flex-row sm:items-center sm:justify-between">
          <span>Proof of Work · Content Machine</span>
          <div className="flex items-center gap-4">
            <Link href="/dashboard" className="hover:text-zinc-300 transition">
              Dashboard
            </Link>
            <span>·</span>
            <span className="text-zinc-600">v1.0 Producción</span>
          </div>
        </footer>
      </div>
    </main>
  );
}
