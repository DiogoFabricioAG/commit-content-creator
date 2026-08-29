"use client";

import { ConvexProvider, ConvexReactClient } from "convex/react";
import { useMemo, type ReactNode } from "react";

type ProvidersProps = {
  children: ReactNode;
};

export function Providers({ children }: ProvidersProps) {
  const convexUrl =
    process.env.NEXT_PUBLIC_CONVEX_URL || "https://tremendous-kangaroo-148.convex.cloud";
  const client = useMemo(() => new ConvexReactClient(convexUrl), [convexUrl]);

  return <ConvexProvider client={client}>{children}</ConvexProvider>;
}

