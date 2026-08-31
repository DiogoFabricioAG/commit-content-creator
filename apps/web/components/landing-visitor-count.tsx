"use client";

import { useEffect } from "react";
import { useMutation, useQuery } from "convex/react";
import { UsersRound } from "lucide-react";

import { api } from "@convex/api";

const VISITOR_ID_STORAGE_KEY = "laborin-landing-visitor-id";

function createVisitorId() {
  if (typeof crypto !== "undefined" && "randomUUID" in crypto) {
    return crypto.randomUUID();
  }
  return `${Date.now()}-${Math.random().toString(36).slice(2)}`;
}

export function LandingVisitorCount() {
  const visitorCount = useQuery(api.landingVisits.getVisitorCount);
  const registerVisitor = useMutation(api.landingVisits.registerVisitor);

  useEffect(() => {
    const storedVisitorId = window.localStorage.getItem(VISITOR_ID_STORAGE_KEY);
    const nextVisitorId = storedVisitorId || createVisitorId();
    if (!storedVisitorId) {
      window.localStorage.setItem(VISITOR_ID_STORAGE_KEY, nextVisitorId);
    }
    void registerVisitor({ visitorId: nextVisitorId }).catch(() => undefined);
  }, [registerVisitor]);

  return (
    <div className="inline-flex items-center gap-3 border-y border-[var(--landing-line)] py-3 text-xs text-[var(--landing-muted)]">
      <UsersRound className="size-4 text-[var(--signal)]" aria-hidden="true" />
      <span>
        <strong className="font-mono text-sm text-[var(--landing-text)]">
          {visitorCount ?? 100}
        </strong>{" "}
        builders ya visitaron LaborIN
      </span>
      <span className="status-dot" aria-hidden="true" />
      <span className="sr-only" aria-live="polite">
        {visitorCount ?? 100} visitantes únicos registrados
      </span>
    </div>
  );
}
