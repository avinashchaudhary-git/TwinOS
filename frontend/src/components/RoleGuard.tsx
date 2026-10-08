"use client";

import React, { useEffect, useState } from "react";
import { Role, SessionUser } from "@/lib/types";
import { getStoredUser } from "@/lib/auth";
import { ShieldAlert } from "lucide-react";
import Link from "next/link";

interface RoleGuardProps {
  allowedRoles: Role[];
  children: React.ReactNode;
}

export const RoleGuard: React.FC<RoleGuardProps> = ({ allowedRoles, children }) => {
  const [user, setUser] = useState<SessionUser | null>(null);
  const [mounted, setMounted] = useState(false);

  useEffect(() => {
    setUser(getStoredUser());
    setMounted(true);
  }, []);

  if (!mounted) {
    return <div className="min-h-[400px] flex items-center justify-center text-slate-500">Loading permissions...</div>;
  }

  if (!user || !allowedRoles.includes(user.role)) {
    return (
      <div className="max-w-xl mx-auto my-16 p-8 rounded-2xl glass-panel border border-rose-500/30 text-center">
        <div className="w-16 h-16 mx-auto mb-4 rounded-2xl bg-rose-500/10 flex items-center justify-center text-rose-400">
          <ShieldAlert className="w-8 h-8" />
        </div>
        <h2 className="text-xl font-bold text-white mb-2">Access Restricted</h2>
        <p className="text-slate-400 text-sm mb-6 leading-relaxed">
          Your current role (<span className="text-rose-400 font-semibold">{user?.role || "guest"}</span>) does not have permission to view this page. This resource is restricted to <span className="font-semibold text-slate-200">{allowedRoles.join(" / ")}</span> roles per organizational RBAC policy.
        </p>
        <div className="flex justify-center gap-3">
          <Link
            href="/my-work"
            className="px-4 py-2 rounded-xl bg-slate-800 hover:bg-slate-700 text-white text-sm font-medium transition"
          >
            Go to My Work
          </Link>
          <Link
            href="/dashboard"
            className="px-4 py-2 rounded-xl bg-primary-600 hover:bg-primary-500 text-white text-sm font-medium transition"
          >
            Back to Dashboard
          </Link>
        </div>
      </div>
    );
  }

  return <>{children}</>;
};

export default RoleGuard;
