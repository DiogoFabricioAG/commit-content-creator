"use client";

import { useState } from "react";
import { useQuery } from "convex/react";
import {
  ArrowLeft,
  ArrowRight,
  CheckCircle2,
  Code2,
  FileText,
  MessageSquare,
  Phone,
  Plus,
  ShieldAlert,
  Sparkles,
  User,
  Wand2,
  X,
  Zap,
} from "lucide-react";
import { api } from "@convex/api";
import type { Id } from "@convex/dataModel";

type OnboardingWizardProps = {
  userId?: Id<"users">;
  onComplete?: () => void;
};

type ToneKey =
  | "humble_builder"
  | "deep_technical"
  | "direct_minimal"
  | "storyteller"
  | "pragmatic_lead"
  | "startup_founder";

type AudienceKey =
  | "senior_engineers"
  | "tech_founders"
  | "recruiters"
  | "junior_developers"
  | "general_tech";

type CTAKey =
  | "discussion_question"
  | "github_link"
  | "lesson_takeaway"
  | "custom_cta"
  | "none";

const TONE_OPTIONS: { id: ToneKey; title: string; badge: string; desc: string; sampleHook: string }[] = [
  {
    id: "humble_builder",
    title: "Constructor Humilde",
    badge: "Recomendado",
    desc: "Transparente sobre retos y errores. Destaca lecciones prácticas y trade-offs reales sin arrogancia.",
    sampleHook: "Pasamos 3 días buscando un memory leak en producción. La causa fue mucho más simple de lo que pensábamos.",
  },
  {
    id: "deep_technical",
    title: "Técnico Profundo",
    badge: "Arquitectura",
    desc: "Detalle riguroso de arquitectura, estructuras de datos, índices, concurrencia y decisiones de bajo nivel.",
    sampleHook: "Cómo redujimos el overhead de consultas agregadas a O(1) combinando índices compuestos y batching asíncrono.",
  },
  {
    id: "direct_minimal",
    title: "Directo & Minimalista",
    badge: "Alto Signal/Noise",
    desc: "Estructura concisa, bullet points, cero relleno. Directo al problema técnico y a la solución aplicada.",
    sampleHook: "Problema: Locks en base de datos bajo alta concurrencia.\nSolución: Aislamiento optimista a nivel de tenant.",
  },
  {
    id: "storyteller",
    title: "Narrador de Historias",
    badge: "Engaging",
    desc: "Gancho inicial atractivo, tensión técnica durante el bug y desenlace satisfactorio en producción.",
    sampleHook: "Eran las 2 AM cuando el alert manager se encendió: la sincronización en tiempo real se había congelado.",
  },
  {
    id: "pragmatic_lead",
    title: "Líder Pragmático",
    badge: "Engineering Lead",
    desc: "Enfoque en mantenibilidad, velocidad del equipo, reducción de deuda técnica y decisiones pragmáticas.",
    sampleHook: "No reescribimos todo desde cero: aislamos los 3 módulos críticos y aumentamos la velocidad del equipo un 40%.",
  },
  {
    id: "startup_founder",
    title: "Fundador Técnico",
    badge: "Product Engineer",
    desc: "Velocidad de shipping, balance entre arquitectura limpia y valor directo entregado a los usuarios.",
    sampleHook: "Cómo lanzamos el nuevo motor de autorizaciones en 48 horas manteniendo tests negativos y aislamiento total.",
  },
];

const FORMAT_OPTIONS: { id: string; label: string; desc: string }[] = [
  { id: "problem_solution", label: "Problema → Solución", desc: "El formato clásico de ingeniería con contexto y resolución." },
  { id: "before_after", label: "Antes vs Después", desc: "Contraste directo del sistema antes y después del cambio." },
  { id: "build_log", label: "Diario de Construcción", desc: "Ship log cronológico desde el reto inicial hasta el despliegue." },
  { id: "mini_case_study", label: "Mini Caso de Estudio", desc: "Conecta problema, decisión arquitectónica, resultado y aprendizaje." },
  { id: "architecture_breakdown", label: "Desglose de Arquitectura", desc: "Explicación paso a paso de diagramas y capas del sistema." },
  { id: "failure_story", label: "Historia de Error & Aprendizaje", desc: "Postmortem constructivo: qué falló y cómo se solucionó definitivamente." },
  { id: "benchmark_metric", label: "Métricas & Rendimiento", desc: "Enfoque en optimizaciones numéricas, latencia y throughput." },
];

const SUGGESTED_BUZZWORDS = [
  "revolucionario",
  "game-changer",
  "mágico",
  "secreto",
  "infalible",
  "delve",
  "seamlessly",
  "paradigma",
  "disruptivo",
  "innovador",
];

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
  const [overrideTone, setOverrideTone] = useState<ToneKey | null>(null);
  const [overrideTargetAudience, setOverrideTargetAudience] = useState<AudienceKey | null>(null);
  const [overrideTechnicalLevel, setOverrideTechnicalLevel] = useState<"high" | "medium" | "accessible" | null>(null);
  const [overridePostLength, setOverridePostLength] = useState<"concise" | "standard" | "deep_dive" | null>(null);
  const [overrideAllowedFormats, setOverrideAllowedFormats] = useState<string[] | null>(null);
  const [overrideAvoidWords, setOverrideAvoidWords] = useState<string[] | null>(null);
  const [newAvoidWord, setNewAvoidWord] = useState("");
  const [overrideCustomRules, setOverrideCustomRules] = useState<string[] | null>(null);
  const [newRule, setNewRule] = useState("");
  const [overridePreferredCTA, setOverridePreferredCTA] = useState<CTAKey | null>(null);
  const [overrideCustomCTA, setOverrideCustomCTA] = useState<string | null>(null);
  const [overrideIncludeCodeSnippets, setOverrideIncludeCodeSnippets] = useState<boolean | null>(null);
  const [overrideIncludeMetrics, setOverrideIncludeMetrics] = useState<boolean | null>(null);
  const [overrideHashtags, setOverrideHashtags] = useState<string[] | null>(null);
  const [overrideAutoPublish, setOverrideAutoPublish] = useState<boolean | null>(null);
  const [saving, setSaving] = useState(false);
  const [savedSuccess, setSavedSuccess] = useState(false);

  // Effective Values
  const displayName = overrideName ?? defaultUser?.displayName ?? "Lead Developer";
  const roleTitle = overrideRole ?? existingPrefs?.roleTitle ?? "Senior Software Engineer";
  const language = overrideLanguage ?? existingPrefs?.language ?? "es";
  const tone: ToneKey = (overrideTone ?? existingPrefs?.tone ?? "humble_builder") as ToneKey;
  const targetAudience: AudienceKey = (overrideTargetAudience ?? existingPrefs?.targetAudience ?? "senior_engineers") as AudienceKey;
  const technicalLevel = overrideTechnicalLevel ?? existingPrefs?.technicalLevel ?? "high";
  const postLength = overridePostLength ?? existingPrefs?.postLength ?? "standard";
  const allowedFormats: string[] =
    overrideAllowedFormats ??
    existingPrefs?.allowedFormats ?? [
      "problem_solution",
      "before_after",
      "build_log",
      "mini_case_study",
      "architecture_breakdown",
      "failure_story",
      "benchmark_metric",
    ];
  const avoidWords: string[] =
    overrideAvoidWords ??
    existingPrefs?.avoidWords ?? [
      "revolucionario",
      "game-changer",
      "mágico",
      "secreto",
      "infalible",
      "delve",
      "seamlessly",
      "paradigma",
      "disruptivo",
    ];
  const customRules: string[] = overrideCustomRules ?? (existingPrefs as { customRules?: string[] })?.customRules ?? [];
  const preferredCTA: CTAKey = (overridePreferredCTA ?? existingPrefs?.preferredCTA ?? "discussion_question") as CTAKey;
  const customCTA = overrideCustomCTA ?? (existingPrefs as { customCTA?: string })?.customCTA ?? "¿Cómo lo resolverían ustedes?";
  const includeCodeSnippets =
    overrideIncludeCodeSnippets ?? (existingPrefs as { includeCodeSnippets?: boolean })?.includeCodeSnippets ?? true;
  const includeMetrics =
    overrideIncludeMetrics ?? (existingPrefs as { includeMetrics?: boolean })?.includeMetrics ?? true;
  const hashtags: string[] =
    overrideHashtags ?? existingPrefs?.hashtags ?? ["#SoftwareEngineering", "#Architecture", "#ProofOfWork", "#BuildInPublic"];
  const autoPublish = overrideAutoPublish ?? existingPrefs?.autoPublish ?? false;

  const toggleFormat = (formatId: string) => {
    if (allowedFormats.includes(formatId)) {
      if (allowedFormats.length > 1) {
        setOverrideAllowedFormats(allowedFormats.filter((f) => f !== formatId));
      }
    } else {
      setOverrideAllowedFormats([...allowedFormats, formatId]);
    }
  };

  const addAvoidWord = (wordToAdd?: string) => {
    const word = (wordToAdd || newAvoidWord).trim().toLowerCase();
    if (word && !avoidWords.includes(word)) {
      setOverrideAvoidWords([...avoidWords, word]);
      if (!wordToAdd) setNewAvoidWord("");
    }
  };

  const removeAvoidWord = (w: string) => {
    setOverrideAvoidWords(avoidWords.filter((item) => item !== w));
  };

  const addCustomRule = () => {
    if (newRule.trim() && !customRules.includes(newRule.trim())) {
      setOverrideCustomRules([...customRules, newRule.trim()]);
      setNewRule("");
    }
  };

  const removeCustomRule = (r: string) => {
    setOverrideCustomRules(customRules.filter((item) => item !== r));
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
          custom_rules: customRules,
          include_code_snippets: includeCodeSnippets,
          include_metrics: includeMetrics,
          preferred_cta: preferredCTA,
          custom_cta: preferredCTA === "custom_cta" ? customCTA : undefined,
          hashtags,
          allowed_formats: allowedFormats,
          auto_publish: autoPublish,
          onboarding_completed: true,
        }),
      });

      if (!res.ok) {
        const errData = await res.json().catch(() => ({}));
        throw new Error((errData as { detail?: string })?.detail || "Failed to save preferences");
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

  // Live mockup text generator for dynamic preview
  const selectedToneObj = TONE_OPTIONS.find((t) => t.id === tone) ?? TONE_OPTIONS[0];

  return (
    <div className="rounded-3xl border border-white/10 bg-[#09090b]/90 p-6 sm:p-8 backdrop-blur-xl shadow-2xl">
      {/* Header & Steps Indicator */}
      <div className="flex flex-col gap-4 border-b border-white/10 pb-6 lg:flex-row lg:items-center lg:justify-between">
        <div>
          <div className="inline-flex items-center gap-2 rounded-full border border-emerald-500/30 bg-emerald-500/10 px-3 py-1 text-xs font-mono text-emerald-300">
            <Sparkles className="size-3.5" />
            LaborIN Editorial Studio · Control Total de IA
          </div>
          <h2 className="mt-2 text-2xl font-bold tracking-tight text-white">
            Personaliza tu Voz de Autor & Reglas de Publicación
          </h2>
          <p className="text-xs text-zinc-400 mt-1">
            Cada push de GitHub se redactará respetando rigurosamente tu tono, tu rol técnico y tus reglas anti-hype.
          </p>
        </div>

        {/* Step Progress */}
        <div className="flex flex-wrap items-center gap-2">
          {[
            { num: 1, label: "Identidad & Rol" },
            { num: 2, label: "Voz & Personalidad" },
            { num: 3, label: "Formatos & Reglas" },
            { num: 4, label: "Preview & Canales" },
          ].map((s) => (
            <button
              key={s.num}
              type="button"
              onClick={() => setStep(s.num)}
              className={`flex items-center gap-2 rounded-xl px-3 py-1.5 text-xs font-semibold transition ${
                step === s.num
                  ? "bg-white text-black font-bold shadow-lg shadow-white/20"
                  : step > s.num
                    ? "bg-emerald-500/20 text-emerald-300 border border-emerald-500/40"
                    : "bg-white/5 text-zinc-500 border border-white/10 hover:border-white/20"
              }`}
            >
              <span>{step > s.num ? "✓" : s.num}</span>
              <span>{s.label}</span>
            </button>
          ))}
        </div>
      </div>

      {/* Main Form Body */}
      <div className="mt-8 min-h-[380px]">
        {/* STEP 1: Identidad & Rol */}
        {step === 1 && (
          <div className="space-y-6">
            <div>
              <h3 className="text-base font-semibold text-white flex items-center gap-2">
                <User className="size-4 text-emerald-400" />
                1. Identidad Técnica y Audiencia Principal
              </h3>
              <p className="text-xs text-zinc-400 mt-1">
                Configura tu identidad profesional para que el agente use el vocabulario y perspectiva adecuados.
              </p>
            </div>

            <div className="grid gap-4 sm:grid-cols-2">
              <div>
                <label className="block text-xs font-medium text-zinc-300">Nombre de Autor a Mostrar</label>
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
                  Título Técnico o Especialidad
                </label>
                <input
                  type="text"
                  value={roleTitle}
                  onChange={(e) => setOverrideRole(e.target.value)}
                  placeholder="ej: Staff Backend Engineer / AI Architect"
                  className="mt-1.5 w-full rounded-xl border border-white/10 bg-black/40 px-4 py-2.5 text-sm text-white placeholder-zinc-500 focus:border-white/30 focus:outline-none"
                />
              </div>
            </div>

            <div className="grid gap-4 sm:grid-cols-2">
              <div>
                <label className="block text-xs font-medium text-zinc-300">Audiencia Principal a Impactar</label>
                <select
                  value={targetAudience}
                  onChange={(e) => setOverrideTargetAudience(e.target.value as AudienceKey)}
                  className="mt-1.5 w-full rounded-xl border border-white/10 bg-black/40 px-3.5 py-2.5 text-sm text-white focus:outline-none"
                >
                  <option value="senior_engineers">Senior Engineers & Tech Leads (Profundidad y trade-offs)</option>
                  <option value="tech_founders">CTOs & Fundadores Técnicos (Velocidad, arquitectura y valor)</option>
                  <option value="recruiters">Recruiters & Hiring Managers (Artesanía técnica y ownership)</option>
                  <option value="junior_developers">Desarrolladores Junior (Didáctico y lecciones claras)</option>
                  <option value="general_tech">Comunidad Tech General (Accesible y riguroso)</option>
                </select>
              </div>

              <div>
                <label className="block text-xs font-medium text-zinc-300">Idioma de Publicación</label>
                <div className="mt-1.5 grid grid-cols-3 gap-2">
                  {[
                    { id: "es", label: "Español", flag: "🇪🇸" },
                    { id: "en", label: "English", flag: "🇺🇸" },
                    { id: "pt", label: "Português", flag: "🇧🇷" },
                  ].map((item) => (
                    <button
                      key={item.id}
                      type="button"
                      onClick={() => setOverrideLanguage(item.id as "es" | "en" | "pt")}
                      className={`flex items-center justify-center gap-1.5 rounded-xl border py-2.5 text-xs font-semibold transition ${
                        language === item.id
                          ? "border-emerald-400 bg-emerald-500/10 text-emerald-300 shadow-sm"
                          : "border-white/10 bg-black/30 text-zinc-400 hover:border-white/20"
                      }`}
                    >
                      <span>{item.flag}</span>
                      <span>{item.label}</span>
                    </button>
                  ))}
                </div>
              </div>
            </div>
          </div>
        )}

        {/* STEP 2: Voz, Tono & Personalidad */}
        {step === 2 && (
          <div className="space-y-6">
            <div>
              <h3 className="text-base font-semibold text-white flex items-center gap-2">
                <Wand2 className="size-4 text-emerald-400" />
                2. Voz, Tono Editorial y Profundidad
              </h3>
              <p className="text-xs text-zinc-400 mt-1">
                Elige la personalidad con la que el agente narrará tus soluciones de software.
              </p>
            </div>

            {/* 6 Tone Cards */}
            <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
              {TONE_OPTIONS.map((item) => (
                <button
                  key={item.id}
                  type="button"
                  onClick={() => setOverrideTone(item.id)}
                  className={`rounded-2xl border p-4 text-left transition relative flex flex-col justify-between ${
                    tone === item.id
                      ? "border-emerald-400 bg-emerald-500/10 text-white shadow-lg shadow-emerald-500/5"
                      : "border-white/10 bg-black/30 text-zinc-400 hover:border-white/25 hover:bg-white/[0.02]"
                  }`}
                >
                  <div>
                    <div className="flex items-center justify-between mb-2">
                      <span className="font-bold text-sm text-white">{item.title}</span>
                      <span className={`text-[10px] px-2 py-0.5 rounded-full border font-mono ${
                        tone === item.id
                          ? "bg-emerald-500/20 text-emerald-300 border-emerald-500/30"
                          : "bg-white/5 text-zinc-500 border-white/10"
                      }`}>
                        {item.badge}
                      </span>
                    </div>
                    <p className="text-xs text-zinc-400 leading-snug">{item.desc}</p>
                  </div>

                  <div className="mt-3 pt-2.5 border-t border-white/5 text-[11px] text-zinc-500 italic">
                    &ldquo;{item.sampleHook}&rdquo;
                  </div>
                </button>
              ))}
            </div>

            {/* Technical Depth & Length */}
            <div className="grid gap-4 sm:grid-cols-2 pt-2">
              <div>
                <label className="block text-xs font-medium text-zinc-300">Profundidad Técnica</label>
                <select
                  value={technicalLevel}
                  onChange={(e) => setOverrideTechnicalLevel(e.target.value as "high" | "medium" | "accessible")}
                  className="mt-1.5 w-full rounded-xl border border-white/10 bg-black/40 px-3.5 py-2.5 text-sm text-white focus:outline-none"
                >
                  <option value="high">Alto (Detalle de código, diffs, índices, concurrencia)</option>
                  <option value="medium">Medio (Balance entre diseño de sistemas y código)</option>
                  <option value="accessible">Accesible (Enfoque conceptual comprensible para todos)</option>
                </select>
              </div>

              <div>
                <label className="block text-xs font-medium text-zinc-300">Longitud del Post</label>
                <div className="mt-1.5 grid grid-cols-3 gap-2">
                  {[
                    { id: "concise", label: "Conciso", desc: "100-150 p." },
                    { id: "standard", label: "Estándar", desc: "150-250 p." },
                    { id: "deep_dive", label: "Deep Dive", desc: "250-400 p." },
                  ].map((len) => (
                    <button
                      key={len.id}
                      type="button"
                      onClick={() => setOverridePostLength(len.id as "concise" | "standard" | "deep_dive")}
                      className={`rounded-xl border py-2 px-2 text-center transition ${
                        postLength === len.id
                          ? "border-emerald-400 bg-emerald-500/10 text-white"
                          : "border-white/10 bg-black/30 text-zinc-400 hover:border-white/20"
                      }`}
                    >
                      <p className="text-xs font-semibold">{len.label}</p>
                      <p className="text-[10px] text-zinc-500">{len.desc}</p>
                    </button>
                  ))}
                </div>
              </div>
            </div>

            {/* Code Snippets & Metrics Switches */}
            <div className="grid gap-3 sm:grid-cols-2 pt-2">
              <label className="flex items-center justify-between p-3.5 rounded-2xl border border-white/10 bg-black/30 cursor-pointer hover:border-white/20 transition">
                <div className="flex items-center gap-2.5">
                  <Code2 className="size-4 text-emerald-400" />
                  <div>
                    <p className="text-xs font-semibold text-white">Incluir fragmentos de código / diffs</p>
                    <p className="text-[10px] text-zinc-400">Inserta ejemplos de código concisos cuando aporten valor.</p>
                  </div>
                </div>
                <input
                  type="checkbox"
                  checked={includeCodeSnippets}
                  onChange={(e) => setOverrideIncludeCodeSnippets(e.target.checked)}
                  className="rounded bg-black border-white/20 text-emerald-500 size-4 focus:ring-0"
                />
              </label>

              <label className="flex items-center justify-between p-3.5 rounded-2xl border border-white/10 bg-black/30 cursor-pointer hover:border-white/20 transition">
                <div className="flex items-center gap-2.5">
                  <Zap className="size-4 text-sky-400" />
                  <div>
                    <p className="text-xs font-semibold text-white">Destacar métricas y benchmarks</p>
                    <p className="text-[10px] text-zinc-400">Resalta números reales de diffs, tiempos y rendimiento.</p>
                  </div>
                </div>
                <input
                  type="checkbox"
                  checked={includeMetrics}
                  onChange={(e) => setOverrideIncludeMetrics(e.target.checked)}
                  className="rounded bg-black border-white/20 text-sky-500 size-4 focus:ring-0"
                />
              </label>
            </div>
          </div>
        )}

        {/* STEP 3: Formatos Editoriales & Reglas Anti-Hype */}
        {step === 3 && (
          <div className="space-y-6">
            <div>
              <h3 className="text-base font-semibold text-white flex items-center gap-2">
                <ShieldAlert className="size-4 text-amber-400" />
                3. Formatos Permitidos & Reglas Anti-Hype
              </h3>
              <p className="text-xs text-zinc-400 mt-1">
                Define qué formatos narrativos puede usar el agente y qué palabras o clichés están 100% prohibidos.
              </p>
            </div>

            {/* Formats Selection */}
            <div>
              <label className="block text-xs font-medium text-zinc-300 mb-2">
                Formatos Editoriales Permitidos (Selecciona los que te gusten)
              </label>
              <div className="grid gap-2.5 sm:grid-cols-2 lg:grid-cols-3">
                {FORMAT_OPTIONS.map((fmt) => {
                  const isSelected = allowedFormats.includes(fmt.id);
                  return (
                    <button
                      key={fmt.id}
                      type="button"
                      onClick={() => toggleFormat(fmt.id)}
                      className={`rounded-2xl border p-3 text-left transition flex items-start justify-between ${
                        isSelected
                          ? "border-emerald-400/80 bg-emerald-500/10 text-white"
                          : "border-white/10 bg-black/30 text-zinc-500 hover:border-white/20"
                      }`}
                    >
                      <div>
                        <p className="text-xs font-semibold text-white">{fmt.label}</p>
                        <p className="text-[10px] text-zinc-400 mt-0.5">{fmt.desc}</p>
                      </div>
                      <span className={`size-4 rounded-full flex items-center justify-center text-[10px] shrink-0 ml-2 font-bold ${
                        isSelected ? "bg-emerald-400 text-black" : "border border-white/20"
                      }`}>
                        {isSelected ? "✓" : ""}
                      </span>
                    </button>
                  );
                })}
              </div>
            </div>

            {/* Avoid Words / Anti-Hype */}
            <div className="pt-2">
              <div className="flex items-center justify-between">
                <label className="text-xs font-medium text-zinc-300 flex items-center gap-1.5">
                  <ShieldAlert className="size-3.5 text-rose-400" />
                  Palabras Prohibidas (Filtro Anti-Cliché IA)
                </label>
                <span className="text-[10px] text-zinc-500 font-mono">
                  {avoidWords.length} palabras bloqueadas
                </span>
              </div>

              {/* Suggestions chips */}
              <div className="mt-2 flex flex-wrap items-center gap-1.5">
                <span className="text-[11px] text-zinc-500">Sugerencias rápidas:</span>
                {SUGGESTED_BUZZWORDS.filter((w) => !avoidWords.includes(w)).slice(0, 5).map((w) => (
                  <button
                    key={w}
                    type="button"
                    onClick={() => addAvoidWord(w)}
                    className="inline-flex items-center gap-1 rounded-md border border-white/10 bg-white/5 px-2 py-0.5 text-[10px] text-zinc-400 hover:border-white/30 hover:text-white"
                  >
                    <Plus className="size-2.5" /> {w}
                  </button>
                ))}
              </div>

              {/* Active avoid words */}
              <div className="mt-3 flex flex-wrap gap-1.5 p-3 rounded-2xl border border-white/10 bg-black/40 min-h-[50px]">
                {avoidWords.map((w) => (
                  <span
                    key={w}
                    className="inline-flex items-center gap-1.5 rounded-lg border border-rose-500/30 bg-rose-500/10 px-2.5 py-1 text-xs text-rose-300"
                  >
                    {w}
                    <button
                      type="button"
                      onClick={() => removeAvoidWord(w)}
                      className="hover:text-white"
                    >
                      <X className="size-3" />
                    </button>
                  </span>
                ))}
              </div>

              {/* Input for adding new word */}
              <div className="mt-2 flex gap-2">
                <input
                  type="text"
                  value={newAvoidWord}
                  onChange={(e) => setNewAvoidWord(e.target.value)}
                  onKeyDown={(e) => e.key === "Enter" && (e.preventDefault(), addAvoidWord())}
                  placeholder="Agregar palabra prohibida (ej: disruptivo)..."
                  className="flex-1 rounded-xl border border-white/10 bg-black/40 px-3.5 py-2 text-xs text-white placeholder-zinc-600 focus:outline-none"
                />
                <button
                  type="button"
                  onClick={() => addAvoidWord()}
                  className="rounded-xl border border-white/20 bg-white/10 px-4 py-2 text-xs font-semibold text-white hover:bg-white/20"
                >
                  Agregar
                </button>
              </div>
            </div>

            {/* Custom Author Rules */}
            <div className="pt-2">
              <label className="block text-xs font-medium text-zinc-300">
                Reglas de Estilo Personalizadas (Directivas libres para el agente)
              </label>
              <p className="text-[11px] text-zinc-500 mt-0.5">
                Instrucciones específicas que el LLM seguirá siempre (ej: &ldquo;No uses emojis en el título&rdquo;, &ldquo;Usa viñetas para contrastar trade-offs&rdquo;).
              </p>

              {customRules.length > 0 && (
                <div className="mt-2 space-y-1.5">
                  {customRules.map((rule) => (
                    <div
                      key={rule}
                      className="flex items-center justify-between rounded-xl border border-white/10 bg-white/[0.02] px-3 py-2 text-xs text-zinc-300"
                    >
                      <span>• {rule}</span>
                      <button
                        type="button"
                        onClick={() => removeCustomRule(rule)}
                        className="text-zinc-500 hover:text-rose-400"
                      >
                        <X className="size-3.5" />
                      </button>
                    </div>
                  ))}
                </div>
              )}

              <div className="mt-2 flex gap-2">
                <input
                  type="text"
                  value={newRule}
                  onChange={(e) => setNewRule(e.target.value)}
                  onKeyDown={(e) => e.key === "Enter" && (e.preventDefault(), addCustomRule())}
                  placeholder="ej: Empezar siempre con el resultado medido..."
                  className="flex-1 rounded-xl border border-white/10 bg-black/40 px-3.5 py-2 text-xs text-white placeholder-zinc-600 focus:outline-none"
                />
                <button
                  type="button"
                  onClick={addCustomRule}
                  className="rounded-xl border border-white/20 bg-white/10 px-4 py-2 text-xs font-semibold text-white hover:bg-white/20"
                >
                  Añadir Regla
                </button>
              </div>
            </div>
          </div>
        )}

        {/* STEP 4: Preview Reactivo en Tiempo Real & Canales */}
        {step === 4 && (
          <div className="space-y-6">
            <div className="flex items-center justify-between">
              <div>
                <h3 className="text-base font-semibold text-white flex items-center gap-2">
                  <FileText className="size-4 text-emerald-400" />
                  4. Previsualización en Vivo de tu Voz de Autor
                </h3>
                <p className="text-xs text-zinc-400 mt-1">
                  Así transformará el agente de LaborIN tus commits en publicaciones de LinkedIn con tu configuración.
                </p>
              </div>
              <span className="rounded-full border border-emerald-500/30 bg-emerald-500/10 px-3 py-1 font-mono text-xs text-emerald-300">
                {selectedToneObj.title} · {language.toUpperCase()}
              </span>
            </div>

            {/* Live LinkedIn Mockup Card */}
            <div className="rounded-3xl border border-white/15 bg-zinc-950 p-6 shadow-2xl space-y-4">
              {/* Author Header */}
              <div className="flex items-center justify-between border-b border-white/10 pb-4">
                <div className="flex items-center gap-3">
                  <div className="size-10 rounded-full bg-emerald-500/20 border border-emerald-500/30 flex items-center justify-center text-emerald-300 font-bold text-sm">
                    {displayName.slice(0, 2).toUpperCase()}
                  </div>
                  <div>
                    <p className="font-bold text-sm text-white">{displayName}</p>
                    <p className="text-xs text-zinc-400">{roleTitle} · 🌐 LinkedIn</p>
                  </div>
                </div>
                <span className="text-[10px] font-mono px-2.5 py-1 rounded-full bg-white/5 border border-white/10 text-zinc-400">
                  Voz: {selectedToneObj.title}
                </span>
              </div>

              {/* Generated Content Body */}
              <div className="font-mono text-xs leading-relaxed text-zinc-200 space-y-3">
                <p className="font-bold text-white text-sm">
                  🚀 Optimización de Consultas Reactivas con Índices Compuestos en Convex
                </p>

                <p className="text-zinc-300">
                  {selectedToneObj.sampleHook}
                </p>

                <div className="p-3.5 rounded-2xl bg-black/60 border border-white/10 space-y-2">
                  <p className="text-zinc-300">
                    <strong className="text-emerald-300">El desafío:</strong> Al escalar el aislamiento multi-inquilino, el escaneo de tablas empezó a degradar la reactividad en eventos de push masivos.
                  </p>
                  <p className="text-zinc-300">
                    <strong className="text-sky-300">La solución técnica:</strong> Implementamos índices compuestos <code className="text-emerald-400 bg-white/5 px-1 rounded font-mono">by_user_full_name</code> y validación criptográfica de sesión antes del acceso a datos.
                  </p>
                  {includeMetrics && (
                    <p className="text-zinc-300">
                      <strong className="text-amber-300">Métrica:</strong> 0% de fuga de datos en 55 tests de integración continua y reducción del tiempo de respuesta a &lt;15ms.
                    </p>
                  )}
                  {includeCodeSnippets && (
                    <div className="p-2.5 rounded-xl bg-black/90 border border-white/10 font-mono text-[11px] text-emerald-400">
                      {"// Schema compound index"}<br/>
                      .index(&quot;by_user_full_name&quot;, [&quot;userId&quot;, &quot;fullName&quot;])
                    </div>
                  )}
                  <p className="text-zinc-300">
                    <strong className="text-purple-300">Aprendizaje:</strong> La reactividad solo escala cuando los índices reflejan exactamente el patrón de acceso de la UI.
                  </p>
                </div>

                {/* CTA Rendering */}
                <p className="text-zinc-300 pt-1">
                  {preferredCTA === "discussion_question"
                    ? "¿Cómo abordan ustedes el aislamiento multi-tenant en arquitecturas serverless reactivas?"
                    : preferredCTA === "lesson_takeaway"
                      ? "📌 Conclusión: Medir el impacto real y aislar responsabilidades antes de optimizar la capa de transporte."
                      : preferredCTA === "github_link"
                        ? "🔗 Puedes ver el commit y los tests de aislamiento en el repositorio público."
                        : preferredCTA === "custom_cta"
                          ? customCTA
                          : ""}
                </p>

                <p className="text-emerald-400 font-semibold pt-1">
                  {hashtags.join(" ")}
                </p>
              </div>
            </div>

            {/* CTA & Hashtags tuning */}
            <div className="grid gap-4 sm:grid-cols-2">
              <div>
                <label className="block text-xs font-medium text-zinc-300">
                  Llamada a la Acción (CTA) Final
                </label>
                <select
                  value={preferredCTA}
                  onChange={(e) => setOverridePreferredCTA(e.target.value as CTAKey)}
                  className="mt-1.5 w-full rounded-xl border border-white/10 bg-black/40 px-3.5 py-2.5 text-sm text-white focus:outline-none"
                >
                  <option value="discussion_question">Pregunta para debate técnico en comentarios</option>
                  <option value="lesson_takeaway">Conclusión / Regla de oro de ingeniería</option>
                  <option value="github_link">Enlace al commit de GitHub</option>
                  <option value="custom_cta">Texto personalizado libre</option>
                  <option value="none">Sin CTA (Solo la historia técnica)</option>
                </select>

                {preferredCTA === "custom_cta" && (
                  <input
                    type="text"
                    value={customCTA}
                    onChange={(e) => setOverrideCustomCTA(e.target.value)}
                    placeholder="Escribe tu llamada a la acción personalizada..."
                    className="mt-2 w-full rounded-xl border border-white/10 bg-black/40 px-3.5 py-2 text-xs text-white focus:outline-none"
                  />
                )}
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
                  placeholder="#SoftwareEngineering, #Architecture, #ProofOfWork"
                  className="mt-1.5 w-full rounded-xl border border-white/10 bg-black/40 px-3.5 py-2.5 text-sm text-white focus:outline-none"
                />
              </div>
            </div>

            {/* WhatsApp Validation Bot Banner */}
            <div className="rounded-2xl border border-emerald-500/30 bg-emerald-950/20 p-4 space-y-3">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-3">
                  <div className="flex size-8 items-center justify-center rounded-lg bg-emerald-500/20 text-emerald-400">
                    <Phone className="size-4" />
                  </div>
                  <div>
                    <p className="text-xs font-semibold text-white">Validación de Aprobación por WhatsApp</p>
                    <p className="text-[11px] text-zinc-400">
                      Debes hablarle primero al bot oficial para abrir la ventana de 24h y recibir borradores interactivos.
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

        {step < 4 ? (
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
            {saving ? "Guardando..." : savedSuccess ? "¡Voz Editorial Guardada!" : "Guardar y Activar Personalización"}
            <CheckCircle2 className="size-4" />
          </button>
        )}
      </div>
    </div>
  );
}
