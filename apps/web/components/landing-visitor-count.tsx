"use client";

import { useEffect, useState } from "react";
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
  const [registeredCount, setRegisteredCount] = useState<number | null>(null);
  const [registrationSettled, setRegistrationSettled] = useState(false);

  useEffect(() => {
    const storedVisitorId = window.localStorage.getItem(VISITOR_ID_STORAGE_KEY);
    const nextVisitorId = storedVisitorId || createVisitorId();
    if (!storedVisitorId) {
      window.localStorage.setItem(VISITOR_ID_STORAGE_KEY, nextVisitorId);
    }

    let active = true;
    void registerVisitor({ visitorId: nextVisitorId })
      .then((count) => {
        if (!active) return;
        setRegisteredCount(count);
        setRegistrationSettled(true);
      })
      .catch(() => {
        if (active) setRegistrationSettled(true);
      });

    return () => {
      active = false;
    };
  }, [registerVisitor]);

  const displayCount =
    registrationSettled && (visitorCount !== undefined || registeredCount !== null)
      ? Math.max(visitorCount ?? 0, registeredCount ?? 0)
      : null;

  return (
    <div className="inline-flex items-center gap-3 border-y border-[var(--landing-line)] py-3 text-xs text-[var(--landing-muted)]">
      <UsersRound className="size-4 text-[var(--signal)]" aria-hidden="true" />
      <span aria-busy={displayCount === null}>
        <strong
          className={`inline-block min-w-8 text-center font-mono text-sm text-[var(--landing-text)] ${
            displayCount === null ? "visitor-count-loading" : ""
          }`}
        >
          {displayCount ?? "…"}
        </strong>{" "}
        builders ya visitaron LaborIN
      </span>
      <span className="status-dot" aria-hidden="true" />
      <span className="sr-only" aria-live="polite">
        {displayCount === null
          ? "Cargando visitantes registrados"
          : `${displayCount} visitantes únicos registrados`}
      </span>
    </div>
  );
}
