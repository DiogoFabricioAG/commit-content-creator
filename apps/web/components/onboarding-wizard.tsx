"use client";

import { useState } from "react";
import { useMutation, useQuery } from "convex/react";
import {
  ArrowLeft,
  ArrowRight,
  Check,
  CheckCircle2,
  ExternalLink,
  Phone,
  ShieldAlert,
  Wand2,
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

type OnboardingWizardProps = {
  userId?: Id<"users">;
  onComplete?: () => void;
};


export function OnboardingWizard({ userId, onComplete }: OnboardingWizardProps) {
  const [step, setStep] = useState(1);

  // Queries
  const defaultUser = useQuery(api.users.getByWhatsappPhone, {
    whatsappPhone: "+51999888777",
  });
  const activeUserId = userId ?? defaultUser?._id;

  const existingPrefs = useQuery(
    api.preferences.getForUser,
    activeUserId ? { userId: activeUserId } : "skip",
  );

  const linkedinAccount = useQuery(
    api.socialAccounts.getByUserAndProvider,
    activeUserId ? { userId: activeUserId, provider: "linkedin" } : "skip",
  );

  const repositories = useQuery(
    api.repositories.listForUser,
    activeUserId ? { userId: activeUserId } : "skip",
  );

  // Mutations
  const savePreferences = useMutation(api.preferences.save);
  const updateUserProfile = useMutation(api.users.updateProfile);
  const getOrCreateRepo = useMutation(api.repositories.getOrCreateForUser);

  // Overrides
  const [overridePhone, setOverridePhone] = useState<string | null>(null);
  const [overrideName, setOverrideName] = useState<string | null>(null);
  const [overrideRepo, setOverrideRepo] = useState<string | null>(null);
  const [overrideRole, setOverrideRole] = useState<string | null>(null);
  const [overrideLanguage, setOverrideLanguage] = useState<"es" | "en" | "pt" | null>(null);
  const [overrideTone, setOverrideTone] = useState<
    "humble_builder" | "deep_technical" | "direct_minimal" | "storyteller" | null
  >(null);
  const [overrideTechnicalLevel, setOverrideTechnicalLevel] = useState<"high" | "medium" | "accessible" | null>(null);
  const [overrideTargetAudience, setOverrideTargetAudience] = useState<
    "senior_engineers" | "tech_founders" | "recruiters" | "general_tech" | null
  >(null);
  const [overridePostLength, setOverridePostLength] = useState<"concise" | "standard" | "deep_dive" | null>(null);
  const [overrideAvoidWords, setOverrideAvoidWords] = useState<string[] | null>(null);
  const [newAvoidWord, setNewAvoidWord] = useState("");
  const [overridePreferredCTA, setOverridePreferredCTA] = useState<
    "discussion_question" | "github_link" | "lesson_takeaway" | "none" | null
  >(null);
  const [overrideHashtags, setOverrideHashtags] = useState<string[] | null>(null);
  const [overrideAutoPublish, setOverrideAutoPublish] = useState<boolean | null>(null);
  const [saving, setSaving] = useState(false);
  const [savedSuccess, setSavedSuccess] = useState(false);

  // Effective Values
  const whatsappPhone = overridePhone ?? defaultUser?.whatsappPhone ?? "+51999888777";
  const displayName = overrideName ?? defaultUser?.displayName ?? "Lead Developer";
  const repoFullName = overrideRepo ?? repositories?.[0]?.fullName ?? "owner/my-awesome-project";
  const roleTitle = overrideRole ?? existingPrefs?.roleTitle ?? "Senior Backend Engineer";
  const language = overrideLanguage ?? existingPrefs?.language ?? "es";
  const tone = overrideTone ?? existingPrefs?.tone ?? "humble_builder";
  const technicalLevel = overrideTechnicalLevel ?? existingPrefs?.technicalLevel ?? "high";
  const targetAudience = overrideTargetAudience ?? existingPrefs?.targetAudience ?? "senior_engineers";
  const postLength = overridePostLength ?? existingPrefs?.postLength ?? "standard";
  const avoidWords: string[] =
    overrideAvoidWords ??
    existingPrefs?.avoidWords ??
    ["revolucionario", "game-changer", "mágico", "secreto", "infalible"];
  const preferredCTA = overridePreferredCTA ?? existingPrefs?.preferredCTA ?? "discussion_question";
  const hashtags: string[] =
    overrideHashtags ?? existingPrefs?.hashtags ?? ["#SoftwareEngineering", "#Architecture", "#ProofOfWork"];
  const autoPublish = overrideAutoPublish ?? existingPrefs?.autoPublish ?? false;

  const addAvoidWord = () => {
    if (newAvoidWord.trim() && !avoidWords.includes(newAvoidWord.trim().toLowerCase())) {
      setOverrideAvoidWords([...avoidWords, newAvoidWord.trim().toLowerCase()]);
      setNewAvoidWord("");
    }
  };

  const removeAvoidWord = (w: string) => {
    setOverrideAvoidWords(avoidWords.filter((item: string) => item !== w));
  };


  const handleFinish = async () => {
    if (!activeUserId) return;
    setSaving(true);
    try {
      // 1. Update user profile and WhatsApp phone
      await updateUserProfile({
        userId: activeUserId,
        displayName,
        whatsappPhone: whatsappPhone.trim(),
      });

      // 2. Register repository if given
      if (repoFullName.trim()) {
        await getOrCreateRepo({
          userId: activeUserId,
          fullName: repoFullName.trim(),
        });
      }

      // 3. Save editorial preferences
      await savePreferences({
        userId: activeUserId,
        roleTitle,
        language,
        tone,
        targetAudience,
        technicalLevel,
        postLength,
        avoidWords,
        preferredCTA,
        hashtags,
        allowedFormats: [
          "problem_solution",
          "before_after",
          "build_log",
          "mini_case_study",
          "architecture_breakdown",
        ],
        autoPublish,
        onboardingCompleted: true,
      });

      setSavedSuccess(true);
      setTimeout(() => {
        if (onComplete) onComplete();
      }, 1200);
    } catch (err) {
      console.error("Error saving onboarding settings:", err);
    } finally {
      setSaving(false);
    }
  };

  return (
    <div className="rounded-3xl border border-white/10 bg-[#09090b]/90 p-6 sm:p-8 backdrop-blur-xl shadow-2xl">
      {/* Header & Steps Indicator */}
      <div className="flex flex-col gap-4 border-b border-white/10 pb-6 sm:flex-row sm:items-center sm:justify-between">
        <div>
          <div className="inline-flex items-center gap-2 rounded-full border border-emerald-500/30 bg-emerald-500/10 px-3 py-1 text-xs font-mono text-emerald-300">
            <Wand2 className="size-3.5" />
            Configurador de Onboarding & Voz
          </div>
          <h2 className="mt-2 text-2xl font-bold tracking-tight text-white">
            Configura tu Cuenta y Voz Editorial
          </h2>
          <p className="text-xs text-zinc-400">
            Vincula tus canales, define tu WhatsApp para aprobaciones y personaliza tu estilo de publicación.
          </p>
        </div>

        {/* Step Progress */}
        <div className="flex items-center gap-2">
          {[
            { num: 1, label: "Canales" },
            { num: 2, label: "Identidad" },
            { num: 3, label: "Voz & Filtros" },
            { num: 4, label: "Confirmación" },
          ].map((s) => (
            <div
              key={s.num}
              className={`flex items-center gap-2 rounded-xl px-3 py-1.5 text-xs font-semibold transition ${
                step === s.num
                  ? "bg-white text-black font-bold shadow-lg shadow-white/20"
                  : step > s.num
                    ? "bg-emerald-500/20 text-emerald-300 border border-emerald-500/40"
                    : "bg-white/5 text-zinc-500 border border-white/10"
              }`}
            >
              <span>{step > s.num ? "✓" : s.num}</span>
              <span className="hidden md:inline">{s.label}</span>
            </div>
          ))}
        </div>
      </div>

      {/* Step Content */}
      <div className="mt-8 min-h-[360px]">
        {/* STEP 1: Conexión de Canales (GitHub, LinkedIn, WhatsApp) */}
        {step === 1 && (
          <div className="space-y-6">
            <div>
              <h3 className="text-base font-semibold text-white">1. Autenticación y Conexiones</h3>
              <p className="text-xs text-zinc-400 mt-1">
                Conecta tus cuentas para que el sistema observe tus commits, envíe los borradores por WhatsApp y publique en LinkedIn.
              </p>
            </div>

            <div className="grid gap-4 sm:grid-cols-3">
              {/* WhatsApp Card */}
              <div className="rounded-2xl border border-emerald-500/30 bg-emerald-950/10 p-4 flex flex-col justify-between">
                <div>
                  <div className="flex items-center justify-between">
                    <div className="flex size-9 items-center justify-center rounded-xl bg-emerald-500/20 text-emerald-400">
                      <Phone className="size-5" />
                    </div>
                    <span className="rounded-full border border-emerald-500/40 bg-emerald-500/20 px-2 py-0.5 font-mono text-[10px] text-emerald-300">
                      Canal Requerido
                    </span>
                  </div>
                  <h4 className="mt-3 text-sm font-semibold text-white">WhatsApp (Kapso)</h4>
                  <p className="text-xs text-zinc-400 mt-1">
                    Número donde recibirás los borradores para aprobar o pedir cambios en lenguaje natural.
                  </p>
                </div>

                <div className="mt-4">
                  <label className="block text-[11px] font-medium text-zinc-300">
                    Tu número (con código de país)
                  </label>
                  <input
                    type="text"
                    value={whatsappPhone}
                    onChange={(e) => setOverridePhone(e.target.value)}
                    placeholder="+51999888777"
                    className="mt-1 w-full rounded-xl border border-emerald-500/30 bg-black/60 px-3 py-2 text-xs font-mono text-white placeholder-zinc-500 focus:border-emerald-400 focus:outline-none"
                  />
                </div>
              </div>

              {/* GitHub Card */}
              <div className="rounded-2xl border border-white/10 bg-black/40 p-4 flex flex-col justify-between">
                <div>
                  <div className="flex items-center justify-between">
                    <div className="flex size-9 items-center justify-center rounded-xl bg-white/10 text-white">
                      <GithubIcon className="size-5" />
                    </div>
                    <span className="rounded-full border border-white/20 bg-white/10 px-2 py-0.5 font-mono text-[10px] text-zinc-300">
                      Git Observer
                    </span>
                  </div>
                  <h4 className="mt-3 text-sm font-semibold text-white">GitHub Repository</h4>
                  <p className="text-xs text-zinc-400 mt-1">
                    Repositorio donde escuchamos los eventos de `push` y extraemos los diffs.
                  </p>
                </div>

                <div className="mt-4">
                  <label className="block text-[11px] font-medium text-zinc-300">
                    Repositorio a monitorear
                  </label>
                  <input
                    type="text"
                    value={repoFullName}
                    onChange={(e) => setOverrideRepo(e.target.value)}
                    placeholder="usuario/repositorio"
                    className="mt-1 w-full rounded-xl border border-white/10 bg-black/60 px-3 py-2 text-xs font-mono text-white placeholder-zinc-500 focus:border-white/30 focus:outline-none"
                  />
                </div>
              </div>

              {/* LinkedIn Card */}
              <div className="rounded-2xl border border-white/10 bg-black/40 p-4 flex flex-col justify-between">
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
                      <span className="rounded-full border border-amber-500/40 bg-amber-500/20 px-2 py-0.5 font-mono text-[10px] text-amber-300">
                        Pendiente
                      </span>
                    )}
                  </div>
                  <h4 className="mt-3 text-sm font-semibold text-white">LinkedIn OAuth</h4>
                  <p className="text-xs text-zinc-400 mt-1">
                    Permiso `w_member_social` para publicar en tu perfil al dar tu aprobación.
                  </p>
                </div>


                <div className="mt-4">
                  <a
                    href="https://laborin.meowlab.tech/auth/linkedin/login"
                    target="_blank"
                    rel="noreferrer"
                    className="inline-flex w-full items-center justify-center gap-1.5 rounded-xl border border-sky-500/30 bg-sky-500/10 px-3 py-2 text-xs font-semibold text-sky-300 hover:bg-sky-500/20 transition"
                  >
                    <ExternalLink className="size-3.5" />
                    {linkedinAccount ? "Re-autenticar LinkedIn" : "Conectar LinkedIn"}
                  </a>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* STEP 2: Identidad y Rol Técnico */}
        {step === 2 && (
          <div className="space-y-6">
            <div>
              <h3 className="text-base font-semibold text-white">2. Tu Identidad Técnica</h3>
              <p className="text-xs text-zinc-400 mt-1">
                La IA adaptará el vocabulario y contexto según tu rol y especialidad técnica.
              </p>
            </div>

            <div className="grid gap-4 sm:grid-cols-2">
              <div>
                <label className="block text-xs font-medium text-zinc-300">Nombre a Mostrar</label>
                <input
                  type="text"
                  value={displayName}
                  onChange={(e) => setOverrideName(e.target.value)}
                  placeholder="ej: Diogo Fabricio"
                  className="mt-1.5 w-full rounded-xl border border-white/10 bg-black/40 px-4 py-2.5 text-sm text-white placeholder-zinc-500 focus:border-white/30 focus:outline-none"
                />
              </div>

              <div>
                <label className="block text-xs font-medium text-zinc-300">
                  Tu Rol o Título de Ingeniería
                </label>
                <input
                  type="text"
                  value={roleTitle}
                  onChange={(e) => setOverrideRole(e.target.value)}
                  placeholder="ej: Senior Backend Engineer / AI Architect"
                  className="mt-1.5 w-full rounded-xl border border-white/10 bg-black/40 px-4 py-2.5 text-sm text-white placeholder-zinc-500 focus:border-white/30 focus:outline-none"
                />
              </div>
            </div>

            <div>
              <label className="block text-xs font-medium text-zinc-300">
                Idioma Principal de tus Publicaciones
              </label>
              <div className="mt-2 grid grid-cols-3 gap-3">
                {[
                  { id: "es", label: "Español", desc: "Natural & profesional" },
                  { id: "en", label: "English", desc: "Global developer reach" },
                  { id: "pt", label: "Português", desc: "Comunidade tech" },
                ].map((item) => (
                  <button
                    key={item.id}
                    type="button"
                    onClick={() => setOverrideLanguage(item.id as "es" | "en" | "pt")}
                    className={`rounded-2xl border p-3.5 text-left transition ${
                      language === item.id
                        ? "border-white bg-white/10 text-white"
                        : "border-white/10 bg-black/30 text-zinc-400 hover:border-white/20"
                    }`}
                  >
                    <p className="text-sm font-semibold">{item.label}</p>
                    <p className="text-[11px] text-zinc-500">{item.desc}</p>
                  </button>
                ))}
              </div>
            </div>
          </div>
        )}

        {/* STEP 3: Tono, Filtro de Clichés & Hashtags */}
        {step === 3 && (
          <div className="space-y-6">
            <div>
              <h3 className="text-base font-semibold text-white">3. Tono Editorial y Reglas Anti-Hype</h3>
              <p className="text-xs text-zinc-400 mt-1">
                Garantizamos que tus publicaciones sean 100% auténticas y libres de clichés de IA.
              </p>
            </div>

            {/* Tone Selector */}
            <div>
              <label className="block text-xs font-medium text-zinc-300">Tono de Escritura</label>
              <div className="mt-2 grid gap-3 sm:grid-cols-2">
                {[
                  {
                    id: "humble_builder",
                    label: "Constructor Humilde",
                    desc: "Enfocado en lecciones aprendidas y trade-offs reales.",
                  },
                  {
                    id: "deep_technical",
                    label: "Técnico Profundo",
                    desc: "Métricas, arquitectura, diffs y decisiones de diseño.",
                  },
                  {
                    id: "direct_minimal",
                    label: "Directo & Minimalista",
                    desc: "Problema -> Solución en pocas líneas, sin rodeos.",
                  },
                  {
                    id: "storyteller",
                    label: "Narrativo / Storytelling",
                    desc: "El viaje del bug a la solución en producción.",
                  },
                ].map((item) => (
                  <button
                    key={item.id}
                    type="button"
                    onClick={() =>
                      setOverrideTone(
                        item.id as "humble_builder" | "deep_technical" | "direct_minimal" | "storyteller",
                      )
                    }
                    className={`rounded-2xl border p-3.5 text-left transition ${
                      tone === item.id
                        ? "border-white bg-white/10 text-white"
                        : "border-white/10 bg-black/30 text-zinc-400 hover:border-white/20"
                    }`}
                  >
                    <p className="text-sm font-semibold">{item.label}</p>
                    <p className="mt-1 text-xs text-zinc-400 leading-snug">{item.desc}</p>
                  </button>
                ))}
              </div>
            </div>

            {/* Audience and Technical Level */}
            <div className="grid gap-4 sm:grid-cols-3">
              <div>
                <label className="block text-xs font-medium text-zinc-300">Audiencia Objetivo</label>
                <select
                  value={targetAudience}
                  onChange={(e) =>
                    setOverrideTargetAudience(
                      e.target.value as "senior_engineers" | "tech_founders" | "recruiters" | "general_tech",
                    )
                  }
                  className="mt-1.5 w-full rounded-xl border border-white/10 bg-black/40 px-3.5 py-2 text-sm text-white focus:outline-none"
                >
                  <option value="senior_engineers">Senior Engineers & Tech Leads</option>
                  <option value="tech_founders">Founders & CTOs</option>
                  <option value="recruiters">Recruiters & Hiring Managers</option>
                  <option value="general_tech">Comunidad Tech General</option>
                </select>
              </div>

              <div>
                <label className="block text-xs font-medium text-zinc-300">Nivel Técnico</label>
                <select
                  value={technicalLevel}
                  onChange={(e) =>
                    setOverrideTechnicalLevel(e.target.value as "high" | "medium" | "accessible")
                  }
                  className="mt-1.5 w-full rounded-xl border border-white/10 bg-black/40 px-3.5 py-2 text-sm text-white focus:outline-none"
                >
                  <option value="high">Alto (Arquitectos e ingenieros)</option>
                  <option value="medium">Medio (Balance producto / código)</option>
                  <option value="accessible">Accesible (Sin jerga oscura)</option>
                </select>
              </div>

              <div>
                <label className="block text-xs font-medium text-zinc-300">Longitud del Post</label>
                <select
                  value={postLength}
                  onChange={(e) =>
                    setOverridePostLength(e.target.value as "concise" | "standard" | "deep_dive")
                  }
                  className="mt-1.5 w-full rounded-xl border border-white/10 bg-black/40 px-3.5 py-2 text-sm text-white focus:outline-none"
                >
                  <option value="concise">Conciso (100 - 150 palabras)</option>
                  <option value="standard">Estándar (150 - 250 palabras)</option>
                  <option value="deep_dive">Deep Dive (250 - 400 palabras)</option>
                </select>
              </div>
            </div>

            {/* Avoid Words & Hashtags */}
            <div>
              <div className="flex items-center gap-2">
                <ShieldAlert className="size-4 text-amber-400" />
                <label className="text-xs font-medium text-zinc-300">
                  Palabras y Clichés Prohibidos (Zero Buzzwords)
                </label>
              </div>
              <p className="mt-1 text-xs text-zinc-500">
                La IA tiene estrictamente prohibido usar estas palabras al redactar tus posts.
              </p>

              <div className="mt-3 flex flex-wrap gap-2">
                {avoidWords.map((w: string) => (
                  <span
                    key={w}
                    className="inline-flex items-center gap-1.5 rounded-lg border border-rose-500/20 bg-rose-500/10 px-2.5 py-1 text-xs text-rose-300"
                  >
                    {w}
                    <button
                      type="button"
                      onClick={() => removeAvoidWord(w)}
                      className="hover:text-rose-100 font-bold"
                    >
                      ×
                    </button>
                  </span>
                ))}
              </div>


              <div className="mt-3 flex gap-2">
                <input
                  type="text"
                  value={newAvoidWord}
                  onChange={(e) => setNewAvoidWord(e.target.value)}
                  onKeyDown={(e) => e.key === "Enter" && (e.preventDefault(), addAvoidWord())}
                  placeholder="Añadir palabra a evitar..."
                  className="rounded-xl border border-white/10 bg-black/40 px-3.5 py-2 text-xs text-white placeholder-zinc-600 focus:outline-none"
                />
                <button
                  type="button"
                  onClick={addAvoidWord}
                  className="rounded-xl border border-white/20 bg-white/10 px-3 py-2 text-xs font-semibold text-white hover:bg-white/20"
                >
                  Agregar
                </button>
              </div>
            </div>

            <div className="grid gap-4 sm:grid-cols-2">
              <div>
                <label className="block text-xs font-medium text-zinc-300">
                  Llamada a la Acción (CTA) Preferida
                </label>
                <select
                  value={preferredCTA}
                  onChange={(e) =>
                    setOverridePreferredCTA(
                      e.target.value as "discussion_question" | "github_link" | "lesson_takeaway" | "none",
                    )
                  }
                  className="mt-1.5 w-full rounded-xl border border-white/10 bg-black/40 px-3.5 py-2 text-sm text-white focus:outline-none"
                >
                  <option value="discussion_question">Pregunta para debate técnico en comentarios</option>
                  <option value="lesson_takeaway">Conclusión / Aprendizaje clave</option>
                  <option value="github_link">Enlace al repositorio de GitHub</option>
                  <option value="none">Sin CTA (Solo la historia)</option>
                </select>
              </div>

              <div>
                <label className="block text-xs font-medium text-zinc-300">
                  Hashtags Predeterminados (Separados por coma)
                </label>
                <input
                  type="text"
                  value={hashtags.join(", ")}
                  onChange={(e) =>
                    setOverrideHashtags(
                      e.target.value
                        .split(",")
                        .map((s) => s.trim())
                        .filter(Boolean),
                    )
                  }
                  placeholder="#SoftwareEngineering, #ProofOfWork"
                  className="mt-1.5 w-full rounded-xl border border-white/10 bg-black/40 px-3.5 py-2 text-sm text-white focus:outline-none"
                />
              </div>
            </div>
          </div>
        )}

        {/* STEP 4: Previsualización y Activación */}
        {step === 4 && (
          <div className="space-y-6">
            <div className="flex items-center justify-between">
              <div>
                <h3 className="text-base font-semibold text-white">4. Resumen y Previsualización</h3>
                <p className="text-xs text-zinc-400 mt-1">
                  Revisa cómo lucirá tu configuración antes de activarla.
                </p>
              </div>
              <span className="rounded-full border border-emerald-500/30 bg-emerald-500/10 px-3 py-1 font-mono text-xs text-emerald-300">
                Todo listo
              </span>
            </div>

            {/* Generated Mock Post Preview */}
            <div className="rounded-2xl border border-white/10 bg-black/50 p-4 font-mono text-xs leading-relaxed text-zinc-300">
              <p className="font-bold text-white">
                🚀 Migración de Polling a WebSockets en Tiempo Real
              </p>
              <p className="mt-2">
                Como {roleTitle}, cuando construyes una feature en vivo, la solución inicial suele ser
                polling HTTP.
              </p>
              <p className="mt-2 text-zinc-400">
                • El problema: Peticiones duplicadas y sobrecarga innecesaria en la BD.<br />
                • La solución: Arquitectura de WebSockets con eventos desacoplados.<br />
                • Resultado: Cero requests redundantes y entrega instantánea.
              </p>
              <p className="mt-2 text-zinc-400">
                {preferredCTA === "discussion_question"
                  ? "¿Cómo manejan este trade-off en sus arquitecturas?"
                  : "📌 Aprendizaje: Medir y aislar eventos antes de escalar."}
              </p>
              <p className="mt-3 text-emerald-400 font-semibold">{hashtags.join(" ")}</p>
            </div>

            {/* Channels Summary Card */}
            <div className="grid gap-3 sm:grid-cols-2 text-xs">
              <div className="rounded-2xl border border-white/10 bg-white/[0.03] p-3.5">
                <p className="font-semibold text-white flex items-center gap-1.5">
                  <Phone className="size-3.5 text-emerald-400" /> WhatsApp Destino:
                </p>
                <p className="mt-1 font-mono text-emerald-300">{whatsappPhone}</p>
              </div>

              <div className="rounded-2xl border border-white/10 bg-white/[0.03] p-3.5">
                <p className="font-semibold text-white flex items-center gap-1.5">
                  <GithubIcon className="size-3.5 text-zinc-300" /> Repo Monitoreado:
                </p>
                <p className="mt-1 font-mono text-zinc-300">{repoFullName}</p>
              </div>

            </div>

            {/* Auto Publish Toggle */}
            <div className="rounded-2xl border border-white/10 bg-white/[0.03] p-4 flex items-center justify-between">
              <div>
                <p className="text-xs font-semibold text-white">Modo de Publicación</p>
                <p className="text-[11px] text-zinc-400">
                  {autoPublish
                    ? "Auto-publicar historias con alta confianza sin esperar WhatsApp."
                    : "Siempre se te consultará por WhatsApp antes de publicar en LinkedIn."}
                </p>
              </div>
              <label className="flex items-center gap-2 cursor-pointer">
                <input
                  type="checkbox"
                  checked={autoPublish}
                  onChange={(e) => setOverrideAutoPublish(e.target.checked)}
                  className="rounded bg-black/50 border-white/20 text-emerald-500 focus:ring-0 size-4"
                />
                <span className="text-xs text-zinc-300">Auto-publicar</span>
              </label>
            </div>
          </div>
        )}
      </div>

      {/* Footer Navigation Buttons */}
      <div className="mt-8 flex items-center justify-between border-t border-white/10 pt-6">
        {step > 1 ? (
          <button
            type="button"
            onClick={() => setStep(step - 1)}
            className="inline-flex items-center gap-2 rounded-xl border border-white/10 bg-white/5 px-4 py-2.5 text-xs font-semibold text-white hover:bg-white/10"
          >
            <ArrowLeft className="size-4" /> Anterior
          </button>
        ) : (
          <div />
        )}

        {step < 4 ? (
          <button
            type="button"
            onClick={() => setStep(step + 1)}
            className="inline-flex items-center gap-2 rounded-xl bg-white px-5 py-2.5 text-xs font-bold text-black hover:bg-zinc-200 shadow-lg shadow-white/10"
          >
            Siguiente <ArrowRight className="size-4" />
          </button>
        ) : (
          <button
            type="button"
            onClick={handleFinish}
            disabled={saving || savedSuccess}
            className="inline-flex items-center gap-2 rounded-xl bg-emerald-400 px-6 py-2.5 text-xs font-bold text-black hover:bg-emerald-300 shadow-lg shadow-emerald-400/20 disabled:opacity-50"
          >
            {saving ? "Guardando..." : savedSuccess ? "¡Guardado con Éxito!" : "Guardar y Activar Canales"}
            <CheckCircle2 className="size-4" />
          </button>
        )}
      </div>
    </div>
  );
}
