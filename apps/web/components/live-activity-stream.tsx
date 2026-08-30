"use client";

import { useQuery } from "convex/react";
import { Activity, CheckCircle2, Clock, PlayCircle, XCircle } from "lucide-react";
import { api } from "@convex/api";
import type { Doc, Id } from "@convex/dataModel";

type LiveActivityStreamProps = {
  userId?: Id<"users">;
};

export function LiveActivityStream({ userId }: LiveActivityStreamProps) {
  // If no specific userId, query using the default user
  const defaultUser = useQuery(api.users.getByWhatsappPhone, {
    whatsappPhone: "+51999888777",
  });

  const activeUserId = userId ?? defaultUser?._id;
  const activities = useQuery(
    api.activity.listRecent,
    activeUserId ? { userId: activeUserId, limit: 12 } : "skip",
  );


  if (!activities || activities.length === 0) {
    return (
      <div className="rounded-2xl border border-[var(--line)] bg-black/10 p-6 text-center">
        <Activity className="mx-auto size-8 text-[var(--muted)]/50" />
        <p className="mt-3 text-sm font-medium">Esperando eventos en vivo</p>
        <p className="mt-1 text-xs text-[var(--muted)]">
          Los eventos de GitHub, análisis técnico y WhatsApp aparecerán aquí en tiempo real.
        </p>
      </div>
    );
  }

  return (
    <div className="space-y-2.5 max-h-[580px] overflow-y-auto custom-scrollbar pr-1.5">
      {activities.map((act: Doc<"activityEvents">) => {
        const isCompleted = act.status === "completed";
        const isStarted = act.status === "started";
        const isFailed = act.status === "failed";

        return (
          <div
            key={act._id}
            className="flex items-start justify-between gap-3 rounded-2xl border border-[var(--line)] bg-black/10 p-3.5 transition hover:bg-black/20"
          >
            <div className="flex items-start gap-3">
              <div className="mt-0.5 flex size-6 shrink-0 items-center justify-center rounded-lg bg-white/[0.05]">
                {isCompleted ? (
                  <CheckCircle2 className="size-3.5 text-emerald-400" />
                ) : isStarted ? (
                  <PlayCircle className="size-3.5 text-sky-400 animate-pulse" />
                ) : isFailed ? (
                  <XCircle className="size-3.5 text-rose-400" />
                ) : (
                  <Clock className="size-3.5 text-amber-400" />
                )}
              </div>
              <div>
                <p className="text-sm font-medium leading-snug">{act.label}</p>
                <div className="mt-1 flex items-center gap-2 text-[11px] font-mono text-[var(--muted)]">
                  <span>{act.type}</span>
                  <span>·</span>
                  <span>{new Date(act.timestamp).toLocaleTimeString()}</span>
                </div>
              </div>
            </div>
            <span
              className={`rounded-full px-2 py-0.5 font-mono text-[10px] font-medium uppercase tracking-wider ${
                isCompleted
                  ? "border border-emerald-500/20 bg-emerald-500/10 text-emerald-300"
                  : isStarted
                    ? "border border-sky-500/20 bg-sky-500/10 text-sky-300"
                    : isFailed
                      ? "border border-rose-500/20 bg-rose-500/10 text-rose-300"
                      : "border border-amber-500/20 bg-amber-500/10 text-amber-300"
              }`}
            >
              {act.status}
            </span>
          </div>
        );
      })}
    </div>
  );
}
