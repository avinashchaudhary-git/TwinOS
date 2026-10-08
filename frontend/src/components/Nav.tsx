"use client";

import React, { useState, useEffect } from "react";
import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";
import {
  LayoutDashboard,
  BotMessageSquare,
  Network,
  FolderGit2,
  CheckSquare,
  Bell,
  Settings,
  RefreshCw,
  UserCheck,
  ChevronDown,
  Sparkles,
} from "lucide-react";
import { SessionUser } from "@/lib/types";
import { getStoredUser, loginAsDevUser, DEMO_USERS } from "@/lib/auth";
import { api } from "@/lib/api";

export const Nav: React.FC = () => {
  const pathname = usePathname();
  const router = useRouter();
  const [user, setUser] = useState<SessionUser | null>(null);
  const [syncing, setSyncing] = useState(false);
  const [syncMsg, setSyncMsg] = useState<string | null>(null);
  const [roleMenuOpen, setRoleMenuOpen] = useState(false);
  const [alertCount, setAlertCount] = useState(0);

  useEffect(() => {
    const cur = getStoredUser();
    setUser(cur);
    // Fetch unread alerts
    api.alerts
      .list(true)
      .then((res) => setAlertCount(res.length))
      .catch(() => {});
  }, []);

  const handleSwitchUser = (email: string) => {
    const newUser = loginAsDevUser(email);
    setUser(newUser);
    setRoleMenuOpen(false);
    router.refresh();
    window.location.reload();
  };

  const handleTriggerSync = async () => {
    setSyncing(true);
    setSyncMsg(null);
    try {
      const res = await api.sync.triggerRun(true);
      setSyncMsg(res.message);
      setTimeout(() => setSyncMsg(null), 4000);
      window.location.reload();
    } catch (err: any) {
      setSyncMsg(err.message || "Sync failed");
      setTimeout(() => setSyncMsg(null), 4000);
    } finally {
      setSyncing(false);
    }
  };

  const navLinks = [
    { href: "/dashboard", label: "Dashboard", icon: LayoutDashboard, roles: ["manager", "admin"] },
    { href: "/assistant", label: "RAG Assistant", icon: BotMessageSquare, roles: ["employee", "manager", "admin"] },
    { href: "/graph", label: "Knowledge Graph", icon: Network, roles: ["employee", "manager", "admin"] },
    { href: "/projects", label: "Projects", icon: FolderGit2, roles: ["manager", "admin"] },
    { href: "/my-work", label: "My Work", icon: CheckSquare, roles: ["employee"] },
    { href: "/alerts", label: "Alerts", icon: Bell, roles: ["employee", "manager", "admin"], badge: alertCount },
    { href: "/admin/users", label: "Admin Console", icon: Settings, roles: ["admin"] },
  ];

  const visibleLinks = navLinks.filter((link) => user && link.roles.includes(user.role));

  return (
    <header className="sticky top-0 z-50 glass-panel border-b border-slate-800 bg-background/80">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
        {/* Brand */}
        <div className="flex items-center gap-8">
          <Link href="/dashboard" className="flex items-center gap-3 group">
            <div className="w-10 h-10 rounded-xl bg-gradient-to-tr from-indigo-600 via-primary-500 to-cyan-400 p-0.5 flex items-center justify-center shadow-lg shadow-indigo-500/20 group-hover:scale-105 transition">
              <div className="w-full h-full bg-[#090d16] rounded-[10px] flex items-center justify-center">
                <Sparkles className="w-5 h-5 text-indigo-400" />
              </div>
            </div>
            <div>
              <div className="text-base font-bold text-white tracking-wide flex items-center gap-1.5">
                TwinOS
                <span className="text-[10px] uppercase font-semibold px-1.5 py-0.5 rounded bg-indigo-500/20 text-indigo-300 border border-indigo-500/30">
                  v1.0
                </span>
              </div>
              <div className="text-[10px] font-medium text-slate-400 tracking-wider">
                ORGANIZATIONAL DIGITAL TWIN
              </div>
            </div>
          </Link>

          {/* Navigation Links */}
          <nav className="hidden md:flex items-center gap-1">
            {visibleLinks.map((link) => {
              const Icon = link.icon;
              const isActive = pathname.startsWith(link.href);
              return (
                <Link
                  key={link.href}
                  href={link.href}
                  className={`flex items-center gap-2 px-3.5 py-2 rounded-xl text-xs font-semibold tracking-wide transition relative ${
                    isActive
                      ? "bg-indigo-600/15 text-indigo-400 border border-indigo-500/30 shadow-inner"
                      : "text-slate-400 hover:text-slate-200 hover:bg-slate-800/60"
                  }`}
                >
                  <Icon className="w-4 h-4" />
                  <span>{link.label}</span>
                  {link.badge ? (
                    <span className="ml-1 px-1.5 py-0.2 rounded-full text-[10px] bg-rose-500 text-white font-bold">
                      {link.badge}
                    </span>
                  ) : null}
                </Link>
              );
            })}
          </nav>
        </div>

        {/* Action Controls & Role Switcher */}
        <div className="flex items-center gap-3">
          {/* Live Sync Trigger */}
          {user && ["manager", "admin"].includes(user.role) && (
            <button
              onClick={handleTriggerSync}
              disabled={syncing}
              className={`flex items-center gap-2 px-3 py-1.5 rounded-xl text-xs font-semibold border transition ${
                syncing
                  ? "bg-slate-800 border-slate-700 text-slate-400 cursor-not-allowed"
                  : "bg-indigo-600/10 hover:bg-indigo-600/20 text-indigo-300 border-indigo-500/30 hover:border-indigo-500/50"
              }`}
              title="Trigger instant sync from GitHub, Trello, Gmail & Calendar"
            >
              <RefreshCw className={`w-3.5 h-3.5 ${syncing ? "animate-spin text-indigo-400" : ""}`} />
              <span className="hidden sm:inline">{syncing ? "Syncing..." : "Sync Pipeline"}</span>
            </button>
          )}

          {/* Quick Role Switcher Dropdown */}
          <div className="relative">
            <button
              onClick={() => setRoleMenuOpen(!roleMenuOpen)}
              className="flex items-center gap-2.5 px-3 py-1.5 rounded-xl glass-card hover:bg-slate-800/80 border border-slate-700/60 text-xs transition"
            >
              <div className="w-6 h-6 rounded-lg bg-indigo-500/20 border border-indigo-500/40 text-indigo-300 flex items-center justify-center font-bold text-[10px]">
                {user?.name?.slice(0, 2).toUpperCase() || "AC"}
              </div>
              <div className="text-left hidden sm:block">
                <div className="font-semibold text-slate-200 leading-tight">{user?.name || "Alice Chen"}</div>
                <div className="text-[10px] text-indigo-400 font-mono capitalize">{user?.role || "manager"}</div>
              </div>
              <ChevronDown className="w-3.5 h-3.5 text-slate-400" />
            </button>

            {roleMenuOpen && (
              <div className="absolute right-0 mt-2 w-72 rounded-2xl glass-panel border border-slate-700 shadow-2xl p-2 z-50 animate-in fade-in slide-in-from-top-2">
                <div className="px-3 py-2 text-[11px] font-bold uppercase tracking-wider text-slate-400 border-b border-slate-800">
                  Switch Active Role (Dev Mode)
                </div>
                <div className="py-1">
                  {DEMO_USERS.map((u) => {
                    const isSelected = user?.email.toLowerCase() === u.email.toLowerCase();
                    return (
                      <button
                        key={u.email}
                        onClick={() => handleSwitchUser(u.email)}
                        className={`w-full text-left p-2.5 rounded-xl transition flex items-start gap-2.5 ${
                          isSelected ? "bg-indigo-600/20 border border-indigo-500/40" : "hover:bg-slate-800/80"
                        }`}
                      >
                        <div className="w-7 h-7 rounded-lg bg-slate-800 border border-slate-700 text-slate-300 flex items-center justify-center text-xs font-bold shrink-0">
                          {u.avatar}
                        </div>
                        <div className="flex-1 min-w-0">
                          <div className="flex items-center justify-between">
                            <span className="text-xs font-semibold text-white">{u.name}</span>
                            <span className="text-[10px] font-mono px-1.5 py-0.5 rounded uppercase font-bold bg-indigo-500/20 text-indigo-300">
                              {u.role}
                            </span>
                          </div>
                          <p className="text-[11px] text-slate-400 truncate">{u.title}</p>
                        </div>
                      </button>
                    );
                  })}
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
      {syncMsg && (
        <div className="bg-indigo-600 text-white text-xs font-medium py-1 px-4 text-center animate-in fade-in">
          {syncMsg}
        </div>
      )}
    </header>
  );
};
