"use client";
import { authClient } from "@/lib/auth-client";

export function useAuth() {
  const session = authClient.useSession();

  const signUp = async (email: string, password: string, name: string) => {
    return await authClient.signUp.email({ email, password, name });
  };

  const signIn = async (email: string, password: string) => {
    return await authClient.signIn.email({ email, password });
  };

  const signOut = async () => {
    return await authClient.signOut();
  };

  const getToken = async (): Promise<string | null> => {
    const { data } = await authClient.token();
    return data?.token ?? null;
  };

  return {
    session: session.data,
    isLoading: session.isPending,
    isAuthenticated: !!session.data,
    signUp,
    signIn,
    signOut,
    getToken,
  };
}
