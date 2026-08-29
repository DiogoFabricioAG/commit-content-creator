import { Activity, ArrowUpRight, GitCommitHorizontal, Radio, ShieldCheck } from "lucide-react";

import { Button } from "@/components/ui/button";

const stages = [
  { label: "GitHub", detail: "Conexión pendiente", icon: GitCommitHorizontal },
  { label: "Inteligencia", detail: "Esperando evidencia", icon: Activity },
  { label: "Aprobación", detail: "WhatsApp + Kapso", icon: ShieldCheck },
  { label: "LinkedIn", detail: "Publicación protegida", icon: ArrowUpRight },
];

export default function Home() {
  return (
    <main className="min-h-screen bg-[var(--background)] text-[var(--foreground)]">
      <div className="mx-auto flex min-h-screen w-full max-w-6xl flex-col px-6 py-8 lg:px-10">
        <header className="flex items-center justify-between border-b border-[var(--line)] pb-6">
          <div className="flex items-center gap-3">
            <div className="flex size-10 items-center justify-center rounded-xl bg-[var(--accent)] text-sm font-bold text-white">
              PoW
            </div>
            <div>
              <p className="text-sm font-semibold tracking-tight">Proof of Work</p>
              <p className="text-xs text-[var(--muted)]">Story intelligence para developers</p>
            </div>
          </div>
          <span className="rounded-full border border-amber-300/30 bg-amber-300/10 px-3 py-1 text-xs font-medium text-amber-200">
            Foundation
          </span>
        </header>

        <section className="grid flex-1 items-center gap-12 py-14 lg:grid-cols-[1.1fr_0.9fr]">
          <div>
            <div className="mb-6 inline-flex items-center gap-2 rounded-full border border-[var(--line)] bg-white/[0.03] px-3 py-1.5 text-xs text-[var(--muted)]">
              <Radio className="size-3.5 text-emerald-300" />
              Sistema preparado para recibir evidencia
            </div>
            <h1 className="max-w-3xl text-5xl font-semibold leading-[0.98] tracking-[-0.06em] sm:text-6xl">
              Tu trabajo ya tiene una historia.
              <span className="block text-[var(--accent-soft)]">Proof of Work la encuentra.</span>
            </h1>
            <p className="mt-6 max-w-xl text-base leading-7 text-[var(--muted)]">
              El dashboard base está listo para conectar GitHub, entender cambios relacionados y llevar un borrador a WhatsApp antes de publicar cualquier cosa.
            </p>
            <div className="mt-8 flex flex-wrap gap-3">
              <Button>Configurar conexiones</Button>
              <Button variant="outline">Ver arquitectura</Button>
            </div>
          </div>

          <div className="rounded-3xl border border-[var(--line)] bg-white/[0.035] p-5 shadow-2xl shadow-black/20">
            <div className="flex items-start justify-between border-b border-[var(--line)] pb-5">
              <div>
                <p className="text-xs uppercase tracking-[0.18em] text-[var(--muted)]">Live pipeline</p>
                <h2 className="mt-2 text-lg font-semibold">Primera rebanada vertical</h2>
              </div>
              <span className="rounded-full bg-white/[0.06] px-2.5 py-1 text-[10px] font-medium text-[var(--muted)]">
                Sin datos aún
              </span>
            </div>
            <div className="space-y-3 pt-5">
              {stages.map((stage, index) => {
                const Icon = stage.icon;
                return (
                  <div key={stage.label} className="relative flex items-center gap-3 rounded-2xl border border-[var(--line)] bg-black/10 p-3.5">
                    {index < stages.length - 1 ? (
                      <span className="absolute left-[27px] top-[49px] h-3 w-px bg-[var(--line)]" aria-hidden />
                    ) : null}
                    <div className="flex size-8 shrink-0 items-center justify-center rounded-lg bg-white/[0.06] text-[var(--accent-soft)]">
                      <Icon className="size-4" />
                    </div>
                    <div>
                      <p className="text-sm font-medium">{stage.label}</p>
                      <p className="text-xs text-[var(--muted)]">{stage.detail}</p>
                    </div>
                  </div>
                );
              })}
            </div>
          </div>
        </section>

        <footer className="flex flex-col gap-2 border-t border-[var(--line)] pt-5 text-xs text-[var(--muted)] sm:flex-row sm:items-center sm:justify-between">
          <span>Evidence before content · Human approval before publishing</span>
          <span>Milestone 0 / Foundation</span>
        </footer>
      </div>
    </main>
  );
}
