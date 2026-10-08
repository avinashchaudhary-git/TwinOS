"use client";

import React, { useState, useEffect } from "react";
import { api } from "@/lib/api";
import { Alert } from "@/lib/types";
import { Bell, Check, Clock, AlertTriangle, ShieldAlert } from "lucide-react";

export default function AlertsPage() {
  const [alerts, setAlerts] = useState<Alert[]>([]);
  const [loading, setLoading] = useState(true);

  const loadAlerts = async () => {
    setLoading(true);
    try {
      const res = await api.alerts.list(false);
      setAlerts(res);
    } catch {
      setAlerts([]);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadAlerts();
  }, []);

  const handleMarkAsRead = async (alertId: string) => {
    try {
      await api.alerts.markAsRead(alertId);
      setAlerts((prev) =>
        prev.map((a) => (a.id === alertId ? { ...a, is_read: true } : a))
      );
    } catch (err) {
      console.error(err);
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between pb-2 border-b border-slate-800">
        <div>
          <h1 className="text-2xl font-extrabold text-white tracking-tight flex items-center gap-2.5">
            <Bell className="w-6 h-6 text-indigo-400" />
            In-App Alert Notifications
          </h1>
          <p className="text-xs text-slate-400 mt-1">
            Real-time notifications triggered when project risk scores escalate to higher severity tiers
          </p>
        </div>
      </div>

      {loading ? (
        <div className="py-20 text-center text-slate-500 text-xs animate-pulse">Loading notifications...</div>
      ) : alerts.length > 0 ? (
        <div className="space-y-4">
          {alerts.map((alert) => (
            <div
              key={alert.id}
              className={`p-5 rounded-2xl glass-panel border transition flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 ${
                alert.is_read
                  ? "border-slate-800/80 opacity-70"
                  : "border-rose-500/30 bg-rose-500/5 shadow-lg shadow-rose-950/20"
              }`}
            >
              <div className="space-y-2 max-w-2xl">
                <div className="flex items-center gap-2">
                  <span
                    className={`px-2.5 py-0.5 rounded-full text-[10px] font-bold uppercase tracking-wider ${
                      alert.to_band === "critical"
                        ? "bg-rose-500/10 text-rose-400 border border-rose-500/30"
                        : "bg-amber-500/10 text-amber-400 border border-amber-500/30"
                    }`}
                  >
                    Escalated to {alert.to_band}
                  </span>
                  {alert.from_band && (
                    <span className="text-xs text-slate-500 font-mono">
                      (from {alert.from_band})
                    </span>
                  )}
                </div>

                <p className="text-xs sm:text-sm font-semibold text-white leading-relaxed">
                  {alert.message}
                </p>

                {alert.recommendation && (
                  <div className="p-3 rounded-xl bg-indigo-500/10 border border-indigo-500/20 text-xs text-indigo-300">
                    <span className="font-semibold text-indigo-200">Prescriptive Action: </span>
                    {alert.recommendation}
                  </div>
                )}

                <div className="text-[11px] text-slate-500 font-mono flex items-center gap-1">
                  <Clock className="w-3.5 h-3.5" />
                  {alert.created_at ? new Date(alert.created_at).toLocaleString() : "Recently"}
                </div>
              </div>

              {!alert.is_read && (
                <button
                  onClick={() => handleMarkAsRead(alert.id)}
                  className="px-3.5 py-2 rounded-xl bg-slate-800 hover:bg-slate-700 text-xs font-semibold text-white border border-slate-700 flex items-center gap-1.5 transition shrink-0"
                >
                  <Check className="w-3.5 h-3.5 text-emerald-400" />
                  Mark as Read
                </button>
              )}
            </div>
          ))}
        </div>
      ) : (
        <div className="py-20 text-center text-slate-500 text-xs">
          No notifications recorded in your inbox.
        </div>
      )}
    </div>
  );
}
