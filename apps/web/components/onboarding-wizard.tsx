"use client";

import { useState } from "react";
import { useQuery } from "convex/react";
import {
  ArrowLeft,
  ArrowRight,
  CheckCircle2,
  FileText,
  Layers,
  MessageSquare,
  Phone,
  ShieldAlert,
  User,
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


  // Overrides
  const [overrideName, setOverrideName] = useState<string | null>(null);
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
  const displayName = overrideName ?? defaultUser?.displayName ?? "Lead Developer";
  const roleTitle = overrideRole ?? existingPrefs?.roleTitle ?? "Senior Software Engineer";
  const language = overrideLanguage ?? existingPrefs?.language ?? "es";
  const tone = overrideTone ?? existingPrefs?.tone ?? "humble_builder";
  const technicalLevel = overrideTechnicalLevel ?? existingPrefs?.technicalLevel ?? "high";
  const targetAudience = overrideTargetAudience ?? existingPrefs?.targetAudience ?? "senior_engineers";
  const postLength = overridePostLength ?? existingPrefs?.postLength ?? "standard";
  const avoidWords: string[] =
    overrideAvoidWords ??
    existingPrefs?.avoidWords ??
    ["revolucionario", "game-changer", "mágico", "secreto", "infalible", "delve", "seamlessly"];
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

  const API_BASE_URL = (process.env.NEXT_PUBLIC_API_URL || "").replace(/\/$/, "");

  const handleFinish = async () => {
    setSaving(true);
    try {
      // 1. Update user profile via session API
      await fetch(`${API_BASE_URL}/api/portal/profile`, {
        method: "PATCH",
        credentials: "include",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          display_name: displayName,
        }),
      });

      // 2. Save editorial preferences via session API
      const res = await fetch(`${API_BASE_URL}/api/portal/preferences`, {
        method: "PUT",
        credentials: "include",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          role_title: roleTitle,
          language,
          tone,
          target_audience: targetAudience,
          technical_level: technicalLevel,
          post_length: postLength,
          avoid_words: avoidWords,
          preferred_cta: preferredCTA,
          hashtags,
          allowed_formats: [
            "problem_solution",
            "before_after",
            "build_log",
            "mini_case_study",
            "architecture_breakdown",
          ],
          auto_publish: autoPublish,
          onboarding_completed: true,
        }),
      });

      if (!res.ok) {
        throw new Error("Failed to save preferences");
      }

      setSavedSuccess(true);
      setTimeout(() => {
        if (onComplete) onComplete();
      }, 1000);
    } catch (err) {
      console.error("Error saving onboarding preferences:", err);
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
            Personalización de Voz & Formato
          </div>
          <h2 className="mt-2 text-2xl font-bold tracking-tight text-white">
            Configura tu Voz Editorial y Estilo
          </h2>
          <p className="text-xs text-zinc-400">
            Define tu rol, la profundidad técnica y el formato narrativo de tus publicaciones en LinkedIn.
          </p>
        </div>

        {/* Step Progress (3 Steps) */}
        <div className="flex items-center gap-2">
          {[
            { num: 1, label: "Identidad & Rol" },
            { num: 2, label: "Voz & Filtros" },
            { num: 3, label: "Formato & Preview" },
          ].map((s) => (
            <div
              key={s.num}
              className={`flex items-center gap-2 rounded-xl px-3.5 py-1.5 text-xs font-semibold transition ${
                step === s.num
                  ? "bg-white text-black font-bold shadow-lg shadow-white/20"
                  : step > s.num
                    ? "bg-emerald-500/20 text-emerald-300 border border-emerald-500/40"
                    : "bg-white/5 text-zinc-500 border border-white/10"
              }`}
            >
              <span>{step > s.num ? "✓" : s.num}</span>
              <span>{s.label}</span>
            </div>
          ))}
        </div>
      </div>

      {/* Step Content */}
      <div className="mt-8 min-h-[340px]">
        {/* STEP 1: Identidad, Rol e Idioma */}
        {step === 1 && (
          <div className="space-y-6">
            <div>
              <h3 className="text-base font-semibold text-white flex items-center gap-2">
                <User className="size-4 text-emerald-400" />
                1. Identidad Técnica y Audiencia
              </h3>
              <p className="text-xs text-zinc-400 mt-1">
                La IA contextualizará el nivel técnico de cada post según tu perfil profesional.
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
                  Tu Rol o Especialidad Técnica
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

            {/* Audience & Technical Level */}
            <div className="grid gap-4 sm:grid-cols-2">
              <div>
                <label className="block text-xs font-medium text-zinc-300">Audiencia Objetivo</label>
                <select
                  value={targetAudience}
                  onChange={(e) =>
                    setOverrideTargetAudience(
                      e.target.value as "senior_engineers" | "tech_founders" | "recruiters" | "general_tech",
                    )
                  }
                  className="mt-1.5 w-full rounded-xl border border-white/10 bg-black/40 px-3.5 py-2.5 text-sm text-white focus:outline-none"
                >
                  <option value="senior_engineers">Senior Engineers & Tech Leads</option>
                  <option value="tech_founders">Founders & CTOs</option>
                  <option value="recruiters">Recruiters & Hiring Managers</option>
                  <option value="general_tech">Comunidad Tech General</option>
                </select>
              </div>

              <div>
                <label className="block text-xs font-medium text-zinc-300">Nivel de Profundidad Técnica</label>
                <select
                  value={technicalLevel}
                  onChange={(e) =>
                    setOverrideTechnicalLevel(e.target.value as "high" | "medium" | "accessible")
                  }
                  className="mt-1.5 w-full rounded-xl border border-white/10 bg-black/40 px-3.5 py-2.5 text-sm text-white focus:outline-none"
                >
                  <option value="high">Alto (Arquitectura, diffs, trade-offs y benchmarks)</option>
                  <option value="medium">Medio (Balance entre producto y código)</option>
                  <option value="accessible">Accesible (Enfoque conceptual sin jerga compleja)</option>
                </select>
              </div>
            </div>

            {/* Language Selector */}
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

        {/* STEP 2: Tono Editorial, Filtro de Clichés & CTA */}
        {step === 2 && (
          <div className="space-y-6">
            <div>
              <h3 className="text-base font-semibold text-white flex items-center gap-2">
                <Layers className="size-4 text-emerald-400" />
                2. Tono Editorial y Reglas Anti-Hype
              </h3>
              <p className="text-xs text-zinc-400 mt-1">
                La evidencia de tus commits manda. Cero datos inventados, cero clichés de IA.
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
                    desc: "Enfocado en lecciones aprendidas, desafíos y trade-offs reales.",
                  },
                  {
                    id: "deep_technical",
                    label: "Técnico Profundo",
                    desc: "Detalle de arquitectura, impacto en rendimiento y decisiones de diseño.",
                  },
                  {
                    id: "direct_minimal",
                    label: "Directo & Minimalista",
                    desc: "Estructura Problem -> Solution en pocas líneas, sin relleno.",
                  },
                  {
                    id: "storyteller",
                    label: "Narrativo / Storytelling",
                    desc: "La narrativa del bug a la solución en producción.",
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

            {/* Avoid Words (Anti-Hype Filter) */}
            <div>
              <div className="flex items-center gap-2">
                <ShieldAlert className="size-4 text-amber-400" />
                <label className="text-xs font-medium text-zinc-300">
                  Palabras Prohibidas (Filtro Anti-Cliché)
                </label>
              </div>
              <p className="mt-1 text-xs text-zinc-500">
                La IA tiene estrictamente prohibido usar estas palabras al redactar tus historias.
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

            {/* CTA & Hashtags */}
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
                  className="mt-1.5 w-full rounded-xl border border-white/10 bg-black/40 px-3.5 py-2.5 text-sm text-white focus:outline-none"
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
                  className="mt-1.5 w-full rounded-xl border border-white/10 bg-black/40 px-3.5 py-2.5 text-sm text-white focus:outline-none"
                />
              </div>
            </div>
          </div>
        )}

        {/* STEP 3: Formato Narrativo & Previsualización Grounded */}
        {step === 3 && (
          <div className="space-y-6">
            <div className="flex items-center justify-between">
              <div>
                <h3 className="text-base font-semibold text-white flex items-center gap-2">
                  <FileText className="size-4 text-emerald-400" />
                  3. Formato Grounded y Previsualización
                </h3>
                <p className="text-xs text-zinc-400 mt-1">
                  Estructura técnica con evidencia de commits: Reto, Solución, Resultado y Aprendizaje.
                </p>
              </div>
              <span className="rounded-full border border-emerald-500/30 bg-emerald-500/10 px-3 py-1 font-mono text-xs text-emerald-300">
                Formato Problem → Solution
              </span>
            </div>

            {/* Post Length Selector */}
            <div className="grid gap-3 sm:grid-cols-3">
              {[
                { id: "concise", label: "Conciso (100-150 palabras)", desc: "Directo al grano para feeds rápidos." },
                { id: "standard", label: "Estándar (150-250 palabras)", desc: "Formato recomendado con reto y lección." },
                { id: "deep_dive", label: "Deep Dive (250-400 palabras)", desc: "Desglose minucioso de arquitectura." },
              ].map((len) => (
                <button
                  key={len.id}
                  type="button"
                  onClick={() => setOverridePostLength(len.id as "concise" | "standard" | "deep_dive")}
                  className={`rounded-2xl border p-3 text-left transition ${
                    postLength === len.id
                      ? "border-emerald-400 bg-emerald-500/10 text-white"
                      : "border-white/10 bg-black/30 text-zinc-400 hover:border-white/20"
                  }`}
                >
                  <p className="text-xs font-semibold">{len.label}</p>
                  <p className="text-[10px] text-zinc-500 mt-0.5">{len.desc}</p>
                </button>
              ))}
            </div>

            {/* Live Grounded Mock Preview */}
            <div className="rounded-2xl border border-white/10 bg-black/60 p-5 font-mono text-xs leading-relaxed text-zinc-300">
              <div className="flex items-center justify-between border-b border-white/10 pb-3 mb-3">
                <span className="font-bold text-white text-sm">
                  🚀 Optimización de Consultas Reactivas con Índices Compuestos
                </span>
                <span className="text-[10px] text-emerald-400 bg-emerald-500/10 px-2 py-0.5 rounded-full border border-emerald-500/20">
                  Evidencia 100% Verificada
                </span>
              </div>

              <p className="text-zinc-300">
                Al escalar el dashboard en tiempo real con Convex, las consultas agregadas por tenant
                empezaron a generar latencia acumulada en eventos push masivos.
              </p>

              <div className="my-3 space-y-1.5 border-l-2 border-emerald-500/50 pl-3">
                <p className="text-zinc-400">
                  <strong className="text-white">El reto:</strong> Reducir el scan overhead sin romper la reactividad de las suscripciones.
                </p>
                <p className="text-zinc-400">
                  <strong className="text-white">Qué hicimos:</strong> Reestructuramos el esquema con índices compuestos `by_user_status` y batching de eventos en el backend.
                </p>
                <p className="text-zinc-400">
                  <strong className="text-white">Resultado:</strong> El tiempo de sincronización se estabilizó de forma inmediata sin locks.
                </p>
                <p className="text-zinc-400">
                  <strong className="text-white">Aprendizaje clave:</strong> La reactividad solo escala si los índices reflejan exactamente el patrón de acceso de la UI.
                </p>
              </div>

              <p className="mt-3 text-zinc-400">
                {preferredCTA === "discussion_question"
                  ? "¿Cómo manejan este trade-off en sus arquitecturas reactivas?"
                  : "📌 Conclusión: Medir siempre el índice antes de optimizar la capa de transporte."}
              </p>
              <p className="mt-3 text-emerald-400 font-semibold">{hashtags.join(" ")}</p>
            </div>

            {/* Approval Workflow Note & Mandatory Bot Button */}
            <div className="rounded-2xl border border-emerald-500/30 bg-emerald-950/20 p-4 space-y-3">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-3">
                  <div className="flex size-8 items-center justify-center rounded-lg bg-emerald-500/20 text-emerald-400">
                    <Phone className="size-4" />
                  </div>
                  <div>
                    <p className="text-xs font-semibold text-white">Validación de Aprobación por WhatsApp</p>
                    <p className="text-[11px] text-zinc-400">
                      Debes hablarle primero al bot oficial para abrir la ventana de 24h y recibir borradores.
                    </p>
                  </div>
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

              <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-2 pt-2 border-t border-emerald-500/20">
                <p className="text-[11px] text-emerald-300">
                  Bot oficial de LaborIN: <strong>+1 (208) 441-5504</strong>
                </p>
                <a
                  href="https://wa.me/12084415504?text=Hola%20LaborIN,%20quiero%20activar%20mi%20cuenta"
                  target="_blank"
                  rel="noopener noreferrer"
                  className="inline-flex items-center justify-center gap-1.5 rounded-xl bg-emerald-400 px-3.5 py-2 text-xs font-bold text-black hover:bg-emerald-300 transition shrink-0 shadow-sm"
                >
                  <MessageSquare className="size-3.5" />
                  Hablar al +1 (208) 441-5504 para Iniciar Validación
                </a>
              </div>
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
            className="inline-flex items-center gap-2 rounded-xl border border-white/10 bg-white/5 px-4 py-2.5 text-xs font-semibold text-white hover:bg-white/10 transition"
          >
            <ArrowLeft className="size-4" /> Anterior
          </button>
        ) : (
          <div />
        )}

        {step < 3 ? (
          <button
            type="button"
            onClick={() => setStep(step + 1)}
            className="inline-flex items-center gap-2 rounded-xl bg-white px-5 py-2.5 text-xs font-bold text-black hover:bg-zinc-200 transition shadow-lg shadow-white/10"
          >
            Siguiente <ArrowRight className="size-4" />
          </button>
        ) : (
          <button
            type="button"
            onClick={handleFinish}
            disabled={saving || savedSuccess}
            className="inline-flex items-center gap-2 rounded-xl bg-emerald-400 px-6 py-2.5 text-xs font-bold text-black hover:bg-emerald-300 transition shadow-lg shadow-emerald-400/20 disabled:opacity-50"
          >
            {saving ? "Guardando..." : savedSuccess ? "¡Preferencias Guardadas!" : "Guardar y Finalizar Personalización"}
            <CheckCircle2 className="size-4" />
          </button>
        )}
      </div>
    </div>
  );
}
