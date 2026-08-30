"use client";

import { useState, useEffect, Suspense } from "react";
import { useRouter, useSearchParams } from "next/navigation";
import Link from "next/link";
import {
  ArrowRight,
  Check,
  CheckCircle2,
  ExternalLink,
  Phone,
  ShieldCheck,
  Sparkles,
  Wand2,
} from "lucide-react";
import { useMutation, useQuery } from "convex/react";
import { api } from "@convex/api";
import { useAuth } from "../../contexts/auth-context";

function GithubIcon({ className = "size-5" }: { className?: string }) {
  return (
    <svg className={className} fill="currentColor" viewBox="0 0 24 24" aria-hidden="true">
      <path
        fillRule="evenodd"
        d="M12 2C6.477 2 2 6.484 2 12.017c0 4.425 2.865 8.18 6.839 9.504.5.092.682-.217.682-.483 0-.237-.008-.868-.013-1.703-2.782.605-3.369-1.343-3.369-1.343-.454-1.158-1.11-1.466-1.11-1.466-.908-.62.069-.608.069-.608 1.003.07 1.53 1.032 1.53 1.032.892 1.53 2.341 1.088 2.91.832.092-.647.35-1.088.636-1.338-2.22-.253-4.555-1.113-4.555-4.951 0-1.093.39-1.988 1.029-2.688-.103-.253-.446-1.272.098-2.65 0 0 .84-.27 2.75 1.026A9.564 9.564 0 0112 6.844c.85.004 1.705.115 2.504.337 1.909-1.296 2.747-1.027 2.747-1.027.546 1.379.202 2.398.1 2.651.64.7 1.028 1.595 1.028 2.688 0 3.848-2.339 4.695-4.566 4.943.359.309.678.92.678 1.855 0 1.338-.012 2.419-.012 2.747 0 .268.18.58.688.482A10.019 10.019 0 0022 12.017C22 6.484 17.522 2 12 2z"
        clipRule="evenodd"
      />
    </svg>
  );
}

function LinkedinIcon({ className = "size-5" }: { className?: string }) {
  return (
    <svg className={className} fill="currentColor" viewBox="0 0 24 24" aria-hidden="true">
      <path d="M19 3a2 2 0 0 1 2 2v14a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h14m-.5 15.5v-5.3a3.26 3.26 0 0 0-3.26-3.26c-.85 0-1.84.52-2.28 1.3v-1.11h-2.79v8.37h2.79v-4.93c0-.77.62-1.4 1.39-1.4a1.4 1.4 0 0 1 1.4 1.4v4.93h2.75M6.46 8.76a1.46 1.46 0 0 0 1.46-1.46 1.46 1.46 0 1 0-2.92 0 1.46 1.46 0 0 0 1.46 1.46m1.39 9.74v-8.37H5.07v8.37h2.78z" />
    </svg>
  );
}

function LoginContent() {
  const { userId, isAuthenticated, isLoading, loginWithPhone } = useAuth();

  const router = useRouter();
  const searchParams = useSearchParams();

  const [mode, setMode] = useState<"unified" | "quick">("unified");
  const [phone, setPhone] = useState("+51");
  const [displayName, setDisplayName] = useState("");
  const [repoFullName, setRepoFullName] = useState("");
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [errorMsg, setErrorMsg] = useState("");

  const getOrCreateRepo = useMutation(api.repositories.getOrCreateForUser);

  // Queries to check status if session is active or redirected
  const linkedinAccount = useQuery(
    api.socialAccounts.getByUserAndProvider,
    userId ? { userId, provider: "linkedin" } : "skip",
  );

  const repositories = useQuery(
    api.repositories.listForUser,
    userId ? { userId } : "skip",
  );

  const redirectUrl = searchParams.get("redirect") || "/dashboard";

  useEffect(() => {
    if (!isLoading && isAuthenticated && mode === "quick") {
      router.replace(redirectUrl);
    }
  }, [isAuthenticated, isLoading, router, redirectUrl, mode]);

  const handleUnifiedSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!phone || phone.trim().length < 8) {
      setErrorMsg("Por favor ingresa tu número de WhatsApp con código de país (ej. +51999888777).");
      return;
    }
    setIsSubmitting(true);
    setErrorMsg("");
    try {
      const newUserId = await loginWithPhone(phone, displayName || undefined);
      if (repoFullName.trim()) {
        await getOrCreateRepo({
          userId: newUserId,
          fullName: repoFullName.trim(),
        });
      }
      router.push(redirectUrl);
    } catch (err: unknown) {
      const message = err instanceof Error ? err.message : "Error al configurar tu cuenta";
      setErrorMsg(message);
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="relative min-h-screen bg-[#000000] text-[#ededed] font-sans antialiased flex flex-col justify-between selection:bg-white selection:text-black">
      {/* Background Glow */}
      <div className="fixed inset-0 pointer-events-none z-0 overflow-hidden">
        <div className="absolute -top-[25%] left-1/2 -translate-x-1/2 w-[800px] h-[550px] bg-white/[0.04] blur-[150px] rounded-full" />
      </div>

      {/* Header */}
      <header className="relative z-10 w-full max-w-5xl mx-auto px-6 py-8 flex items-center justify-between">
        <Link href="/" className="flex items-center gap-2.5 group">
          <div className="size-8 rounded-xl bg-white text-black flex items-center justify-center font-bold font-mono text-sm tracking-tighter group-hover:scale-105 transition shadow-lg shadow-white/20">
            L
          </div>
          <span className="font-semibold text-lg tracking-tight text-white">LaborIN</span>
        </Link>

        <div className="flex items-center gap-4">
          <button
            type="button"
            onClick={() => setMode(mode === "unified" ? "quick" : "unified")}
            className="text-xs font-medium text-zinc-400 hover:text-white transition"
          >
            {mode === "unified" ? "Acceso rápido con WhatsApp →" : "← Configuración 3-en-1"}
          </button>
          <Link
            href="/"
            className="text-xs text-zinc-500 hover:text-zinc-300 transition hidden sm:inline"
          >
            Portada
          </Link>
        </div>
      </header>

      {/* Main Card */}
      <main className="relative z-10 flex-1 flex items-center justify-center px-4 py-6">
        <div className="w-full max-w-2xl rounded-3xl border border-white/10 bg-[#09090b]/90 p-6 sm:p-8 backdrop-blur-2xl shadow-2xl shadow-black/80">
          <div className="text-center">
            <div className="inline-flex items-center gap-2 rounded-full border border-emerald-500/30 bg-emerald-500/10 px-3 py-1 font-mono text-xs text-emerald-300 mb-3">
              <Wand2 className="size-3.5" />
              Configuración Unificada de Acceso
            </div>
            <h1 className="text-2xl sm:text-3xl font-bold tracking-tight text-white">
              {mode === "unified"
                ? "Conecta tus 3 Canales y Entra"
                : "Inicia Sesión con tu WhatsApp"}
            </h1>
            <p className="mt-2 text-xs sm:text-sm text-zinc-400 max-w-lg mx-auto leading-relaxed">
              {mode === "unified"
                ? "Vincula WhatsApp para aprobar historias, GitHub para escuchar tus commits y LinkedIn para publicar."
                : "Ingresa tu número registrado para acceder directamente a tu espacio de trabajo."}
            </p>
          </div>

          {errorMsg && (
            <div className="mt-6 rounded-2xl border border-rose-500/20 bg-rose-500/10 p-3.5 text-xs text-rose-300">
              {errorMsg}
            </div>
          )}

          {mode === "unified" ? (
            /* UNIFIED 3-IN-1 SETUP FORM */
            <form onSubmit={handleUnifiedSubmit} className="mt-8 space-y-6">
              {/* Channel 1: WhatsApp */}
              <div className="rounded-2xl border border-emerald-500/30 bg-emerald-950/15 p-4 sm:p-5">
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-3">
                    <div className="flex size-9 items-center justify-center rounded-xl bg-emerald-500/20 text-emerald-400">
                      <Phone className="size-5" />
                    </div>
                    <div>
                      <h3 className="text-sm font-semibold text-white">1. WhatsApp (Aprobaciones Kapso)</h3>
                      <p className="text-[11px] text-zinc-400">Canal donde recibirás borradores interactivos.</p>
                    </div>
                  </div>
                  <span className="rounded-full border border-emerald-500/40 bg-emerald-500/20 px-2 py-0.5 font-mono text-[10px] text-emerald-300">
                    Requerido
                  </span>
                </div>

                <div className="mt-4 grid gap-3 sm:grid-cols-2">
                  <div>
                    <label className="block text-[11px] font-medium text-zinc-300">
                      Número con código de país
                    </label>
                    <input
                      type="tel"
                      value={phone}
                      onChange={(e) => setPhone(e.target.value)}
                      placeholder="+51999888777"
                      className="mt-1 w-full rounded-xl border border-emerald-500/30 bg-black/60 px-3.5 py-2 text-xs font-mono text-white placeholder-zinc-500 focus:border-emerald-400 focus:outline-none"
                      required
                    />
                  </div>

                  <div>
                    <label className="block text-[11px] font-medium text-zinc-300">
                      Nombre a Mostrar <span className="text-zinc-500">(opcional)</span>
                    </label>
                    <input
                      type="text"
                      value={displayName}
                      onChange={(e) => setDisplayName(e.target.value)}
                      placeholder="ej: Diogo Fabricio"
                      className="mt-1 w-full rounded-xl border border-white/10 bg-black/60 px-3.5 py-2 text-xs text-white placeholder-zinc-500 focus:border-white/30 focus:outline-none"
                    />
                  </div>
                </div>

                <div className="mt-4 rounded-xl border border-emerald-500/20 bg-emerald-950/30 p-3 flex flex-col sm:flex-row sm:items-center sm:justify-between gap-2">
                  <p className="text-[11px] text-emerald-200">
                    👉 <strong>Validación inicial:</strong> Háblale a nuestro bot para abrir la sesión de 24h:
                  </p>
                  <a
                    href="https://wa.me/12084415504?text=Hola%20LaborIN,%20quiero%20activar%20mi%20cuenta"
                    target="_blank"
                    rel="noopener noreferrer"
                    className="inline-flex items-center justify-center gap-1.5 rounded-lg bg-emerald-400 px-3 py-1.5 text-xs font-bold text-black hover:bg-emerald-300 transition shrink-0"
                  >
                    Hablar al +1 (208) 441-5504
                  </a>
                </div>
              </div>

              {/* Channels 2 & 3: GitHub & LinkedIn in side-by-side grid */}
              <div className="grid gap-4 sm:grid-cols-2">

                {/* GitHub Card */}
                <div className="rounded-2xl border border-white/10 bg-white/[0.02] p-4 flex flex-col justify-between">
                  <div>
                    <div className="flex items-center justify-between">
                      <div className="flex size-9 items-center justify-center rounded-xl bg-white/10 text-white">
                        <GithubIcon className="size-5" />
                      </div>
                      {repositories && repositories.length > 0 ? (
                        <span className="inline-flex items-center gap-1 rounded-full border border-emerald-500/40 bg-emerald-500/20 px-2 py-0.5 font-mono text-[10px] text-emerald-300">
                          <Check className="size-3" /> Vinculado
                        </span>
                      ) : (
                        <span className="rounded-full border border-white/20 bg-white/10 px-2 py-0.5 font-mono text-[10px] text-zinc-300">
                          Paso 2
                        </span>
                      )}
                    </div>
                    <h3 className="mt-3 text-sm font-semibold text-white">2. GitHub (Commits & Diffs)</h3>
                    <p className="text-[11px] text-zinc-400 mt-1">
                      Monitorea eventos push y extrae historias técnicas.
                    </p>
                  </div>

                  <div className="mt-4 space-y-2">
                    <a
                      href={userId ? "/auth/github/login" : "#"}
                      onClick={(event) => {
                        if (!userId) {
                          event.preventDefault();
                          setErrorMsg("Primero crea tu espacio con WhatsApp y luego conecta GitHub.");
                        }
                      }}
                      className={`inline-flex w-full items-center justify-center gap-1.5 rounded-xl border px-3 py-2 text-xs font-semibold transition ${
                        userId
                          ? "border-white/20 bg-white/10 text-white hover:bg-white/20"
                          : "border-white/10 bg-white/5 text-zinc-500"
                      }`}
                    >
                      <ExternalLink className="size-3.5" />
                      Autenticar con GitHub
                    </a>
                    <input
                      type="text"
                      value={repoFullName}
                      onChange={(e) => setRepoFullName(e.target.value)}
                      placeholder="o escribe repo: usuario/repo"
                      className="w-full rounded-xl border border-white/10 bg-black/60 px-3 py-2 text-xs font-mono text-white placeholder-zinc-500 focus:outline-none"
                    />
                  </div>
                </div>

                {/* LinkedIn Card */}
                <div className="rounded-2xl border border-white/10 bg-white/[0.02] p-4 flex flex-col justify-between">
                  <div>
                    <div className="flex items-center justify-between">
                      <div className="flex size-9 items-center justify-center rounded-xl bg-sky-500/20 text-sky-400">
                        <LinkedinIcon className="size-5" />
                      </div>
                      {linkedinAccount ? (
                        <span className="inline-flex items-center gap-1 rounded-full border border-emerald-500/40 bg-emerald-500/20 px-2 py-0.5 font-mono text-[10px] text-emerald-300">
                          <Check className="size-3" /> Conectado
                        </span>
                      ) : (
                        <span className="rounded-full border border-sky-500/30 bg-sky-500/10 px-2 py-0.5 font-mono text-[10px] text-sky-300">
                          Paso 3
                        </span>
                      )}
                    </div>
                    <h3 className="mt-3 text-sm font-semibold text-white">3. LinkedIn (Publicación)</h3>
                    <p className="text-[11px] text-zinc-400 mt-1">
                      Permiso para publicar borradores tras tu visto bueno.
                    </p>
                  </div>

                  <div className="mt-4">
                    <a
                      href={userId ? "/auth/linkedin/login" : "#"}
                      onClick={(event) => {
                        if (!userId) {
                          event.preventDefault();
                          setErrorMsg("Primero crea tu espacio con WhatsApp y luego conecta LinkedIn.");
                        }
                      }}
                      className={`inline-flex w-full items-center justify-center gap-1.5 rounded-xl border px-3 py-2 text-xs font-semibold transition ${
                        userId
                          ? "border-sky-500/30 bg-sky-500/10 text-sky-300 hover:bg-sky-500/20"
                          : "border-white/10 bg-white/5 text-zinc-500"
                      }`}
                    >
                      <ExternalLink className="size-3.5" />
                      {linkedinAccount ? "Re-conectar LinkedIn" : "Conectar LinkedIn"}
                    </a>
                  </div>
                </div>
              </div>

              {/* Submit Button */}
              <button
                type="submit"
                disabled={isSubmitting}
                className="mt-4 flex w-full items-center justify-center gap-2 rounded-2xl bg-white px-6 py-3.5 text-sm font-bold text-black hover:bg-zinc-200 transition shadow-xl shadow-white/10 disabled:opacity-50"
              >
                {isSubmitting ? "Guardando canales..." : "Crear Espacio y Entrar al Dashboard"}
                <ArrowRight className="size-4" />
              </button>
            </form>
          ) : (
            /* QUICK WHATSAPP LOGIN FORM */
            <form onSubmit={handleUnifiedSubmit} className="mt-8 space-y-4 max-w-sm mx-auto">
              <div>
                <label className="block text-xs font-medium text-zinc-300">
                  Número de WhatsApp registrado
                </label>
                <div className="relative mt-1.5">
                  <Phone className="absolute left-3.5 top-1/2 -translate-y-1/2 size-4 text-emerald-400" />
                  <input
                    type="tel"
                    value={phone}
                    onChange={(e) => setPhone(e.target.value)}
                    placeholder="+51999888777"
                    className="w-full rounded-2xl border border-emerald-500/30 bg-black/60 pl-10 pr-4 py-2.5 text-sm font-mono text-white placeholder-zinc-500 focus:border-emerald-400 focus:outline-none"
                    required
                  />
                </div>
              </div>

              <button
                type="submit"
                disabled={isSubmitting}
                className="mt-2 flex w-full items-center justify-center gap-2 rounded-2xl bg-white px-5 py-3 text-sm font-bold text-black hover:bg-zinc-200 transition shadow-lg shadow-white/10 disabled:opacity-50"
              >
                {isSubmitting ? "Ingresando..." : "Ingresar a mi Espacio"}
                <ArrowRight className="size-4" />
              </button>
            </form>
          )}

          {/* Footer Badges */}
          <div className="mt-8 grid grid-cols-3 gap-2 border-t border-white/10 pt-6 text-[11px] text-zinc-400 text-center">
            <div className="flex items-center justify-center gap-1.5">
              <CheckCircle2 className="size-3.5 text-emerald-400" />
              <span>Multi-Tenant Seguro</span>
            </div>
            <div className="flex items-center justify-center gap-1.5">
              <ShieldCheck className="size-3.5 text-emerald-400" />
              <span>Aprobación Humana</span>
            </div>
            <div className="flex items-center justify-center gap-1.5">
              <Sparkles className="size-3.5 text-emerald-400" />
              <span>Cero Clichés de IA</span>
            </div>
          </div>
        </div>
      </main>

      {/* Footer */}
      <footer className="relative z-10 w-full max-w-5xl mx-auto px-6 py-6 text-center text-xs text-zinc-600">
        © 2026 LaborIN. Proof of Work Content Automation.
      </footer>
    </div>
  );
}

export default function LoginPage() {
  return (
    <Suspense
      fallback={
        <div className="min-h-screen bg-black flex items-center justify-center text-white">
          <div className="size-8 rounded-full border-2 border-white/20 border-t-white animate-spin" />
        </div>
      }
    >
      <LoginContent />
    </Suspense>
  );
}
