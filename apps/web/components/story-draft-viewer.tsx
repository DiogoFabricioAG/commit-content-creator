"use client";

import { useState } from "react";
import { useQuery } from "convex/react";
import {
  ArrowUpRight,
  BookOpen,
  Check,
  Copy,
  GitBranch,
  History,
  MessageSquare,
  Sparkles,
} from "lucide-react";
import { api } from "@convex/api";
import type { Id } from "@convex/dataModel";

type StoryDraftViewerProps = {
  userId?: Id<"users">;
};

export function StoryDraftViewer({ userId }: StoryDraftViewerProps) {
  const defaultUser = useQuery(api.users.getByWhatsappPhone, {
    whatsappPhone: "+51999888777",
  });

  const activeUserId = userId ?? defaultUser?._id;
  const stories = useQuery(
    api.stories.listForUser,
    activeUserId ? { userId: activeUserId, limit: 5 } : "skip",
  );
  const posts = useQuery(
    api.posts.listForUser,
    activeUserId ? { userId: activeUserId, limit: 5 } : "skip",
  );
  const prefs = useQuery(
    api.preferences.getForUser,
    activeUserId ? { userId: activeUserId } : "skip",
  );

  const [copied, setCopied] = useState(false);
  const [selectedStoryIndex, setSelectedStoryIndex] = useState(0);

  const activeStory = stories?.[selectedStoryIndex] ?? stories?.[0];
  const latestPost = posts?.[0];

  const latestPostVersion = useQuery(
    api.postVersions.getLatestForPost,
    latestPost?._id ? { postId: latestPost._id } : "skip",
  );

  const allPostVersions = useQuery(
    api.postVersions.listForPost,
    latestPost?._id ? { postId: latestPost._id } : "skip",
  );

  const copyToClipboard = (text: string) => {
    navigator.clipboard.writeText(text);
    setCopied(true);
    setTimeout(() => setCopied(false), 2500);
  };

  if (!stories || stories.length === 0) {
    return (
      <div className="rounded-3xl border border-white/10 bg-white/[0.02] p-10 text-center shadow-xl">
        <div className="mx-auto flex size-12 items-center justify-center rounded-2xl bg-emerald-500/10 text-emerald-400">
          <Sparkles className="size-6" />
        </div>
        <h3 className="mt-4 text-base font-semibold text-white">Ninguna historia técnica detectada aún</h3>
        <p className="mt-1.5 text-xs text-zinc-400 max-w-md mx-auto">
          Haz un push de código a tus repositorios configurados. LaborIN agrupará los commits relacionados y generará borradores automáticamente.
        </p>
        <div className="mt-6 inline-flex items-center gap-2 rounded-full border border-white/10 bg-white/5 px-3 py-1 text-[11px] text-zinc-400 font-mono">
          <GitBranch className="size-3 text-emerald-400" />
          Escuchando commits en tiempo real
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Story Selector if multiple stories */}
      {stories.length > 1 && (
        <div className="flex items-center gap-2 overflow-x-auto pb-1">
          {stories.map((s: { _id: string; title: string }, idx: number) => (
            <button
              key={s._id}
              type="button"
              onClick={() => setSelectedStoryIndex(idx)}
              className={`rounded-xl px-3 py-1.5 text-xs font-semibold whitespace-nowrap transition border ${
                selectedStoryIndex === idx
                  ? "border-emerald-400 bg-emerald-500/10 text-emerald-300 shadow-sm"
                  : "border-white/10 bg-black/40 text-zinc-400 hover:border-white/20 hover:text-white"
              }`}
            >
              Historia #{idx + 1}: {s.title.slice(0, 24)}...
            </button>
          ))}
        </div>
      )}

      {/* Story Narrative Box */}
      {activeStory && (
        <div className="rounded-3xl border border-white/10 bg-white/[0.035] p-6 shadow-xl space-y-4">
          <div className="flex items-center justify-between border-b border-white/10 pb-4">
            <div className="flex items-center gap-2">
              <BookOpen className="size-4 text-emerald-400" />
              <span className="font-mono text-xs uppercase tracking-wider text-zinc-400">
                Evidencia de Commits · {activeStory.storyType}
              </span>
            </div>
            <div className="flex items-center gap-2">
              <span className="rounded-full border border-emerald-500/30 bg-emerald-500/10 px-2.5 py-0.5 font-mono text-xs text-emerald-300">
                {Math.round(activeStory.confidence * 100)}% Confianza
              </span>
            </div>
          </div>

          <div>
            <h3 className="text-xl font-bold tracking-tight text-white">{activeStory.title}</h3>
            <p className="mt-2 text-xs leading-relaxed text-zinc-300">{activeStory.summary}</p>
          </div>

          <div className="grid gap-3 sm:grid-cols-2">
            <div className="rounded-2xl border border-white/10 bg-black/30 p-3.5">
              <p className="text-xs font-semibold text-rose-300 flex items-center gap-1.5">
                <span className="size-1.5 rounded-full bg-rose-400" /> Problema detectado
              </p>
              <p className="mt-1 text-xs text-zinc-400 leading-normal">{activeStory.problem || "Resolver necesidad técnica concreta"}</p>
            </div>
            <div className="rounded-2xl border border-white/10 bg-black/30 p-3.5">
              <p className="text-xs font-semibold text-emerald-300 flex items-center gap-1.5">
                <span className="size-1.5 rounded-full bg-emerald-400" /> Solución aplicada
              </p>
              <p className="mt-1 text-xs text-zinc-400 leading-normal">{activeStory.solution || "Implementación verificada"}</p>
            </div>
          </div>

          {activeStory.learning && (
            <div className="rounded-2xl border border-white/10 bg-black/30 p-3.5">
              <p className="text-xs font-semibold text-sky-300 flex items-center gap-1.5">
                <span className="size-1.5 rounded-full bg-sky-400" /> Aprendizaje clave
              </p>
              <p className="mt-1 text-xs text-zinc-400 leading-normal">{activeStory.learning}</p>
            </div>
          )}
        </div>
      )}

      {/* LinkedIn Post & Approval State */}
      {latestPost && (
        <div className="rounded-3xl border border-white/10 bg-[#09090b]/90 p-6 shadow-xl space-y-4">
          <div className="flex flex-wrap items-center justify-between border-b border-white/10 pb-4 gap-2">
            <div className="flex items-center gap-2">
              <MessageSquare className="size-4 text-emerald-400" />
              <span className="font-mono text-xs uppercase tracking-wider text-zinc-400">
                Borrador LinkedIn
              </span>
              {latestPostVersion && (
                <span className="rounded-md border border-white/10 bg-white/5 px-2 py-0.5 font-mono text-[10px] text-zinc-400">
                  v{latestPostVersion.version}
                </span>
              )}
            </div>

            <div className="flex items-center gap-2">
              <span
                className={`rounded-full px-2.5 py-0.5 font-mono text-[11px] uppercase tracking-wider ${
                  latestPost.status === "published"
                    ? "border border-emerald-500/30 bg-emerald-500/10 text-emerald-300"
                    : latestPost.status === "approved"
                      ? "border border-sky-500/30 bg-sky-500/10 text-sky-300"
                      : "border border-amber-500/30 bg-amber-500/10 text-amber-300"
                }`}
              >
                {latestPost.status === "published"
                  ? "Publicado en LinkedIn"
                  : latestPost.status === "approved"
                    ? "Aprobado por WhatsApp"
                    : "Esperando Aprobación WhatsApp"}
              </span>

              {latestPostVersion?.body && (
                <button
                  type="button"
                  onClick={() => copyToClipboard(latestPostVersion.body)}
                  className="inline-flex items-center gap-1.5 rounded-xl border border-white/10 bg-white/5 px-3 py-1 text-xs font-semibold text-zinc-300 hover:bg-white/10 hover:text-white transition"
                  title="Copiar borrador"
                >
                  {copied ? <Check className="size-3 text-emerald-400" /> : <Copy className="size-3" />}
                  <span>{copied ? "Copiado" : "Copiar"}</span>
                </button>
              )}
            </div>
          </div>

          {/* Active Voice Badges */}
          {prefs && (
            <div className="flex flex-wrap items-center gap-1.5 text-[11px] text-zinc-400">
              <span className="font-semibold text-zinc-500">Voz activa:</span>
              <span className="rounded-md border border-emerald-500/20 bg-emerald-500/10 px-2 py-0.5 font-mono text-emerald-300">
                {prefs.tone}
              </span>
              <span className="rounded-md border border-white/10 bg-white/5 px-2 py-0.5 font-mono text-zinc-300">
                {prefs.targetAudience}
              </span>
              <span className="rounded-md border border-white/10 bg-white/5 px-2 py-0.5 font-mono text-zinc-300">
                {prefs.language.toUpperCase()}
              </span>
            </div>
          )}

          {/* Post Content Display */}
          {latestPostVersion ? (
            <div className="rounded-2xl border border-white/10 bg-black/60 p-5 font-mono text-xs leading-relaxed whitespace-pre-line text-zinc-200 shadow-inner">
              {latestPostVersion.body}
            </div>
          ) : (
            <div className="rounded-2xl border border-white/10 bg-black/30 p-5 font-mono text-xs text-zinc-400">
              {latestPost.format} · Generando versión con IA...
            </div>
          )}

          {/* Version History Chips if multiple */}
          {allPostVersions && allPostVersions.length > 1 && (
            <div className="flex items-center gap-2 pt-2 border-t border-white/5">
              <History className="size-3.5 text-zinc-500" />
              <span className="text-[11px] text-zinc-500">Historial de iteraciones:</span>
              <div className="flex items-center gap-1.5">
                {allPostVersions.map((v: { _id: string; version: number; createdAt: number }) => (
                  <span
                    key={v._id}
                    className="rounded-md border border-white/10 bg-white/5 px-2 py-0.5 text-[10px] font-mono text-zinc-400"
                  >
                    v{v.version} ({new Date(v.createdAt).toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" })})
                  </span>
                ))}
              </div>
            </div>
          )}

          {/* Published Link if available */}
          {latestPost.externalPostUrn && (
            <div className="flex items-center justify-between rounded-2xl border border-emerald-500/30 bg-emerald-500/10 p-3.5">
              <div className="flex items-center gap-2">
                <span className="size-2 rounded-full bg-emerald-400 animate-pulse" />
                <span className="font-mono text-xs text-emerald-200">
                  URN: {latestPost.externalPostUrn}
                </span>
              </div>
              <a
                href={`https://linkedin.com/feed/update/${latestPost.externalPostUrn}`}
                target="_blank"
                rel="noreferrer"
                className="inline-flex items-center gap-1 text-xs font-semibold text-emerald-300 hover:underline"
              >
                Ver publicación en LinkedIn <ArrowUpRight className="size-3.5" />
              </a>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
