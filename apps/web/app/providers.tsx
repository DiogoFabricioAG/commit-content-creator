"use client";

import { ConvexProvider, ConvexReactClient } from "convex/react";
import { useMemo, type ReactNode } from "react";

import { AuthProvider } from "../contexts/auth-context";

type ProvidersProps = {
  children: ReactNode;
};

const DEFAULT_CONVEX_URL = "https://tremendous-kangaroo-148.convex.cloud";

export function Providers({ children }: ProvidersProps) {
  const client = useMemo(() => {
    let url = process.env.NEXT_PUBLIC_CONVEX_URL;
    if (!url || typeof url !== "string" || !url.startsWith("http")) {
      url = DEFAULT_CONVEX_URL;
    }
    try {
      return new ConvexReactClient(url);
    } catch {
      return new ConvexReactClient(DEFAULT_CONVEX_URL);
    }
  }, []);

  return (
    <ConvexProvider client={client}>
      <AuthProvider>{children}</AuthProvider>
    </ConvexProvider>
  );
}

