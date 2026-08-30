"use client";

import {
  createContext,
  useCallback,
  useContext,
  useEffect,
  useState,
  type ReactNode,
} from "react";
import { useQuery } from "convex/react";
import { api } from "@convex/api";
import type { Id } from "@convex/dataModel";

type UserDoc = {
  _id: Id<"users">;
  displayName?: string;
  email?: string;
  whatsappPhone?: string;
  createdAt: number;
  updatedAt: number;
};

type AuthContextType = {
  userId: Id<"users"> | null;
  user: UserDoc | null | undefined;
  isLoading: boolean;
  isAuthenticated: boolean;
  requestPhoneVerification: (phone: string, displayName?: string) => Promise<void>;
  verifyPhoneCode: (code: string) => Promise<Id<"users">>;
  logout: () => void;
};

const AuthContext = createContext<AuthContextType | undefined>(undefined);
const API_BASE_URL = (process.env.NEXT_PUBLIC_API_URL || "").replace(/\/$/, "");

export function AuthProvider({ children }: { children: ReactNode }) {
  const [userId, setUserId] = useState<Id<"users"> | null>(null);
  const [sessionReady, setSessionReady] = useState(false);

  useEffect(() => {
    let mounted = true;

    const loadSession = async () => {
      try {
        const response = await fetch(`${API_BASE_URL}/auth/session/me`, {
          credentials: "include",
        });
        if (!response.ok) return;
        const data = (await response.json()) as { userId?: string };
        if (mounted && data.userId) {
          setUserId(data.userId as Id<"users">);
        }
      } catch {
        // An absent session is expected on the public login page.
      } finally {
        if (mounted) setSessionReady(true);
      }
    };

    void loadSession();
    return () => {
      mounted = false;
    };
  }, []);

  const user = useQuery(
    api.users.getById,
    userId ? { userId } : "skip",
  ) as UserDoc | null | undefined;

  const requestPhoneVerification = useCallback(
    async (phone: string, displayName?: string) => {
      const response = await fetch(`${API_BASE_URL}/auth/session/login`, {
        method: "POST",
        credentials: "include",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          phone: phone.trim(),
          displayName: displayName?.trim() || undefined,
        }),
      });

      const data = (await response.json().catch(() => ({}))) as {
        detail?: string;
        message?: string;
      };
      if (!response.ok) {
        throw new Error(data.detail || "No se pudo enviar el código de WhatsApp");
      }
    },
    [],
  );

  const verifyPhoneCode = useCallback(async (code: string) => {
    const response = await fetch(`${API_BASE_URL}/auth/session/verify`, {
      method: "POST",
      credentials: "include",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ code: code.trim() }),
    });

    const data = (await response.json().catch(() => ({}))) as {
      detail?: string;
      userId?: string;
    };
    if (!response.ok) {
      throw new Error(data.detail || "El código de WhatsApp no es válido");
    }
    if (!data.userId) throw new Error("El backend no devolvió una sesión válida");

    const newUserId = data.userId as Id<"users">;
    setUserId(newUserId);
    return newUserId;
  }, []);

  const logout = useCallback(() => {
    void fetch(`${API_BASE_URL}/auth/session/logout`, {
      method: "POST",
      credentials: "include",
    }).catch(() => undefined);
    setUserId(null);
  }, []);

  const value: AuthContextType = {
    userId,
    user: userId ? user : null,
    isLoading: !sessionReady || (!!userId && user === undefined),
    isAuthenticated: !!userId && !!user,
    requestPhoneVerification,
    verifyPhoneCode,
    logout,
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error("useAuth must be used within an AuthProvider");
  }
  return context;
}
