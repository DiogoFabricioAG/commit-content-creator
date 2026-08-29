"use client";

import { useQuery } from "convex/react";
import { ArrowUpRight, BookOpen, MessageSquare, Sparkles } from "lucide-react";
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


  if (!stories || stories.length === 0) {
    return (
      <div className="rounded-3xl border border-[var(--line)] bg-white/[0.02] p-8 text-center">
        <Sparkles className="mx-auto size-10 text-[var(--accent-soft)]/40" />
        <h3 className="mt-4 text-base font-semibold">Ninguna historia detectada aún</h3>
        <p className="mt-1 text-sm text-[var(--muted)]">
          Realiza un push a tu repositorio o ejecuta la demo para agrupar cambios relacionados en historias.
        </p>
      </div>
    );
  }

  const latestStory = stories[0];
  const latestPost = posts?.[0];

  return (
    <div className="space-y-6">
      {/* Story Narrative Box */}
      <div className="rounded-3xl border border-[var(--line)] bg-white/[0.035] p-6 shadow-xl">
        <div className="flex items-start justify-between border-b border-[var(--line)] pb-4">
          <div className="flex items-center gap-2">
            <BookOpen className="size-4 text-[var(--accent-soft)]" />
            <span className="font-mono text-xs uppercase tracking-wider text-[var(--muted)]">
              Historia detectada
            </span>
          </div>
          <span className="rounded-full border border-emerald-500/30 bg-emerald-500/10 px-2.5 py-0.5 font-mono text-xs text-emerald-300">
            {Math.round(latestStory.confidence * 100)}% Confianza
          </span>
        </div>

        <div className="mt-4">
          <h3 className="text-xl font-semibold tracking-tight">{latestStory.title}</h3>
          <p className="mt-2 text-sm leading-relaxed text-[var(--muted)]">{latestStory.summary}</p>
        </div>

        <div className="mt-6 grid gap-3 sm:grid-cols-2">
          <div className="rounded-2xl border border-[var(--line)] bg-black/20 p-3.5">
            <p className="text-xs font-semibold text-rose-300">Problema detectado</p>
            <p className="mt-1 text-xs text-[var(--muted)] leading-normal">{latestStory.problem}</p>
          </div>
          <div className="rounded-2xl border border-[var(--line)] bg-black/20 p-3.5">
            <p className="text-xs font-semibold text-emerald-300">Solución aplicada</p>
            <p className="mt-1 text-xs text-[var(--muted)] leading-normal">{latestStory.solution}</p>
          </div>
        </div>

        {latestStory.learning ? (
          <div className="mt-3 rounded-2xl border border-[var(--line)] bg-black/20 p-3.5">
            <p className="text-xs font-semibold text-sky-300">Aprendizaje clave</p>
            <p className="mt-1 text-xs text-[var(--muted)] leading-normal">{latestStory.learning}</p>
          </div>
        ) : null}
      </div>

      {/* LinkedIn Post & Approval State */}
      {latestPost ? (
        <div className="rounded-3xl border border-[var(--line)] bg-white/[0.035] p-6 shadow-xl">
          <div className="flex items-center justify-between border-b border-[var(--line)] pb-4">
            <div className="flex items-center gap-2">
              <MessageSquare className="size-4 text-emerald-400" />
              <span className="font-mono text-xs uppercase tracking-wider text-[var(--muted)]">
                Borrador LinkedIn & WhatsApp
              </span>
            </div>
            <span
              className={`rounded-full px-2.5 py-0.5 font-mono text-xs uppercase tracking-wider ${
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
                  : "Esperando Aprobación"}
            </span>
          </div>

          <div className="mt-4">
            <div className="rounded-2xl border border-[var(--line)] bg-black/30 p-4 font-mono text-xs leading-relaxed whitespace-pre-line text-zinc-300">
              {latestPost.format} · Borrador generado
            </div>
          </div>

          {latestPost.externalPostUrn ? (
            <div className="mt-4 flex items-center justify-between rounded-2xl border border-emerald-500/30 bg-emerald-500/10 p-3.5">
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
                Ver en LinkedIn <ArrowUpRight className="size-3.5" />
              </a>
            </div>
          ) : null}
        </div>
      ) : null}
    </div>
  );
}
