"use client";

import { useState } from "react";
import { useMutation, useQuery } from "convex/react";
import {
  Check,
  CheckCircle2,
  ExternalLink,
  GitBranch,
  MessageSquare,
  Phone,
  Plus,
  Radio,
  Save,
  ShieldCheck,
  User,
} from "lucide-react";
import { api } from "@convex/api";
import type { Id } from "@convex/dataModel";

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

type AccountsSettingsProps = {
  userId: Id<"users">;
};

export function AccountsSettings({ userId }: AccountsSettingsProps) {
  const user = useQuery(api.users.getById, { userId });
  const linkedinAccount = useQuery(api.socialAccounts.getByUserAndProvider, {
    userId,
    provider: "linkedin",
  });
  const repositories = useQuery(api.repositories.listForUser, { userId });

  const updateUserProfile = useMutation(api.users.updateProfile);
  const getOrCreateRepo = useMutation(api.repositories.getOrCreateForUser);

  // Form states
  const [editingPhone, setEditingPhone] = useState(false);
  const [phoneValue, setPhoneValue] = useState("");
  const [displayNameValue, setDisplayNameValue] = useState("");
  const [newRepoInput, setNewRepoInput] = useState("");
  const [savingProfile, setSavingProfile] = useState(false);
  const [addingRepo, setAddingRepo] = useState(false);
  const [saveSuccessMsg, setSaveSuccessMsg] = useState("");

  const handleSaveProfile = async () => {
    setSavingProfile(true);
    try {
      await updateUserProfile({
        userId,
        whatsappPhone: phoneValue.trim() || undefined,
        displayName: displayNameValue.trim() || undefined,
      });
      setEditingPhone(false);
      setSaveSuccessMsg("Perfil actualizado correctamente");
      setTimeout(() => setSaveSuccessMsg(""), 3000);
    } catch (err) {
      console.error("Error updating profile:", err);
    } finally {
      setSavingProfile(false);
    }
  };

  const handleAddRepo = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!newRepoInput.trim()) return;
    setAddingRepo(true);
    try {
      await getOrCreateRepo({
        userId,
        fullName: newRepoInput.trim(),
      });
      setNewRepoInput("");
      setSaveSuccessMsg("Repositorio agregado");
      setTimeout(() => setSaveSuccessMsg(""), 3000);
    } catch (err) {
      console.error("Error adding repo:", err);
    } finally {
      setAddingRepo(false);
    }
  };

  return (
    <div className="space-y-6">
      {/* Header Banner */}
      <div className="flex flex-col gap-2 border-b border-white/10 pb-6 sm:flex-row sm:items-center sm:justify-between">
        <div>
          <h2 className="text-xl font-bold tracking-tight text-white flex items-center gap-2">
            <ShieldCheck className="size-5 text-emerald-400" />
            Canales y Perfiles Conectados
          </h2>
          <p className="text-xs text-zinc-400 mt-1">
            Estado en tiempo real de tus conexiones de WhatsApp, GitHub y LinkedIn.
          </p>
        </div>

        {saveSuccessMsg && (
          <div className="inline-flex items-center gap-1.5 rounded-full border border-emerald-500/30 bg-emerald-500/10 px-3 py-1 font-mono text-xs text-emerald-300">
            <CheckCircle2 className="size-3.5" />
            {saveSuccessMsg}
          </div>
        )}
      </div>

      {/* 3 Channels Grid */}
      <div className="grid gap-6 lg:grid-cols-3">
        {/* 1. WHATSAPP CHANNEL */}
        <div className="rounded-3xl border border-emerald-500/30 bg-[#09090b]/90 p-5 sm:p-6 backdrop-blur-xl shadow-xl flex flex-col justify-between">
          <div>
            <div className="flex items-center justify-between">
              <div className="flex size-10 items-center justify-center rounded-2xl bg-emerald-500/20 text-emerald-400">
                <Phone className="size-5" />
              </div>
              {user?.whatsappPhone ? (
                <span className="inline-flex items-center gap-1 rounded-full border border-emerald-500/40 bg-emerald-500/20 px-2.5 py-1 font-mono text-[10px] text-emerald-300">
                  <span className="size-1.5 rounded-full bg-emerald-400 animate-pulse" />
                  Activo / Kapso
                </span>
              ) : (
                <span className="rounded-full border border-amber-500/40 bg-amber-500/20 px-2.5 py-1 font-mono text-[10px] text-amber-300">
                  No configurado
                </span>
              )}
            </div>

            <h3 className="mt-4 text-base font-semibold text-white">1. WhatsApp (Kapso Bot)</h3>
            <p className="text-xs text-zinc-400 mt-1 leading-relaxed">
              Número donde recibes los borradores generados para aprobar o solicitar revisiones con IA.
            </p>

            {/* MANDATORY VALIDATION BOT BUTTON */}
            <div className="mt-4 rounded-2xl border border-emerald-500/30 bg-emerald-950/30 p-3.5 space-y-2.5">
              <p className="text-[11px] text-emerald-200 leading-snug">
                👉 <strong>Paso obligatorio de validación:</strong> Debes enviarle un primer mensaje a nuestro bot para abrir la sesión de 24h.
              </p>
              <a
                href="https://wa.me/12084415504?text=Hola%20LaborIN,%20quiero%20activar%20mi%20cuenta"
                target="_blank"
                rel="noopener noreferrer"
                className="inline-flex w-full items-center justify-center gap-2 rounded-xl bg-emerald-400 px-3.5 py-2.5 text-xs font-bold text-black hover:bg-emerald-300 transition shadow-lg shadow-emerald-400/20"
              >
                <MessageSquare className="size-4" />
                Hablar al +1 (208) 441-5504
              </a>
            </div>

            <div className="mt-4 rounded-2xl border border-white/10 bg-white/[0.02] p-3.5">
              <span className="text-[10px] font-mono uppercase tracking-wider text-zinc-500 block">
                Tu Número Registrado
              </span>
              <p className="font-mono text-sm font-semibold text-emerald-300 mt-0.5">
                {user?.whatsappPhone || "Sin número registrado"}
              </p>
              <span className="text-[10px] font-mono uppercase tracking-wider text-zinc-500 block mt-2">
                Nombre de Autor
              </span>
              <p className="text-xs text-white font-medium">
                {user?.displayName || "Desarrollador"}
              </p>
            </div>
          </div>

          <div className="mt-6 pt-4 border-t border-white/10">
            {editingPhone ? (
              <div className="space-y-3">
                <div>
                  <label className="block text-[11px] font-medium text-zinc-400">
                    Nuevo número de WhatsApp
                  </label>
                  <input
                    type="tel"
                    value={phoneValue || user?.whatsappPhone || ""}
                    onChange={(e) => setPhoneValue(e.target.value)}
                    placeholder="+51999888777"
                    className="mt-1 w-full rounded-xl border border-emerald-500/30 bg-black/60 px-3 py-2 text-xs font-mono text-white focus:outline-none"
                  />
                </div>
                <div>
                  <label className="block text-[11px] font-medium text-zinc-400">
                    Nombre a mostrar
                  </label>
                  <input
                    type="text"
                    value={displayNameValue || user?.displayName || ""}
                    onChange={(e) => setDisplayNameValue(e.target.value)}
                    placeholder="Diogo Fabricio"
                    className="mt-1 w-full rounded-xl border border-white/10 bg-black/60 px-3 py-2 text-xs text-white focus:outline-none"
                  />
                </div>
                <div className="flex gap-2">
                  <button
                    type="button"
                    onClick={handleSaveProfile}
                    disabled={savingProfile}
                    className="flex-1 inline-flex items-center justify-center gap-1 rounded-xl bg-emerald-400 px-3 py-2 text-xs font-bold text-black hover:bg-emerald-300 transition"
                  >
                    <Save className="size-3.5" />
                    {savingProfile ? "Guardando..." : "Guardar"}
                  </button>
                  <button
                    type="button"
                    onClick={() => setEditingPhone(false)}
                    className="rounded-xl border border-white/10 bg-white/5 px-3 py-2 text-xs text-zinc-400 hover:text-white"
                  >
                    Cancelar
                  </button>
                </div>
              </div>
            ) : (
              <button
                type="button"
                onClick={() => {
                  setPhoneValue(user?.whatsappPhone || "");
                  setDisplayNameValue(user?.displayName || "");
                  setEditingPhone(true);
                }}
                className="inline-flex w-full items-center justify-center gap-1.5 rounded-xl border border-white/20 bg-white/5 px-3 py-2.5 text-xs font-semibold text-white hover:bg-white/10 transition"
              >
                Modificar mi número o nombre
              </button>
            )}
          </div>
        </div>

        {/* 2. GITHUB CHANNEL */}
        <div className="rounded-3xl border border-white/10 bg-[#09090b]/90 p-5 sm:p-6 backdrop-blur-xl shadow-xl flex flex-col justify-between">
          <div>
            <div className="flex items-center justify-between">
              <div className="flex size-10 items-center justify-center rounded-2xl bg-white/10 text-white">
                <GithubIcon className="size-5" />
              </div>
              {repositories && repositories.length > 0 ? (
                <span className="inline-flex items-center gap-1 rounded-full border border-emerald-500/40 bg-emerald-500/20 px-2.5 py-1 font-mono text-[10px] text-emerald-300">
                  <Check className="size-3" />
                  {repositories.length} {repositories.length === 1 ? "Repo" : "Repos"}
                </span>
              ) : (
                <span className="rounded-full border border-white/20 bg-white/10 px-2.5 py-1 font-mono text-[10px] text-zinc-400">
                  Sin repos
                </span>
              )}
            </div>

            <h3 className="mt-4 text-base font-semibold text-white">2. GitHub (Commits & Repos)</h3>
            <p className="text-xs text-zinc-400 mt-1 leading-relaxed">
              Monitorea los eventos `push` para extraer historias basadas en tus cambios de código reales.
            </p>

            {/* Repositories List */}
            <div className="mt-5 space-y-2 max-h-40 overflow-y-auto pr-1">
              {repositories && repositories.length > 0 ? (
                repositories.map((repo: { _id: string; fullName: string; defaultBranch?: string }) => (
                  <div
                    key={repo._id}
                    className="flex items-center justify-between rounded-xl border border-white/10 bg-white/[0.02] px-3 py-2 text-xs"
                  >
                    <div className="flex items-center gap-2 truncate">
                      <GitBranch className="size-3.5 text-zinc-400 shrink-0" />
                      <span className="font-mono text-white truncate">{repo.fullName}</span>
                    </div>
                    <span className="font-mono text-[10px] text-emerald-400 shrink-0 ml-2">
                      {repo.defaultBranch || "main"}
                    </span>
                  </div>
                ))
              ) : (
                <p className="text-xs text-zinc-500 font-mono py-2">
                  No hay repositorios vinculados aún.
                </p>
              )}
            </div>

            {/* Quick Add Repo Form */}
            <form onSubmit={handleAddRepo} className="mt-3 flex gap-2">
              <input
                type="text"
                value={newRepoInput}
                onChange={(e) => setNewRepoInput(e.target.value)}
                placeholder="usuario/repositorio"
                className="flex-1 rounded-xl border border-white/10 bg-black/60 px-3 py-1.5 text-xs font-mono text-white placeholder-zinc-600 focus:outline-none"
              />
              <button
                type="submit"
                disabled={addingRepo}
                className="rounded-xl border border-white/20 bg-white/10 px-3 py-1.5 text-xs font-semibold text-white hover:bg-white/20 disabled:opacity-50"
              >
                <Plus className="size-3.5" />
              </button>
            </form>
          </div>

          <div className="mt-6 pt-4 border-t border-white/10">
            <a
              href="https://laborin.meowlab.tech/auth/github/login"
              className="inline-flex w-full items-center justify-center gap-1.5 rounded-xl border border-white/20 bg-white/10 px-3 py-2.5 text-xs font-semibold text-white hover:bg-white/20 transition"
            >
              <ExternalLink className="size-3.5" />
              Conectar o Re-instalar GitHub App
            </a>
          </div>
        </div>

        {/* 3. LINKEDIN CHANNEL */}
        <div className="rounded-3xl border border-white/10 bg-[#09090b]/90 p-5 sm:p-6 backdrop-blur-xl shadow-xl flex flex-col justify-between">
          <div>
            <div className="flex items-center justify-between">
              <div className="flex size-10 items-center justify-center rounded-2xl bg-sky-500/20 text-sky-400">
                <LinkedinIcon className="size-5" />
              </div>
              {linkedinAccount ? (
                <span className="inline-flex items-center gap-1 rounded-full border border-emerald-500/40 bg-emerald-500/20 px-2.5 py-1 font-mono text-[10px] text-emerald-300">
                  <Check className="size-3" />
                  Conectado
                </span>
              ) : (
                <span className="rounded-full border border-amber-500/40 bg-amber-500/20 px-2.5 py-1 font-mono text-[10px] text-amber-300">
                  Pendiente
                </span>
              )}
            </div>

            <h3 className="mt-4 text-base font-semibold text-white">3. LinkedIn (Publicación)</h3>
            <p className="text-xs text-zinc-400 mt-1 leading-relaxed">
              Permiso OAuth `w_member_social` para publicar en tu perfil profesional únicamente tras tu visto bueno.
            </p>

            <div className="mt-5 rounded-2xl border border-white/10 bg-white/[0.02] p-3.5">
              <span className="text-[10px] font-mono uppercase tracking-wider text-zinc-500 block">
                Estado de Autorización
              </span>
              <p className="text-xs font-semibold text-white mt-0.5">
                {linkedinAccount ? "Token Cifrado y Activo" : "Requiere Autorización OAuth"}
              </p>
              {linkedinAccount?.authorUrn && (
                <>
                  <span className="text-[10px] font-mono uppercase tracking-wider text-zinc-500 block mt-2">
                    Author URN
                  </span>
                  <p className="font-mono text-[11px] text-sky-300 truncate">
                    {linkedinAccount.authorUrn}
                  </p>
                </>
              )}
            </div>
          </div>

          <div className="mt-6 pt-4 border-t border-white/10">
            <a
              href="https://laborin.meowlab.tech/auth/linkedin/login"
              className={`inline-flex w-full items-center justify-center gap-1.5 rounded-xl px-3 py-2.5 text-xs font-semibold transition ${
                linkedinAccount
                  ? "border border-white/20 bg-white/5 text-zinc-300 hover:bg-white/10"
                  : "border border-sky-500/30 bg-sky-500/20 text-sky-300 hover:bg-sky-500/30"
              }`}
            >
              <ExternalLink className="size-3.5" />
              {linkedinAccount ? "Re-conectar Cuenta de LinkedIn" : "Conectar LinkedIn Ahora"}
            </a>
          </div>
        </div>
      </div>

      {/* Account / Tenant Info Footer */}
      <div className="rounded-2xl border border-white/10 bg-white/[0.02] p-4 flex flex-col sm:flex-row sm:items-center sm:justify-between text-xs text-zinc-400 gap-2">
        <div className="flex items-center gap-2">
          <User className="size-4 text-zinc-300" />
          <span>Tenant ID: <code className="font-mono text-white">{userId}</code></span>
        </div>
        <div className="flex items-center gap-2">
          <Radio className="size-3.5 text-emerald-400 animate-pulse" />
          <span>Sincronización Convex Reactiva Activa</span>
        </div>
      </div>
    </div>
  );
}
