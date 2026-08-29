"use client";

import { useState } from "react";
import { useMutation, useQuery } from "convex/react";
import {
  ArrowLeft,
  ArrowRight,
  Check,
  CheckCircle2,
  ShieldAlert,
  Wand2,
} from "lucide-react";
import { api } from "@convex/api";
import type { Id } from "@convex/dataModel";


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

  // Mutations
  const savePreferences = useMutation(api.preferences.save);

  // Form State
  const [roleTitle, setRoleTitle] = useState(existingPrefs?.roleTitle ?? "Senior Software Engineer");
  const [language, setLanguage] = useState<"es" | "en" | "pt">(existingPrefs?.language ?? "es");
  const [tone, setTone] = useState<"humble_builder" | "deep_technical" | "direct_minimal" | "storyteller">(
    existingPrefs?.tone ?? "humble_builder",
  );
  const [technicalLevel, setTechnicalLevel] = useState<"high" | "medium" | "accessible">(
    existingPrefs?.technicalLevel ?? "high",
  );
  const [targetAudience, setTargetAudience] = useState<
    "senior_engineers" | "tech_founders" | "recruiters" | "general_tech"
  >(existingPrefs?.targetAudience ?? "senior_engineers");
  const [postLength, setPostLength] = useState<"concise" | "standard" | "deep_dive">(
    existingPrefs?.postLength ?? "standard",
  );
  const [avoidWords, setAvoidWords] = useState<string[]>(
    existingPrefs?.avoidWords ?? ["revolucionario", "game-changer", "mágico", "secreto", "infalible"],
  );
  const [newAvoidWord, setNewAvoidWord] = useState("");
  const [preferredCTA, setPreferredCTA] = useState<"discussion_question" | "github_link" | "lesson_takeaway" | "none">(
    existingPrefs?.preferredCTA ?? "discussion_question",
  );
  const [hashtags, setHashtags] = useState<string[]>(
    existingPrefs?.hashtags ?? ["#SoftwareEngineering", "#Architecture", "#ProofOfWork"],
  );
  const [autoPublish, setAutoPublish] = useState(existingPrefs?.autoPublish ?? false);
  const [saving, setSaving] = useState(false);

  const addAvoidWord = () => {
    if (newAvoidWord.trim() && !avoidWords.includes(newAvoidWord.trim().toLowerCase())) {
      setAvoidWords([...avoidWords, newAvoidWord.trim().toLowerCase()]);
      setNewAvoidWord("");
    }
  };

  const removeAvoidWord = (w: string) => {
    setAvoidWords(avoidWords.filter((item) => item !== w));
  };

  const handleFinish = async () => {
    if (!activeUserId) return;
    setSaving(true);
    try {
      await savePreferences({
        userId: activeUserId,
        roleTitle,
        language,
        tone,
        targetAudience,
        technicalLevel,
        postLength,
        avoidWords,
        preferredCTA: preferredCTA,
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
      if (onComplete) onComplete();
    } catch (err) {
      console.error("Error saving preferences:", err);
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
            Configurador de Voz Editorial
          </div>
          <h2 className="mt-2 text-2xl font-bold tracking-tight text-white">
            Personaliza tu Proof of Work
          </h2>
          <p className="text-xs text-zinc-400">
            Define tu estilo técnico para que la IA redacte con tu voz y nunca use clichés.
          </p>
        </div>

        {/* Step Progress */}
        <div className="flex items-center gap-2">
          {[1, 2, 3, 4].map((s) => (
            <div
              key={s}
              className={`flex size-8 items-center justify-center rounded-full text-xs font-semibold transition ${
                step === s
                  ? "bg-white text-black font-bold shadow-lg shadow-white/20"
                  : step > s
                    ? "bg-emerald-500/20 text-emerald-300 border border-emerald-500/40"
                    : "bg-white/5 text-zinc-500 border border-white/10"
              }`}
            >
              {step > s ? <Check className="size-4" /> : s}
            </div>
          ))}
        </div>
      </div>

      {/* Step Content */}
      <div className="mt-8 min-h-[340px]">
        {/* STEP 1: Perfil y Rol */}
        {step === 1 && (
          <div className="space-y-6">
            <h3 className="text-base font-semibold text-white">1. Tu Identidad Técnica</h3>

            <div className="space-y-4">
              <div>
                <label className="block text-xs font-medium text-zinc-300">
                  Tu Rol o Especialidad
                </label>
                <input
                  type="text"
                  value={roleTitle}
                  onChange={(e) => setRoleTitle(e.target.value)}
                  placeholder="ej: Senior Backend Engineer / AI Architect"
                  className="mt-1.5 w-full rounded-xl border border-white/10 bg-black/40 px-4 py-2.5 text-sm text-white placeholder-zinc-500 focus:border-white/30 focus:outline-none"
                />
              </div>

              <div>
                <label className="block text-xs font-medium text-zinc-300">
                  Idioma de las Publicaciones
                </label>
                <div className="mt-2 grid grid-cols-3 gap-3">
                  {[
                    { id: "es", label: "Español", desc: "Natural & profesional" },
                    { id: "en", label: "English", desc: "Global reach" },
                    { id: "pt", label: "Português", desc: "Comunidade tech" },
                  ].map((item) => (
                    <button
                      key={item.id}
                      type="button"
                      onClick={() => setLanguage(item.id as "es" | "en" | "pt")}
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
          </div>
        )}

        {/* STEP 2: Tono y Audiencia */}
        {step === 2 && (
          <div className="space-y-6">
            <h3 className="text-base font-semibold text-white">2. Tono y Audiencia</h3>

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
                      setTone(item.id as "humble_builder" | "deep_technical" | "direct_minimal" | "storyteller")
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

            <div className="grid gap-4 sm:grid-cols-3">
              <div>
                <label className="block text-xs font-medium text-zinc-300">Audiencia Objetivo</label>
                <select
                  value={targetAudience}
                  onChange={(e) =>
                    setTargetAudience(
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
                  onChange={(e) => setTechnicalLevel(e.target.value as "high" | "medium" | "accessible")}
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
                  onChange={(e) => setPostLength(e.target.value as "concise" | "standard" | "deep_dive")}
                  className="mt-1.5 w-full rounded-xl border border-white/10 bg-black/40 px-3.5 py-2 text-sm text-white focus:outline-none"
                >
                  <option value="concise">Conciso (100 - 150 palabras)</option>
                  <option value="standard">Estándar (150 - 250 palabras)</option>
                  <option value="deep_dive">Deep Dive (250 - 400 palabras)</option>
                </select>
              </div>
            </div>
          </div>
        )}

        {/* STEP 3: Filtro de Buzzwords y Reglas */}
        {step === 3 && (
          <div className="space-y-6">
            <h3 className="text-base font-semibold text-white">3. Reglas de Calidad Anti-Hype & Hashtags</h3>

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
                {avoidWords.map((w) => (
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
                    setPreferredCTA(
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
                    setHashtags(
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

        {/* STEP 4: Preview y Confirmación */}
        {step === 4 && (
          <div className="space-y-6">
            <div className="flex items-center justify-between">
              <h3 className="text-base font-semibold text-white">4. Previsualización de tu Estilo</h3>
              <span className="rounded-full border border-emerald-500/30 bg-emerald-500/10 px-2.5 py-0.5 font-mono text-xs text-emerald-300">
                Listo para producción
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
                  onChange={(e) => setAutoPublish(e.target.checked)}
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
            disabled={saving}
            className="inline-flex items-center gap-2 rounded-xl bg-emerald-400 px-6 py-2.5 text-xs font-bold text-black hover:bg-emerald-300 shadow-lg shadow-emerald-400/20 disabled:opacity-50"
          >
            {saving ? "Guardando..." : "Guardar y Activar Preferencias"}
            <CheckCircle2 className="size-4" />
          </button>
        )}
      </div>
    </div>
  );
}
