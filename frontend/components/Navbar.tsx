"use client";

import { useRouter } from "next/navigation";
import { useAuth } from "@/hooks/useAuth";

export default function Navbar() {
  const { session, signOut } = useAuth();
  const router = useRouter();

  const handleSignOut = async () => {
    await signOut();
    router.push("/login");
  };

  const displayName = session?.user?.name || session?.user?.email || "User";

  return (
    <nav className="sticky top-0 z-10 flex items-center justify-between bg-white px-6 py-3 shadow">
      <h1 className="text-lg font-semibold text-gray-900">Todo App</h1>
      <div className="flex items-center gap-4">
        <span className="text-sm text-gray-600">{displayName}</span>
        <button
          onClick={handleSignOut}
          className="rounded-lg border border-gray-300 px-3 py-1.5 text-sm text-gray-700 hover:bg-gray-50 transition-colors"
        >
          Sign Out
        </button>
      </div>
    </nav>
  );
}
