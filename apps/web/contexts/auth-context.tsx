"use client";

import {
  createContext,
  useContext,
  useState,
  useCallback,
  type ReactNode,
} from "react";
import { useMutation, useQuery } from "convex/react";
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
  loginWithPhone: (phone: string, displayName?: string) => Promise<Id<"users">>;
  loginWithUserId: (id: Id<"users">) => void;
  logout: () => void;
};

const AuthContext = createContext<AuthContextType | undefined>(undefined);

const STORAGE_KEY = "laborin_session_user_id";

function getInitialUserId(): Id<"users"> | null {
  if (typeof window === "undefined") return null;
  try {
    const params = new URLSearchParams(window.location.search);
    const urlUserId = params.get("userId") as Id<"users"> | null;
    if (urlUserId) {
      localStorage.setItem(STORAGE_KEY, urlUserId);
      return urlUserId;
    }
    return (localStorage.getItem(STORAGE_KEY) as Id<"users"> | null) ?? null;
  } catch {
    return null;
  }
}

export function AuthProvider({ children }: { children: ReactNode }) {
  const [userId, setUserId] = useState<Id<"users"> | null>(getInitialUserId);
  const loginOrCreateMutation = useMutation(api.users.loginOrCreate);

  // Fetch live user document
  const user = useQuery(
    api.users.getById,
    userId ? { userId } : "skip",
  ) as UserDoc | null | undefined;

  const loginWithUserId = useCallback((id: Id<"users">) => {
    try {
      localStorage.setItem(STORAGE_KEY, id);
    } catch {}
    setUserId(id);
  }, []);

  const loginWithPhone = useCallback(
    async (phone: string, displayName?: string) => {
      const newUserId = await loginOrCreateMutation({
        whatsappPhone: phone.trim(),
        displayName: displayName?.trim() || undefined,
      });
      loginWithUserId(newUserId);
      return newUserId;
    },
    [loginOrCreateMutation, loginWithUserId],
  );

  const logout = useCallback(() => {
    try {
      localStorage.removeItem(STORAGE_KEY);
    } catch {}
    setUserId(null);
  }, []);

  const value: AuthContextType = {
    userId,
    user: userId ? user : null,
    isLoading: !!userId && user === undefined,
    isAuthenticated: !!userId && !!user,
    loginWithPhone,
    loginWithUserId,
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
