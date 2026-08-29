"use client";

import { useState } from "react";
import { useQuery } from "convex/react";
import {
  Activity,
  ArrowUpRight,
  CheckCircle2,
  GitCommitHorizontal,
  LayoutDashboard,
  Radio,
  ShieldCheck,
  Sparkles,
  Wand2,
} from "lucide-react";
import { api } from "@convex/api";
import { LiveActivityStream } from "@/components/live-activity-stream";
import { OnboardingWizard } from "@/components/onboarding-wizard";
import { StoryDraftViewer } from "@/components/story-draft-viewer";

const stages = [
  { label: "1. GitHub Push", detail: "Webhook autenticado & normalizado", icon: GitCommitHorizontal },
  { label: "2. Story Intelligence", detail: "Extracción, análisis y agrupación", icon: Activity },
  { label: "3. WhatsApp / Kapso", detail: "Aprobación natural o revisión", icon: ShieldCheck },
  { label: "4. LinkedIn Posts API", detail: "Publicación con trazabilidad de versiones", icon: ArrowUpRight },
];

export default function Home() {
  const [activeTab, setActiveTab] = useState<"dashboard" | "onboarding">("dashboard");

  const defaultUser = useQuery(api.users.getByWhatsappPhone, {
    whatsappPhone: "+51999888777",
  });
  const prefs = useQuery(
    api.preferences.getForUser,
    defaultUser?._id ? { userId: defaultUser._id } : "skip",
  );

  return (
    <main className="min-h-screen bg-[var(--background)] text-[var(--foreground)]">
      <div className="mx-auto flex min-h-screen w-full max-w-7xl flex-col px-6 py-8 lg:px-10">
        {/* Header */}
        <header className="flex items-center justify-between border-b border-[var(--line)] pb-6">
          <div className="flex items-center gap-3">
            <div className="flex size-10 items-center justify-center rounded-xl bg-[var(--accent)] text-sm font-bold text-white shadow-lg shadow-[var(--accent)]/30">
              PoW
            </div>
            <div>
              <p className="text-sm font-semibold tracking-tight">Proof of Work</p>
              <p className="text-xs text-[var(--muted)]">Story intelligence para developers</p>
            </div>
          </div>

          <div className="flex items-center gap-3">
            {/* Tab Switcher */}
            <div className="flex items-center rounded-xl border border-white/10 bg-white/[0.03] p-1">
              <button
                type="button"
                onClick={() => setActiveTab("dashboard")}
                className={`inline-flex items-center gap-1.5 rounded-lg px-3 py-1.5 text-xs font-semibold transition ${
                  activeTab === "dashboard"
                    ? "bg-white text-black shadow-sm"
                    : "text-zinc-400 hover:text-white"
                }`}
              >
                <LayoutDashboard className="size-3.5" />
                Dashboard
              </button>
              <button
                type="button"
                onClick={() => setActiveTab("onboarding")}
                className={`inline-flex items-center gap-1.5 rounded-lg px-3 py-1.5 text-xs font-semibold transition ${
                  activeTab === "onboarding"
                    ? "bg-white text-black shadow-sm"
                    : "text-zinc-400 hover:text-white"
                }`}
              >
                <Wand2 className="size-3.5" />
                Voz & Onboarding
                {prefs?.onboardingCompleted ? (
                  <span className="size-1.5 rounded-full bg-emerald-400" />
                ) : (
                  <span className="size-1.5 rounded-full bg-amber-400 animate-pulse" />
                )}
              </button>
            </div>

            <span className="hidden sm:inline-flex items-center gap-1.5 rounded-full border border-emerald-500/30 bg-emerald-500/10 px-3 py-1 font-mono text-xs font-medium text-emerald-300">
              <span className="size-1.5 rounded-full bg-emerald-400 animate-ping" />
              Convex Live
            </span>
          </div>
        </header>

        {/* Hero & Subhead */}
        <section className="py-8">
          <div className="inline-flex items-center gap-2 rounded-full border border-[var(--line)] bg-white/[0.03] px-3 py-1.5 text-xs text-[var(--muted)]">
            <Radio className="size-3.5 text-emerald-400 animate-pulse" />
            Evidence before content · Human approval before publishing
          </div>
          <h1 className="mt-4 max-w-4xl text-3xl font-semibold leading-[1.1] tracking-[-0.04em] sm:text-5xl">
            Tu trabajo ya tiene una historia.
            <span className="block text-[var(--accent-soft)]">Proof of Work la encuentra y publica.</span>
          </h1>
          <p className="mt-3 max-w-2xl text-sm leading-relaxed text-[var(--muted)] sm:text-base">
            Observa tu actividad de Git, descubre la narrativa técnica detrás de tus commits, prepara borradores grounded para LinkedIn y pide aprobación directa por WhatsApp.
          </p>
        </section>

        {/* Tab View: ONBOARDING WIZARD */}
        {activeTab === "onboarding" ? (
          <section className="pb-16">
            <OnboardingWizard
              userId={defaultUser?._id}
              onComplete={() => setActiveTab("dashboard")}
            />
          </section>
        ) : (
          /* Tab View: LIVE DASHBOARD */
          <>
            {/* Pipeline Overview */}
            <div className="mb-8 grid gap-3 sm:grid-cols-2 lg:grid-cols-4">
              {stages.map((stage) => {
                const Icon = stage.icon;
                return (
                  <div
                    key={stage.label}
                    className="flex flex-col justify-between rounded-2xl border border-[var(--line)] bg-white/[0.025] p-4"
                  >
                    <div className="flex items-center justify-between">
                      <div className="flex size-8 items-center justify-center rounded-lg bg-white/[0.06] text-[var(--accent-soft)]">
                        <Icon className="size-4" />
                      </div>
                      <CheckCircle2 className="size-4 text-emerald-400" />
                    </div>
                    <div className="mt-4">
                      <p className="text-sm font-semibold">{stage.label}</p>
                      <p className="text-xs text-[var(--muted)] mt-0.5">{stage.detail}</p>
                    </div>
                  </div>
                );
              })}
            </div>

            {/* Main Dashboard Workspace */}
            <section className="grid flex-1 gap-8 lg:grid-cols-[1.2fr_0.8fr] pb-16">
              {/* Left Column: Story Intelligence & Post Versioning */}
              <div>
                <div className="mb-4 flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <Sparkles className="size-4 text-[var(--accent-soft)]" />
                    <h2 className="text-lg font-semibold tracking-tight">Narrativa & Borrador</h2>
                  </div>
                  <span className="font-mono text-xs text-[var(--muted)]">Actualización reactiva</span>
                </div>

                <StoryDraftViewer />
              </div>

              {/* Right Column: Live Activity Stream */}
              <div>
                <div className="mb-4 flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <Activity className="size-4 text-emerald-400" />
                    <h2 className="text-lg font-semibold tracking-tight">Actividad en Vivo</h2>
                  </div>
                  <span className="font-mono text-xs text-[var(--muted)]">Convex Sync</span>
                </div>

                <div className="rounded-3xl border border-[var(--line)] bg-white/[0.035] p-5 shadow-xl">
                  <LiveActivityStream />
                </div>
              </div>
            </section>
          </>
        )}

        {/* Footer */}
        <footer className="flex flex-col gap-2 border-t border-[var(--line)] py-6 text-xs text-[var(--muted)] sm:flex-row sm:items-center sm:justify-between">
          <span>Proof of Work · Content Machine Vertical Slice</span>
          <span>LinkedIn + Kapso WhatsApp + Convex + FastAPI + Next.js</span>
        </footer>
      </div>
    </main>
  );
}

