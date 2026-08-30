"use client";

import { useState, useEffect, Suspense } from "react";
import Link from "next/link";
import { useRouter, useSearchParams } from "next/navigation";
import { useQuery } from "convex/react";
import {
  Activity,
  ArrowLeft,
  ArrowUpRight,
  CheckCircle2,
  GitCommitHorizontal,
  LayoutDashboard,
  LogOut,
  Radio,
  ShieldCheck,
  Sparkles,
  User,
  Wand2,
} from "lucide-react";
import { api } from "@convex/api";
import { useAuth } from "../../contexts/auth-context";
import { AccountsSettings } from "@/components/accounts-settings";
import { HistoricalDigestLauncher } from "@/components/historical-digest-launcher";
import { LiveActivityStream } from "@/components/live-activity-stream";
import { OnboardingWizard } from "@/components/onboarding-wizard";
import { StoryDraftViewer } from "@/components/story-draft-viewer";

const stages = [
  { label: "1. GitHub Push", detail: "Webhook autenticado & normalizado", icon: GitCommitHorizontal },
  { label: "2. Story Intelligence", detail: "Extracción, análisis y agrupación", icon: Activity },
  { label: "3. WhatsApp / Kapso", detail: "Aprobación natural o revisión", icon: ShieldCheck },
  { label: "4. LinkedIn Posts API", detail: "Publicación con trazabilidad de versiones", icon: ArrowUpRight },
];

function DashboardContent() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const { user, userId, isAuthenticated, isLoading, logout } = useAuth();

  const [tabOverride, setTabOverride] = useState<"dashboard" | "onboarding" | "channels" | null>(null);

  const paramTab = searchParams.get("tab");
  const initialComputedTab: "dashboard" | "onboarding" | "channels" =
    paramTab === "onboarding" ? "onboarding" : paramTab === "channels" || paramTab === "settings" ? "channels" : "dashboard";

  const activeTab = tabOverride ?? initialComputedTab;

  // Auth Guard
  useEffect(() => {
    if (!isLoading && !isAuthenticated) {
      router.replace("/login?redirect=/dashboard");
    }
  }, [isAuthenticated, isLoading, router]);

  const prefs = useQuery(
    api.preferences.getForUser,
    userId ? { userId } : "skip",
  );

  const linkedinAccount = useQuery(
    api.socialAccounts.getByUserAndProvider,
    userId ? { userId, provider: "linkedin" } : "skip",
  );

  const repositories = useQuery(
    api.repositories.listForUser,
    userId ? { userId } : "skip",
  );

  const stories = useQuery(
    api.stories.listForUser,
    userId ? { userId, limit: 10 } : "skip",
  );

  const posts = useQuery(
    api.posts.listForUser,
    userId ? { userId, limit: 10 } : "skip",
  );

  if (isLoading) {
    return (
      <div className="min-h-screen bg-black flex items-center justify-center text-white">
        <div className="flex flex-col items-center gap-3">
          <div className="size-8 rounded-full border-2 border-white/20 border-t-white animate-spin" />
          <p className="text-xs font-mono text-zinc-400">Verificando sesión segura...</p>
        </div>
      </div>
    );
  }

  if (!isAuthenticated || !userId) {
    return null;
  }

  const allChannelsConfigured = !!user?.whatsappPhone && !!linkedinAccount && (repositories?.length ?? 0) > 0;

  return (
    <main className="dashboard-shell min-h-screen bg-black text-white selection:bg-white selection:text-black">
      <div className="mx-auto flex min-h-screen w-full max-w-7xl flex-col px-6 py-8 lg:px-10">
        {/* Top Navigation Bar */}
        <header className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between border-b border-white/10 pb-6">
          <div className="flex items-center gap-3">
            <Link
              href="/"
              className="flex size-10 items-center justify-center rounded-xl bg-white text-black font-bold shadow-lg shadow-white/10 hover:bg-zinc-200 transition"
              title="Volver a Inicio"
            >
              L·IN
            </Link>
            <div>
              <div className="flex items-center gap-2">
                <p className="text-sm font-semibold tracking-tight text-white">LaborIN Dashboard</p>
                <Link
                  href="/"
                  className="inline-flex items-center gap-1 text-[11px] text-zinc-500 hover:text-zinc-300 transition"
                >
                  <ArrowLeft className="size-3" /> Inicio
                </Link>
              </div>
              <p className="text-xs text-zinc-400">Story intelligence & content automation</p>
            </div>
          </div>

          <div className="flex flex-wrap items-center gap-3">
            {/* User Profile Badge */}
            <div className="flex items-center gap-2 rounded-xl border border-white/10 bg-white/[0.03] px-3 py-1.5 text-xs text-zinc-300">
              <div className="flex size-6 items-center justify-center rounded-full bg-emerald-500/20 text-emerald-400 font-bold text-[10px]">
                {user?.displayName ? user.displayName.slice(0, 2).toUpperCase() : <User className="size-3" />}
              </div>
              <div className="flex flex-col">
                <span className="font-semibold text-white leading-tight">
                  {user?.displayName || "Mi Espacio"}
                </span>
                <span className="font-mono text-[10px] text-zinc-500">
                  {user?.whatsappPhone || "WhatsApp"}
                </span>
              </div>
            </div>

            {/* Tab Switcher */}
            <div className="flex items-center rounded-xl border border-white/10 bg-white/[0.03] p-1">
              <button
                type="button"
                onClick={() => setTabOverride("dashboard")}
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
                onClick={() => setTabOverride("onboarding")}
                className={`inline-flex items-center gap-1.5 rounded-lg px-3 py-1.5 text-xs font-semibold transition ${
                  activeTab === "onboarding"
                    ? "bg-white text-black shadow-sm"
                    : "text-zinc-400 hover:text-white"
                }`}
              >
                <Wand2 className="size-3.5" />
                Voz & Personalización
                {prefs?.onboardingCompleted ? (
                  <span className="size-1.5 rounded-full bg-emerald-400" />
                ) : (
                  <span className="size-1.5 rounded-full bg-amber-400 animate-pulse" />
                )}
              </button>

              <button
                type="button"
                onClick={() => setTabOverride("channels")}
                className={`inline-flex items-center gap-1.5 rounded-lg px-3 py-1.5 text-xs font-semibold transition ${
                  activeTab === "channels"
                    ? "bg-white text-black shadow-sm"
                    : "text-zinc-400 hover:text-white"
                }`}
              >
                <ShieldCheck className="size-3.5" />
                Canales & Cuentas
                {allChannelsConfigured ? (
                  <span className="size-1.5 rounded-full bg-emerald-400" />
                ) : (
                  <span className="size-1.5 rounded-full bg-amber-400 animate-pulse" />
                )}
              </button>
            </div>

            {/* Logout Button */}
            <button
              type="button"
              onClick={() => {
                logout();
                router.push("/login");
              }}
              className="inline-flex items-center gap-1.5 rounded-xl border border-white/10 bg-white/5 px-3 py-2 text-xs font-semibold text-zinc-400 hover:bg-rose-500/10 hover:border-rose-500/30 hover:text-rose-300 transition"
              title="Cerrar sesión"
            >
              <LogOut className="size-3.5" />
              <span className="hidden sm:inline">Salir</span>
            </button>
          </div>
        </header>

        {/* Status & Subhead Bar */}
        <section className="py-6 flex flex-wrap items-center justify-between gap-3">
          <div className="inline-flex items-center gap-2 rounded-full border border-white/10 bg-white/[0.03] px-3 py-1.5 text-xs text-zinc-400">
            <Radio className="size-3.5 text-emerald-400 animate-pulse" />
            Espacio de trabajo seguro y multi-inquilino · WhatsApp + GitHub + LinkedIn
          </div>

          {/* Quick Active Voice Pill */}
          {prefs && (
            <div className="flex items-center gap-2 text-xs">
              <span className="text-zinc-500">Voz Activa:</span>
              <span className="inline-flex items-center gap-1 rounded-full border border-emerald-500/30 bg-emerald-500/10 px-2.5 py-1 text-emerald-300 font-mono text-[11px]">
                <Sparkles className="size-3" />
                {prefs.tone} ({prefs.language.toUpperCase()})
              </span>
            </div>
          )}
        </section>

        {/* Tab View: CHANNELS & ACCOUNTS SETTINGS */}
        {activeTab === "channels" ? (
          <section className="pb-16">
            <AccountsSettings userId={userId} />
          </section>
        ) : activeTab === "onboarding" ? (
          /* Tab View: ONBOARDING WIZARD */
          <section className="pb-16">
            <OnboardingWizard
              userId={userId}
              onComplete={() => setTabOverride("dashboard")}
            />
          </section>
        ) : (
          /* Tab View: LIVE DASHBOARD */
          <>
            {/* Quick Metrics Bar */}
            <div className="mb-6 grid gap-3 grid-cols-2 sm:grid-cols-4">
              <div className="rounded-2xl border border-white/10 bg-white/[0.02] p-4 flex flex-col justify-between">
                <span className="text-xs text-zinc-400">Historias Detectadas</span>
                <div className="mt-2 flex items-baseline gap-2">
                  <span className="text-2xl font-bold text-white">{stories?.length ?? 0}</span>
                  <span className="text-[10px] text-emerald-400 font-mono">IA clusters</span>
                </div>
              </div>

              <div className="rounded-2xl border border-white/10 bg-white/[0.02] p-4 flex flex-col justify-between">
                <span className="text-xs text-zinc-400">Borradores Generados</span>
                <div className="mt-2 flex items-baseline gap-2">
                  <span className="text-2xl font-bold text-white">{posts?.length ?? 0}</span>
                  <span className="text-[10px] text-zinc-500 font-mono">LinkedIn</span>
                </div>
              </div>

              <div className="rounded-2xl border border-white/10 bg-white/[0.02] p-4 flex flex-col justify-between">
                <span className="text-xs text-zinc-400">Repositorios Conectados</span>
                <div className="mt-2 flex items-baseline gap-2">
                  <span className="text-2xl font-bold text-white">{repositories?.length ?? 0}</span>
                  <span className="text-[10px] text-zinc-500 font-mono">GitHub</span>
                </div>
              </div>

              <div className="rounded-2xl border border-white/10 bg-white/[0.02] p-4 flex flex-col justify-between">
                <span className="text-xs text-zinc-400">Personalización de Voz</span>
                <div className="mt-2 flex items-center gap-1.5">
                  {prefs?.onboardingCompleted ? (
                    <span className="inline-flex items-center gap-1 text-xs font-semibold text-emerald-300">
                      <CheckCircle2 className="size-3.5 text-emerald-400" /> Activa & Calibrada
                    </span>
                  ) : (
                    <button
                      type="button"
                      onClick={() => setTabOverride("onboarding")}
                      className="text-xs font-semibold text-amber-400 hover:underline"
                    >
                      Calibrar Voz →
                    </button>
                  )}
                </div>
              </div>
            </div>

            {/* Historical Project Digest */}
            <HistoricalDigestLauncher repositories={repositories} />

            {/* Pipeline Overview */}
            <div className="mb-8 grid gap-3 sm:grid-cols-2 lg:grid-cols-4">
              {stages.map((stage) => {
                const Icon = stage.icon;
                return (
                  <div
                    key={stage.label}
                    className="flex flex-col justify-between rounded-2xl border border-white/10 bg-white/[0.025] p-4"
                  >
                    <div className="flex items-center justify-between">
                      <div className="flex size-8 items-center justify-center rounded-lg bg-white/10 text-white">
                        <Icon className="size-4" />
                      </div>
                      <CheckCircle2 className="size-4 text-emerald-400" />
                    </div>
                    <div className="mt-4">
                      <p className="text-sm font-semibold text-white">{stage.label}</p>
                      <p className="text-xs text-zinc-400 mt-0.5">{stage.detail}</p>
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
                    <Sparkles className="size-4 text-zinc-300" />
                    <h2 className="text-lg font-semibold tracking-tight text-white">Narrativa & Borrador de Autor</h2>
                  </div>
                  <span className="font-mono text-xs text-zinc-500">Reactivo · Convex Sync</span>
                </div>

                <StoryDraftViewer userId={userId} />
              </div>

              {/* Right Column: Live Activity Stream */}
              <div className="lg:sticky lg:top-8 self-start space-y-4">
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <Activity className="size-4 text-emerald-400" />
                    <h2 className="text-lg font-semibold tracking-tight text-white">Actividad en Vivo</h2>
                  </div>
                  <span className="font-mono text-xs text-zinc-500">Convex Sync</span>
                </div>

                <div className="rounded-3xl border border-white/10 bg-white/[0.035] p-5 shadow-xl">
                  <LiveActivityStream userId={userId} />
                </div>
              </div>
            </section>
          </>
        )}

        {/* Footer */}
        <footer className="flex flex-col gap-2 border-t border-white/10 py-6 text-xs text-zinc-500 sm:flex-row sm:items-center sm:justify-between">
          <span>LaborIN · Proof of Work & Story Intelligence</span>
          <span>LinkedIn + Kapso WhatsApp + Convex + FastAPI + Next.js</span>
        </footer>
      </div>
    </main>
  );
}

export default function DashboardPage() {
  return (
    <Suspense
      fallback={
        <div className="min-h-screen bg-black flex items-center justify-center text-white">
          <div className="size-8 rounded-full border-2 border-white/20 border-t-white animate-spin" />
        </div>
      }
    >
      <DashboardContent />
    </Suspense>
  );
}
