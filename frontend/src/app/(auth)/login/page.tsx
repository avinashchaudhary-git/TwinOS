"use client";

import React, { useState } from "react";
import { useRouter } from "next/navigation";
import { loginAsDevUser, setStoredToken, DEMO_USERS } from "@/lib/auth";
import { Sparkles, ShieldCheck, UserCheck, Key, ArrowRight } from "lucide-react";

export default function LoginPage() {
  const router = useRouter();
  const [customEmail, setCustomEmail] = useState("");
  const [firebaseToken, setFirebaseToken] = useState("");
  const [activeTab, setActiveTab] = useState<"dev" | "firebase">("dev");

  const handleSelectDevUser = (email: string) => {
    loginAsDevUser(email);
    router.push("/dashboard");
    router.refresh();
  };

  const handleCustomDevSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!customEmail.trim()) return;
    loginAsDevUser(customEmail.trim());
    router.push("/dashboard");
    router.refresh();
  };

  const handleFirebaseSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!firebaseToken.trim()) return;
    setStoredToken(firebaseToken.trim());
    router.push("/dashboard");
    router.refresh();
  };

  return (
    <div className="min-h-[80vh] flex items-center justify-center py-12 px-4">
      <div className="max-w-md w-full space-y-8 glass-panel p-8 rounded-3xl border border-slate-800 shadow-2xl relative overflow-hidden">
        {/* Glow accent */}
        <div className="absolute -top-24 -left-24 w-48 h-48 bg-indigo-500/20 rounded-full blur-3xl pointer-events-none" />
        <div className="absolute -bottom-24 -right-24 w-48 h-48 bg-cyan-500/20 rounded-full blur-3xl pointer-events-none" />

        {/* Brand */}
        <div className="text-center">
          <div className="w-14 h-14 mx-auto rounded-2xl bg-gradient-to-tr from-indigo-600 to-cyan-400 p-0.5 flex items-center justify-center shadow-xl shadow-indigo-500/25 mb-4">
            <div className="w-full h-full bg-[#090d16] rounded-[14px] flex items-center justify-center">
              <Sparkles className="w-7 h-7 text-indigo-400" />
            </div>
          </div>
          <h2 className="text-2xl font-extrabold text-white tracking-tight">TwinOS Login</h2>
          <p className="mt-1 text-xs text-slate-400">
            Enterprise Digital Twin Synthesis & Predictive Risk Layer
          </p>
        </div>

        {/* Tab Selection */}
        <div className="flex rounded-xl bg-slate-900/80 p-1 border border-slate-800">
          <button
            onClick={() => setActiveTab("dev")}
            className={`flex-1 py-1.5 rounded-lg text-xs font-semibold transition flex items-center justify-center gap-1.5 ${
              activeTab === "dev" ? "bg-indigo-600 text-white shadow-md" : "text-slate-400 hover:text-white"
            }`}
          >
            <UserCheck className="w-3.5 h-3.5" />
            Dev Mode Profiles
          </button>
          <button
            onClick={() => setActiveTab("firebase")}
            className={`flex-1 py-1.5 rounded-lg text-xs font-semibold transition flex items-center justify-center gap-1.5 ${
              activeTab === "firebase" ? "bg-indigo-600 text-white shadow-md" : "text-slate-400 hover:text-white"
            }`}
          >
            <Key className="w-3.5 h-3.5" />
            Firebase Token
          </button>
        </div>

        {activeTab === "dev" ? (
          <div className="space-y-4">
            <div className="text-xs font-semibold text-slate-400 uppercase tracking-wider">
              Select Demo Role Persona
            </div>

            <div className="space-y-2.5">
              {DEMO_USERS.map((u) => (
                <button
                  key={u.email}
                  onClick={() => handleSelectDevUser(u.email)}
                  className="w-full p-3.5 rounded-2xl glass-card hover:border-indigo-500/50 hover:bg-slate-800/80 transition text-left flex items-center justify-between group cursor-pointer border border-slate-700/60"
                >
                  <div className="flex items-center gap-3">
                    <div className="w-9 h-9 rounded-xl bg-indigo-500/20 text-indigo-300 border border-indigo-500/40 flex items-center justify-center font-bold text-xs shrink-0">
                      {u.avatar}
                    </div>
                    <div>
                      <div className="text-xs font-bold text-white group-hover:text-indigo-400 transition">
                        {u.name}
                      </div>
                      <div className="text-[11px] text-slate-400">{u.title}</div>
                    </div>
                  </div>
                  <div className="flex items-center gap-2">
                    <span className="text-[10px] font-mono px-2 py-0.5 rounded-full uppercase font-bold bg-slate-800 text-indigo-300 border border-slate-700">
                      {u.role}
                    </span>
                    <ArrowRight className="w-4 h-4 text-slate-500 group-hover:text-indigo-400 group-hover:translate-x-0.5 transition" />
                  </div>
                </button>
              ))}
            </div>

            {/* Custom Dev Email Form */}
            <form onSubmit={handleCustomDevSubmit} className="pt-2">
              <label className="block text-[11px] font-semibold text-slate-400 mb-1">
                Or enter any seeded email:
              </label>
              <div className="flex gap-2">
                <input
                  type="email"
                  placeholder="e.g. charlie.davis@acme.org"
                  value={customEmail}
                  onChange={(e) => setCustomEmail(e.target.value)}
                  className="flex-1 bg-slate-900 border border-slate-700 rounded-xl px-3 py-2 text-xs text-white placeholder-slate-500 focus:outline-none focus:border-indigo-500"
                />
                <button
                  type="submit"
                  className="px-3.5 py-2 rounded-xl bg-slate-800 hover:bg-slate-700 text-xs font-semibold text-white transition border border-slate-700"
                >
                  Sign In
                </button>
              </div>
            </form>
          </div>
        ) : (
          <form onSubmit={handleFirebaseSubmit} className="space-y-4">
            <div>
              <label className="block text-xs font-semibold text-slate-300 mb-1">
                Firebase ID Token (JWT)
              </label>
              <textarea
                rows={4}
                placeholder="eyJhbGciOiJSUzI1NiIsImtpZCI6..."
                value={firebaseToken}
                onChange={(e) => setFirebaseToken(e.target.value)}
                className="w-full bg-slate-900 border border-slate-700 rounded-xl p-3 text-xs text-white placeholder-slate-500 font-mono focus:outline-none focus:border-indigo-500"
              />
              <p className="text-[11px] text-slate-500 mt-1">
                Paste a verified Firebase token from your client SDK to authenticate via Firebase Admin.
              </p>
            </div>
            <button
              type="submit"
              className="w-full py-2.5 rounded-xl bg-indigo-600 hover:bg-indigo-500 text-white font-semibold text-xs shadow-lg shadow-indigo-600/30 transition"
            >
              Authenticate Token
            </button>
          </form>
        )}

        <div className="pt-4 border-t border-slate-800 text-center text-[11px] text-slate-500 flex items-center justify-center gap-1.5">
          <ShieldCheck className="w-3.5 h-3.5 text-emerald-400" />
          <span>Role-Based Access Control Active</span>
        </div>
      </div>
    </div>
  );
}
