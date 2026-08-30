"use client";

import { useState } from "react";
import { History, Loader2, Sparkles } from "lucide-react";
import type { Id } from "@convex/dataModel";

type DigestRepository = {
  _id: Id<"repositories">;
  fullName: string;
  defaultBranch?: string;
};

type HistoricalDigestLauncherProps = {
  repositories: DigestRepository[] | undefined;
};

type DigestState = "idle" | "starting" | "started" | "error";

const API_BASE_URL = (process.env.NEXT_PUBLIC_API_URL || "").replace(/\/$/, "");

export function HistoricalDigestLauncher({
  repositories,
}: HistoricalDigestLauncherProps) {
  const [selectedRepositoryId, setSelectedRepositoryId] = useState("");
  const [state, setState] = useState<DigestState>("idle");
  const [message, setMessage] = useState("");

  const effectiveRepositoryId =
    selectedRepositoryId || (repositories && repositories.length > 0 ? String(repositories[0]._id) : "");

  const startDigest = async () => {
    const repository = repositories?.find(
      (item) => String(item._id) === effectiveRepositoryId,
    ) ?? repositories?.[0];
    if (!repository) {
      setState("error");
      setMessage("Conecta un repositorio antes de compilar su historia.");
      return;
    }

    setState("starting");
    setMessage("");
    try {
      const response = await fetch(`${API_BASE_URL}/api/portal/digests`, {
        method: "POST",
        credentials: "include",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          repository_id: String(repository._id),
          branch: repository.defaultBranch || "main",
          max_commits: 500,
        }),
      });
      const data = (await response.json().catch(() => ({}))) as {
        detail?: string;
        message?: string;
      };
      if (!response.ok) {
        throw new Error(data.detail || "No se pudo iniciar la compilación histórica");
      }
      setState("started");
      setMessage(
        data.message || "La lectura empezó. Recibirás una sola narrativa por WhatsApp.",
      );
    } catch (error: unknown) {
      setState("error");
      setMessage(
        error instanceof Error ? error.message : "No se pudo iniciar la compilación histórica",
      );
    }
  };

  return (
    <section className="relative mb-8 overflow-hidden rounded-3xl border border-emerald-500/30 bg-emerald-950/20 p-5 shadow-xl shadow-emerald-950/20 sm:p-6">
      <div className="pointer-events-none absolute -right-12 -top-16 size-48 rounded-full bg-emerald-400/10 blur-3xl" />
      <div className="relative flex flex-col gap-5 lg:flex-row lg:items-center lg:justify-between">
        <div className="max-w-2xl">
          <div className="flex items-center gap-2 text-emerald-300">
            <History className="size-4" />
            <span className="font-mono text-[11px] uppercase tracking-[0.18em]">
              Una historia para todo el proyecto
            </span>
          </div>
          <h2 className="mt-2 text-xl font-semibold tracking-tight text-white">
            Construir historia completa
          </h2>
          <p className="mt-1 text-sm leading-relaxed text-emerald-100/70">
            Lee los commits verificables, encuentra la evolución del proyecto y envía una sola narrativa a WhatsApp para revisarla.
          </p>
        </div>

        <div className="flex w-full flex-col gap-2 sm:flex-row lg:w-auto lg:min-w-[390px]">
          <label className="sr-only" htmlFor="digest-repository">
            Repositorio para compilar
          </label>
          <select
            id="digest-repository"
            value={selectedRepositoryId}
            onChange={(event) => setSelectedRepositoryId(event.target.value)}
            disabled={!repositories || repositories.length === 0 || state === "starting"}
            className="min-w-0 flex-1 rounded-xl border border-emerald-500/30 bg-black/50 px-3 py-2.5 text-xs font-mono text-white outline-none transition focus:border-emerald-300 disabled:cursor-not-allowed disabled:opacity-50"
          >
            {repositories && repositories.length > 0 ? (
              repositories.map((repository) => (
                <option key={String(repository._id)} value={String(repository._id)}>
                  {repository.fullName}
                </option>
              ))
            ) : (
              <option value="">Conecta un repositorio primero</option>
            )}
          </select>
          <button
            type="button"
            onClick={() => void startDigest()}
            disabled={state === "starting" || !repositories || repositories.length === 0}
            className="inline-flex items-center justify-center gap-2 rounded-xl bg-emerald-400 px-4 py-2.5 text-xs font-bold text-black transition hover:bg-emerald-300 disabled:cursor-not-allowed disabled:opacity-50"
          >
            {state === "starting" ? (
              <Loader2 className="size-3.5 animate-spin" />
            ) : (
              <Sparkles className="size-3.5" />
            )}
            {state === "starting" ? "Leyendo historial…" : "Compilar"}
          </button>
        </div>
      </div>
      {message && (
        <p
          className={`relative mt-4 border-t border-emerald-500/20 pt-3 text-xs ${
            state === "error" ? "text-rose-300" : "text-emerald-200"
          }`}
        >
          {message}
        </p>
      )}
    </section>
  );
}
