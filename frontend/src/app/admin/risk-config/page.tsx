"use client";

import React, { useEffect, useState } from "react";
import RoleGuard from "@/components/RoleGuard";
import { api } from "@/lib/api";
import { RiskConfig } from "@/lib/types";
import { useAuth } from "@/lib/auth";

export default function RiskConfigPage() {
  const { user } = useAuth();
  const [config, setConfig] = useState<RiskConfig | null>(null);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [message, setMessage] = useState<{ type: "success" | "error"; text: string } | null>(null);

  // Form states
  const [mediumThreshold, setMediumThreshold] = useState(0.35);
  const [highThreshold, setHighThreshold] = useState(0.60);
  const [criticalThreshold, setCriticalThreshold] = useState(0.80);
  const [minHistoryDays, setMinHistoryDays] = useState(14);
  const [syncIntervalMinutes, setSyncIntervalMinutes] = useState(15);

  const fetchConfig = async () => {
    setLoading(true);
    try {
      const data = await api.admin.getRiskConfig();
      setConfig(data);
      setMediumThreshold(data.medium_threshold);
      setHighThreshold(data.high_threshold);
      setCriticalThreshold(data.critical_threshold);
      setMinHistoryDays(data.min_history_days);
      setSyncIntervalMinutes(data.sync_interval_minutes);
    } catch (err: any) {
      setMessage({ type: "error", text: err.message || "Failed to load risk configuration." });
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchConfig();
  }, []);

  const handleSave = async (e: React.FormEvent) => {
    e.preventDefault();
    if (mediumThreshold >= highThreshold) {
      setMessage({ type: "error", text: "Medium threshold must be strictly less than High threshold." });
      return;
    }
    if (highThreshold >= criticalThreshold) {
      setMessage({ type: "error", text: "High threshold must be strictly less than Critical threshold." });
      return;
    }

    setSaving(true);
    setMessage(null);
    try {
      const updated = await api.admin.updateRiskConfig({
        medium_threshold: Number(mediumThreshold),
        high_threshold: Number(highThreshold),
        critical_threshold: Number(criticalThreshold),
        min_history_days: Number(minHistoryDays),
        sync_interval_minutes: Number(syncIntervalMinutes),
      });
      setConfig(updated);
      setMessage({ type: "success", text: "Risk engine configuration saved and applied globally." });
    } catch (err: any) {
      setMessage({ type: "error", text: err.message || "Failed to save configuration." });
    } finally {
      setSaving(false);
    }
  };

  const handleResetDefaults = () => {
    setMediumThreshold(0.35);
    setHighThreshold(0.60);
    setCriticalThreshold(0.80);
    setMinHistoryDays(14);
    setSyncIntervalMinutes(15);
    setMessage({ type: "success", text: "Reset to system defaults. Click 'Save Changes' to apply." });
  };

  return (
    <RoleGuard allowedRoles={["admin", "manager"]}>
      <div className="space-y-8 max-w-5xl">
        <div>
          <h1 className="text-2xl font-bold text-white tracking-tight">Risk Engine & Pipeline Configuration</h1>
          <p className="text-sm text-slate-400 mt-1">
            Calibrate machine learning risk thresholds, cold-start confidence gating, and sync frequency.
          </p>
        </div>

        {message && (
          <div
            className={`p-4 rounded-xl border text-sm flex items-center justify-between ${
              message.type === "success"
                ? "bg-emerald-950/40 border-emerald-500/30 text-emerald-300"
                : "bg-rose-950/40 border-rose-500/30 text-rose-300"
            }`}
          >
            <span>{message.text}</span>
            <button onClick={() => setMessage(null)} className="text-xs opacity-75 hover:opacity-100 font-mono">
              Dismiss
            </button>
          </div>
        )}

        {loading ? (
          <div className="p-12 text-center text-slate-500 font-mono text-sm">
            Loading active risk configuration...
          </div>
        ) : (
          <form onSubmit={handleSave} className="space-y-8">
            {/* Visual Risk Band Preview */}
            <div className="card-cyber p-6 space-y-4">
              <div className="flex items-center justify-between">
                <h3 className="text-base font-semibold text-white">Risk Band Preview</h3>
                <span className="text-xs font-mono text-slate-400">Score Range: 0.00 – 1.00</span>
              </div>

              <div className="h-6 w-full rounded-lg overflow-hidden flex text-xs font-bold font-mono tracking-wider">
                <div
                  style={{ width: `${mediumThreshold * 100}%` }}
                  className="bg-emerald-500/80 text-emerald-950 flex items-center justify-center transition-all duration-300"
                >
                  LOW (&lt;{Math.round(mediumThreshold * 100)}%)
                </div>
                <div
                  style={{ width: `${(highThreshold - mediumThreshold) * 100}%` }}
                  className="bg-amber-500/80 text-amber-950 flex items-center justify-center transition-all duration-300"
                >
                  MED
                </div>
                <div
                  style={{ width: `${(criticalThreshold - highThreshold) * 100}%` }}
                  className="bg-orange-500/80 text-orange-950 flex items-center justify-center transition-all duration-300"
                >
                  HIGH
                </div>
                <div
                  style={{ width: `${(1 - criticalThreshold) * 100}%` }}
                  className="bg-rose-600 text-rose-100 flex items-center justify-center transition-all duration-300"
                >
                  CRIT (&gt;{Math.round(criticalThreshold * 100)}%)
                </div>
              </div>

              <p className="text-xs text-slate-400">
                Projects scoring below {mediumThreshold} are marked Low risk. Between {mediumThreshold} and {highThreshold} trigger Medium risk. Between {highThreshold} and {criticalThreshold} escalate to High. Projects exceeding {criticalThreshold} generate critical executive dispatch alerts.
              </p>
            </div>

            {/* Threshold Sliders */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              {/* Medium Slider */}
              <div className="card-cyber p-5 space-y-3">
                <div className="flex justify-between items-center">
                  <label className="text-xs font-semibold text-amber-300 uppercase tracking-wider">
                    Medium Threshold
                  </label>
                  <span className="font-mono text-base font-bold text-amber-400">{mediumThreshold}</span>
                </div>
                <input
                  type="range"
                  min="0.10"
                  max="0.50"
                  step="0.05"
                  value={mediumThreshold}
                  onChange={(e) => setMediumThreshold(parseFloat(e.target.value))}
                  className="w-full accent-amber-500 cursor-pointer"
                />
                <p className="text-xs text-slate-400">
                  Cutoff where nominal projects first trigger monitoring watchlists.
                </p>
              </div>

              {/* High Slider */}
              <div className="card-cyber p-5 space-y-3">
                <div className="flex justify-between items-center">
                  <label className="text-xs font-semibold text-orange-300 uppercase tracking-wider">
                    High Threshold
                  </label>
                  <span className="font-mono text-base font-bold text-orange-400">{highThreshold}</span>
                </div>
                <input
                  type="range"
                  min="0.40"
                  max="0.75"
                  step="0.05"
                  value={highThreshold}
                  onChange={(e) => setHighThreshold(parseFloat(e.target.value))}
                  className="w-full accent-orange-500 cursor-pointer"
                />
                <p className="text-xs text-slate-400">
                  Threshold at which automated delay warnings and email dispatches trigger.
                </p>
              </div>

              {/* Critical Slider */}
              <div className="card-cyber p-5 space-y-3">
                <div className="flex justify-between items-center">
                  <label className="text-xs font-semibold text-rose-300 uppercase tracking-wider">
                    Critical Threshold
                  </label>
                  <span className="font-mono text-base font-bold text-rose-400">{criticalThreshold}</span>
                </div>
                <input
                  type="range"
                  min="0.70"
                  max="0.95"
                  step="0.05"
                  value={criticalThreshold}
                  onChange={(e) => setCriticalThreshold(parseFloat(e.target.value))}
                  className="w-full accent-rose-500 cursor-pointer"
                />
                <p className="text-xs text-slate-400">
                  Critical project alert point. Triggers immediate escalation to team leadership.
                </p>
              </div>
            </div>

            {/* Cold Start & Sync Engine Tuning */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div className="card-cyber p-6 space-y-4">
                <div className="flex justify-between items-center">
                  <div>
                    <h3 className="text-sm font-semibold text-white">Cold-Start History Floor (Days)</h3>
                    <p className="text-xs text-slate-400 mt-0.5">
                      Enforces TC-05 heuristic: projects with fewer active days receive Low confidence.
                    </p>
                  </div>
                  <span className="font-mono text-lg font-bold text-cyan-400">{minHistoryDays}d</span>
                </div>
                <input
                  type="range"
                  min="3"
                  max="60"
                  step="1"
                  value={minHistoryDays}
                  onChange={(e) => setMinHistoryDays(parseInt(e.target.value, 10))}
                  className="w-full accent-cyan-500 cursor-pointer"
                />
                <div className="text-xs text-slate-400 bg-slate-900/60 p-3 rounded-lg border border-slate-800">
                  Projects younger than <span className="text-cyan-300 font-mono">{minHistoryDays} days</span> will output{" "}
                  <code className="text-amber-400 font-mono">confidence: &quot;low&quot;</code> and use baseline risk priors to avoid false-precision alarm fatigue.
                </div>
              </div>

              <div className="card-cyber p-6 space-y-4">
                <div className="flex justify-between items-center">
                  <div>
                    <h3 className="text-sm font-semibold text-white">Ingestion Sync Cadence (Minutes)</h3>
                    <p className="text-xs text-slate-400 mt-0.5">
                      Background scheduler interval for pulling GitHub, Trello, Gmail, and GCal data.
                    </p>
                  </div>
                  <span className="font-mono text-lg font-bold text-violet-400">{syncIntervalMinutes}m</span>
                </div>
                <input
                  type="range"
                  min="5"
                  max="60"
                  step="5"
                  value={syncIntervalMinutes}
                  onChange={(e) => setSyncIntervalMinutes(parseInt(e.target.value, 10))}
                  className="w-full accent-violet-500 cursor-pointer"
                />
                <div className="text-xs text-slate-400 bg-slate-900/60 p-3 rounded-lg border border-slate-800">
                  APScheduler runs automated cycles every <span className="text-violet-300 font-mono">{syncIntervalMinutes} minutes</span> to stage diffs, build Cypher relationships, and compute risk predictions.
                </div>
              </div>
            </div>

            {/* Actions Bar */}
            <div className="flex items-center justify-between pt-4 border-t border-slate-800">
              <button
                type="button"
                onClick={handleResetDefaults}
                className="btn-secondary text-xs"
              >
                Reset to Defaults
              </button>

              <div className="flex items-center gap-3">
                {config?.updated_at && (
                  <span className="text-xs font-mono text-slate-500">
                    Last updated: {new Date(config.updated_at).toLocaleString()}
                  </span>
                )}
                {user?.role === "admin" ? (
                  <button
                    type="submit"
                    disabled={saving}
                    className="btn-primary text-xs"
                  >
                    {saving ? "Saving Configuration..." : "Save Changes"}
                  </button>
                ) : (
                  <span className="text-xs text-slate-500 italic">
                    Read-only (Admin role required to save)
                  </span>
                )}
              </div>
            </div>
          </form>
        )}
      </div>
    </RoleGuard>
  );
}
