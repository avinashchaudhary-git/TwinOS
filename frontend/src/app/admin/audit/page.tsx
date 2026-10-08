"use client";

import React, { useEffect, useState } from "react";
import RoleGuard from "@/components/RoleGuard";
import { api } from "@/lib/api";
import { AuditLogItem } from "@/lib/types";

export default function AuditLogsPage() {
  const [logs, setLogs] = useState<AuditLogItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [filterAction, setFilterAction] = useState("");
  const [selectedLog, setSelectedLog] = useState<AuditLogItem | null>(null);

  const fetchLogs = async () => {
    setLoading(true);
    try {
      const data = await api.admin.getAuditLogs(100);
      setLogs(data);
    } catch (err) {
      console.error("Failed to load audit logs:", err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchLogs();
  }, []);

  const filteredLogs = logs.filter((log) => {
    if (!filterAction) return true;
    const query = filterAction.toLowerCase();
    return (
      log.action.toLowerCase().includes(query) ||
      (log.target_entity && log.target_entity.toLowerCase().includes(query)) ||
      (log.actor_id && log.actor_id.toLowerCase().includes(query)) ||
      (log.target_id && log.target_id.toLowerCase().includes(query))
    );
  });

  const getActionBadgeColor = (action: string) => {
    if (action.includes("create")) return "bg-emerald-500/10 text-emerald-400 border-emerald-500/20";
    if (action.includes("update") || action.includes("patch")) return "bg-cyan-500/10 text-cyan-400 border-cyan-500/20";
    if (action.includes("delete") || action.includes("fail")) return "bg-rose-500/10 text-rose-400 border-rose-500/20";
    if (action.includes("sync")) return "bg-purple-500/10 text-purple-400 border-purple-500/20";
    if (action.includes("query") || action.includes("rag")) return "bg-amber-500/10 text-amber-400 border-amber-500/20";
    return "bg-slate-700/30 text-slate-300 border-slate-700";
  };

  return (
    <RoleGuard allowedRoles={["admin"]}>
      <div className="space-y-6 max-w-6xl">
        <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
          <div>
            <h1 className="text-2xl font-bold text-white tracking-tight">Security Audit Trail</h1>
            <p className="text-sm text-slate-400 mt-1">
              Immutable ledger of administrative mutations, configuration updates, and system events.
            </p>
          </div>
          <div className="flex items-center gap-3">
            <input
              type="text"
              placeholder="Filter by action, entity, ID..."
              value={filterAction}
              onChange={(e) => setFilterAction(e.target.value)}
              className="px-3 py-1.5 rounded-lg bg-slate-900 border border-slate-700 text-xs text-white placeholder-slate-500 focus:outline-none focus:border-cyan-500 w-64"
            />
            <button
              onClick={fetchLogs}
              className="btn-secondary text-xs flex items-center gap-1.5"
            >
              <svg className="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
              </svg>
              Refresh
            </button>
          </div>
        </div>

        {/* Audit Log Table */}
        <div className="card-cyber overflow-hidden">
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs">
              <thead className="bg-slate-900/80 border-b border-slate-800 text-slate-400 font-mono uppercase tracking-wider">
                <tr>
                  <th className="px-4 py-3">Timestamp</th>
                  <th className="px-4 py-3">Action</th>
                  <th className="px-4 py-3">Actor ID</th>
                  <th className="px-4 py-3">Entity Type</th>
                  <th className="px-4 py-3">Target ID</th>
                  <th className="px-4 py-3 text-right">Details</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-800/60 font-mono">
                {loading ? (
                  <tr>
                    <td colSpan={6} className="px-4 py-8 text-center text-slate-500">
                      Loading immutable audit events...
                    </td>
                  </tr>
                ) : filteredLogs.length === 0 ? (
                  <tr>
                    <td colSpan={6} className="px-4 py-8 text-center text-slate-500">
                      No audit events matching criteria.
                    </td>
                  </tr>
                ) : (
                  filteredLogs.map((log) => (
                    <tr key={log.id} className="hover:bg-slate-800/30 transition-colors">
                      <td className="px-4 py-3 text-slate-400 whitespace-nowrap">
                        {log.timestamp ? new Date(log.timestamp).toLocaleString() : "N/A"}
                      </td>
                      <td className="px-4 py-3 whitespace-nowrap">
                        <span className={`inline-block px-2 py-0.5 rounded border text-[11px] font-semibold ${getActionBadgeColor(log.action)}`}>
                          {log.action}
                        </span>
                      </td>
                      <td className="px-4 py-3 text-cyan-400/90 whitespace-nowrap max-w-[140px] truncate" title={log.actor_id || "system"}>
                        {log.actor_id ? log.actor_id.slice(0, 12) + "..." : "system"}
                      </td>
                      <td className="px-4 py-3 text-slate-300 capitalize">
                        {log.target_entity || "-"}
                      </td>
                      <td className="px-4 py-3 text-slate-400 whitespace-nowrap max-w-[140px] truncate" title={log.target_id || "-"}>
                        {log.target_id ? log.target_id.slice(0, 12) + "..." : "-"}
                      </td>
                      <td className="px-4 py-3 text-right">
                        <button
                          onClick={() => setSelectedLog(log)}
                          className="text-cyan-400 hover:text-cyan-300 font-medium hover:underline"
                        >
                          View Meta
                        </button>
                      </td>
                    </tr>
                  ))
                )}
              </tbody>
            </table>
          </div>
        </div>

        {/* Log Detail Modal */}
        {selectedLog && (
          <div className="fixed inset-0 z-50 bg-black/75 backdrop-blur-sm flex items-center justify-center p-4">
            <div className="bg-slate-900 border border-slate-700 rounded-2xl max-w-lg w-full p-6 space-y-4 shadow-2xl">
              <div className="flex items-center justify-between border-b border-slate-800 pb-3">
                <h3 className="text-base font-bold text-white flex items-center gap-2">
                  <span className={`px-2 py-0.5 rounded border text-xs font-mono ${getActionBadgeColor(selectedLog.action)}`}>
                    {selectedLog.action}
                  </span>
                  <span>Event Details</span>
                </h3>
                <button
                  onClick={() => setSelectedLog(null)}
                  className="text-slate-400 hover:text-white text-lg font-bold"
                >
                  &times;
                </button>
              </div>

              <div className="space-y-2 text-xs font-mono text-slate-300">
                <div className="flex justify-between py-1 border-b border-slate-800/60">
                  <span className="text-slate-500">Log ID:</span>
                  <span className="text-slate-300">{selectedLog.id}</span>
                </div>
                <div className="flex justify-between py-1 border-b border-slate-800/60">
                  <span className="text-slate-500">Actor ID:</span>
                  <span className="text-cyan-400">{selectedLog.actor_id || "system"}</span>
                </div>
                <div className="flex justify-between py-1 border-b border-slate-800/60">
                  <span className="text-slate-500">Target Entity:</span>
                  <span className="text-slate-300">{selectedLog.target_entity || "N/A"}</span>
                </div>
                <div className="flex justify-between py-1 border-b border-slate-800/60">
                  <span className="text-slate-500">Target ID:</span>
                  <span className="text-slate-300">{selectedLog.target_id || "N/A"}</span>
                </div>
                <div className="flex justify-between py-1 border-b border-slate-800/60">
                  <span className="text-slate-500">Timestamp:</span>
                  <span className="text-slate-300">{selectedLog.timestamp ? new Date(selectedLog.timestamp).toISOString() : "N/A"}</span>
                </div>
              </div>

              <div>
                <label className="text-xs font-mono text-slate-400 block mb-1">Payload Metadata:</label>
                <pre className="bg-slate-950 p-3 rounded-lg border border-slate-800 text-[11px] font-mono text-emerald-400 overflow-x-auto max-h-56">
                  {JSON.stringify(selectedLog.metadata || {}, null, 2)}
                </pre>
              </div>

              <div className="pt-2 flex justify-end">
                <button
                  onClick={() => setSelectedLog(null)}
                  className="btn-secondary text-xs"
                >
                  Close
                </button>
              </div>
            </div>
          </div>
        )}
      </div>
    </RoleGuard>
  );
}
