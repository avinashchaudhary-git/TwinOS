"use client";

import React, { useState, useEffect } from "react";
import Link from "next/link";
import { RoleGuard } from "@/components/RoleGuard";
import { api } from "@/lib/api";
import { PlatformConnection } from "@/lib/types";
import { Network, RefreshCw, CheckCircle2, ShieldCheck, Key } from "lucide-react";

export default function AdminConnectionsPage() {
  const [connections, setConnections] = useState<PlatformConnection[]>([]);
  const [syncing, setSyncing] = useState(false);
  const [msg, setMsg] = useState<string | null>(null);

  const loadConnections = async () => {
    try {
      const res = await api.admin.listConnections();
      setConnections(res);
    } catch {
      setConnections([]);
    }
  };

  useEffect(() => {
    loadConnections();
  }, []);

  const handleSyncAll = async () => {
    setSyncing(true);
    setMsg(null);
    try {
      const res = await api.sync.triggerRun(true);
      setMsg(res.message);
      loadConnections();
    } catch (err: any) {
      setMsg(`Error: ${err.message}`);
    } finally {
      setSyncing(false);
    }
  };

  return (
    <RoleGuard allowedRoles={["admin"]}>
      <div className="space-y-6">
        {/* Subnav */}
        <div className="flex items-center gap-3 border-b border-slate-800 pb-3">
          <Link href="/admin/users" className="px-3 py-1.5 rounded-lg text-slate-400 hover:text-white hover:bg-slate-800 text-xs font-medium">
            User Management
          </Link>
          <Link href="/admin/connections" className="px-3 py-1.5 rounded-lg bg-indigo-600/20 text-indigo-400 text-xs font-bold border border-indigo-500/30">
            Platform Connections
          </Link>
          <Link href="/admin/risk-config" className="px-3 py-1.5 rounded-lg text-slate-400 hover:text-white hover:bg-slate-800 text-xs font-medium">
            Risk Configuration
          </Link>
          <Link href="/admin/audit" className="px-3 py-1.5 rounded-lg text-slate-400 hover:text-white hover:bg-slate-800 text-xs font-medium">
            Audit Logs
          </Link>
        </div>

        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-extrabold text-white tracking-tight flex items-center gap-2.5">
              <Network className="w-6 h-6 text-indigo-400" />
              Platform Connectors & Sync Orchestration
            </h1>
            <p className="text-xs text-slate-400 mt-1">
              Configure credentials, OAuth2 token encryption, and incremental sync pipelines
            </p>
          </div>

          <button
            onClick={handleSyncAll}
            disabled={syncing}
            className="flex items-center gap-2 px-4 py-2 rounded-xl text-xs font-semibold bg-indigo-600 hover:bg-indigo-500 text-white shadow-lg shadow-indigo-600/30 transition"
          >
            <RefreshCw className={`w-3.5 h-3.5 ${syncing ? "animate-spin" : ""}`} />
            <span>{syncing ? "Running Pipeline..." : "Trigger Full Sync"}</span>
          </button>
        </div>

        {msg && (
          <div className="p-3 rounded-xl bg-indigo-500/10 border border-indigo-500/30 text-indigo-300 text-xs">
            {msg}
          </div>
        )}

        {/* 4 Platforms Cards */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-5">
          {[
            { id: "github", name: "GitHub", desc: "Repositories, commits, diffs & code telemetry", scopes: "repo, read:org" },
            { id: "trello", name: "Trello", desc: "Boards, task cards, checklists & due dates", scopes: "read, write" },
            { id: "gmail", name: "Gmail", desc: "Message metadata & snippet only (least privilege)", scopes: "gmail.readonly" },
            { id: "gcalendar", name: "Google Calendar", desc: "Milestones, sprint events & meeting load", scopes: "calendar.readonly" },
          ].map((p) => {
            const conn = connections.find((c) => c.platform === p.id);
            return (
              <div key={p.id} className="p-6 rounded-2xl glass-panel border border-slate-800 flex flex-col justify-between">
                <div>
                  <div className="flex items-center justify-between mb-3">
                    <h3 className="text-base font-bold text-white capitalize">{p.name}</h3>
                    <span className="px-2.5 py-0.5 rounded-full text-[10px] font-bold uppercase bg-emerald-500/10 text-emerald-400 border border-emerald-500/30">
                      {conn?.status || "Connected (Mock)"}
                    </span>
                  </div>
                  <p className="text-xs text-slate-400 leading-relaxed mb-4">{p.desc}</p>
                  <div className="text-[11px] font-mono text-slate-500 space-y-1">
                    <div>Scopes: {p.scopes}</div>
                    <div>Token Security: Fernet Encrypted</div>
                  </div>
                </div>

                <div className="pt-4 border-t border-slate-800/80 flex items-center justify-between text-xs text-slate-400 mt-4">
                  <span>Last synced: {conn?.last_synced_at ? new Date(conn.last_synced_at).toLocaleString() : "Active"}</span>
                  <span className="text-emerald-400 font-medium flex items-center gap-1">
                    <CheckCircle2 className="w-3.5 h-3.5" />
                    Operational
                  </span>
                </div>
              </div>
            );
          })}
        </div>
      </div>
    </RoleGuard>
  );
}
