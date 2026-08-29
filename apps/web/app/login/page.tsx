"use client";

import { useState, useEffect, Suspense } from "react";
import { useRouter, useSearchParams } from "next/navigation";
import Link from "next/link";
import { ArrowRight, CheckCircle2, Lock, Phone, Sparkles } from "lucide-react";
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
  const { isAuthenticated, isLoading, loginWithPhone } = useAuth();
  const router = useRouter();
  const searchParams = useSearchParams();

  const [phone, setPhone] = useState("+51");
  const [displayName, setDisplayName] = useState("");
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [errorMsg, setErrorMsg] = useState("");

  const redirectUrl = searchParams.get("redirect") || "/dashboard";

  useEffect(() => {
    if (!isLoading && isAuthenticated) {
      router.replace(redirectUrl);
    }
  }, [isAuthenticated, isLoading, router, redirectUrl]);

  const handlePhoneSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!phone || phone.trim().length < 8) {
      setErrorMsg("Por favor ingresa un número de WhatsApp válido con código de país (ej. +51999888777).");
      return;
    }
    setIsSubmitting(true);
    setErrorMsg("");
    try {
      await loginWithPhone(phone, displayName || undefined);
      router.push(redirectUrl);
    } catch (err: unknown) {
      const message = err instanceof Error ? err.message : "Error al iniciar sesión";
      setErrorMsg(message);
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="relative min-h-screen bg-[#000000] text-[#ededed] font-sans antialiased flex flex-col justify-between selection:bg-white selection:text-black">
      {/* Background Glow */}
      <div className="fixed inset-0 pointer-events-none z-0 overflow-hidden">
        <div className="absolute -top-[25%] left-1/2 -translate-x-1/2 w-[700px] h-[500px] bg-white/[0.04] blur-[140px] rounded-full" />
      </div>

      {/* Header */}
      <header className="relative z-10 w-full max-w-5xl mx-auto px-6 py-8 flex items-center justify-between">
        <Link href="/" className="flex items-center gap-2.5 group">
          <div className="size-8 rounded-xl bg-white text-black flex items-center justify-center font-bold font-mono text-sm tracking-tighter group-hover:scale-105 transition shadow-lg shadow-white/20">
            L
          </div>
          <span className="font-semibold text-lg tracking-tight text-white">Laborin</span>
        </Link>

        <Link
          href="/"
          className="text-xs text-zinc-400 hover:text-white transition"
        >
          Volver a la portada
        </Link>
      </header>

      {/* Main Login Card */}
      <main className="relative z-10 flex-1 flex items-center justify-center px-4 py-8">
        <div className="w-full max-w-md rounded-3xl border border-white/10 bg-[#09090b]/90 p-8 backdrop-blur-2xl shadow-2xl shadow-black/80">
          <div className="text-center">
            <div className="inline-flex size-12 items-center justify-center rounded-2xl bg-white/10 text-white mb-4 border border-white/10 shadow-inner">
              <Lock className="size-5" />
            </div>
            <h1 className="text-2xl font-bold tracking-tight text-white">
              Inicia sesión en Laborin
            </h1>
            <p className="mt-2 text-xs text-zinc-400 leading-relaxed">
              Accede a tu espacio de trabajo para sincronizar tus commits, configurar tu voz editorial y aprobar historias por WhatsApp.
            </p>
          </div>

          {errorMsg && (
            <div className="mt-6 rounded-2xl border border-rose-500/20 bg-rose-500/10 p-3 text-xs text-rose-300">
              {errorMsg}
            </div>
          )}

          {/* 1-Click OAuth Buttons */}
          <div className="mt-8 space-y-3">
            <a
              href="https://laborin.meowlab.tech/auth/github/login"
              className="flex w-full items-center justify-center gap-3 rounded-2xl border border-white/20 bg-white/5 px-4 py-3 text-sm font-semibold text-white hover:bg-white/10 hover:border-white/40 transition shadow-sm"
            >
              <GithubIcon className="size-5" />
              Continuar con GitHub
            </a>

            <a
              href="https://laborin.meowlab.tech/auth/linkedin/login"
              className="flex w-full items-center justify-center gap-3 rounded-2xl border border-sky-500/30 bg-sky-500/10 px-4 py-3 text-sm font-semibold text-sky-300 hover:bg-sky-500/20 transition shadow-sm"
            >
              <LinkedinIcon className="size-5" />
              Continuar con LinkedIn
            </a>
          </div>

          <div className="relative my-6 flex items-center justify-center">
            <div className="absolute inset-0 flex items-center">
              <div className="w-full border-t border-white/10" />
            </div>
            <span className="relative bg-[#09090b] px-3 font-mono text-[10px] uppercase text-zinc-500 tracking-wider">
              O con tu número de WhatsApp
            </span>
          </div>

          {/* WhatsApp Direct Phone Login */}
          <form onSubmit={handlePhoneSubmit} className="space-y-4">
            <div>
              <label className="block text-xs font-medium text-zinc-300">
                Tu número de WhatsApp (para aprobaciones)
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

            <div>
              <label className="block text-xs font-medium text-zinc-300">
                Nombre de Desarrollador / Display Name <span className="text-zinc-500">(opcional)</span>
              </label>
              <input
                type="text"
                value={displayName}
                onChange={(e) => setDisplayName(e.target.value)}
                placeholder="ej: Diogo Fabricio"
                className="mt-1.5 w-full rounded-2xl border border-white/10 bg-black/40 px-4 py-2.5 text-sm text-white placeholder-zinc-500 focus:border-white/30 focus:outline-none"
              />
            </div>

            <button
              type="submit"
              disabled={isSubmitting}
              className="mt-2 flex w-full items-center justify-center gap-2 rounded-2xl bg-white px-5 py-3 text-sm font-bold text-black hover:bg-zinc-200 transition shadow-lg shadow-white/10 disabled:opacity-50"
            >
              {isSubmitting ? "Ingresando..." : "Entrar a mi Espacio de Trabajo"}
              <ArrowRight className="size-4" />
            </button>
          </form>

          {/* Feature Badges */}
          <div className="mt-8 grid grid-cols-2 gap-2 border-t border-white/10 pt-6 text-[11px] text-zinc-400">
            <div className="flex items-center gap-1.5">
              <CheckCircle2 className="size-3.5 text-emerald-400" />
              <span>Espacio 100% aislado</span>
            </div>
            <div className="flex items-center gap-1.5">
              <Sparkles className="size-3.5 text-emerald-400" />
              <span>Diffs a Historias</span>
            </div>
          </div>
        </div>
      </main>

      {/* Footer */}
      <footer className="relative z-10 w-full max-w-5xl mx-auto px-6 py-6 text-center text-xs text-zinc-600">
        © 2026 Laborin. Proof of Work Content Automation.
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
