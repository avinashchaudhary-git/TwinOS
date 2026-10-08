"use client";

import React, { useState, useEffect } from "react";
import { RoleGuard } from "@/components/RoleGuard";
import { ProjectCard } from "@/components/ProjectCard";
import { api } from "@/lib/api";
import { DashboardSummary } from "@/lib/types";
import {
  FolderGit2,
  Users,
  CheckSquare,
  AlertTriangle,
  RefreshCw,
  Clock,
  ArrowUpRight,
  TrendingUp,
  ShieldCheck,
  Zap,
} from "lucide-react";
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
  Cell,
  PieChart,
  Pie,
} from "recharts";

export default function DashboardPage() {
  const [data, setData] = useState<DashboardSummary | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const loadData = async (refresh = false) => {
    try {
      setLoading(true);
      setError(null);
      const summary = await api.dashboard.getSummary(refresh);
      setData(summary);
    } catch (err: any) {
      setError(err.message || "Failed to load dashboard data");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData();
  }, []);

  const riskChartData = data?.risk_distribution
    ? [
        { name: "Low", count: data.risk_distribution.low, color: "#10b981" },
        { name: "Medium", count: data.risk_distribution.medium, color: "#f59e0b" },
        { name: "High", count: data.risk_distribution.high, color: "#f97316" },
        { name: "Critical", count: data.risk_distribution.critical, color: "#ef4444" },
      ]
    : [];

  return (
    <RoleGuard allowedRoles={["manager", "admin"]}>
      <div className="space-y-8 animate-in fade-in duration-300">
        {/* Top Header */}
        <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 pb-2 border-b border-slate-800">
          <div>
            <h1 className="text-2xl sm:text-3xl font-extrabold text-white tracking-tight flex items-center gap-3">
              Executive Dashboard
              <span className="text-xs font-semibold px-2.5 py-0.5 rounded-full bg-indigo-500/10 text-indigo-400 border border-indigo-500/20">
                Live Synthesis
              </span>
            </h1>
            <p className="text-xs sm:text-sm text-slate-400 mt-1">
              Cross-platform activity synthesis and explainable delay risk predictions
            </p>
          </div>

          <button
            onClick={() => loadData(true)}
            className="flex items-center gap-2 px-3.5 py-2 rounded-xl text-xs font-semibold glass-panel hover:bg-slate-800 border border-slate-700 text-slate-200 transition"
          >
            <RefreshCw className={`w-3.5 h-3.5 ${loading ? "animate-spin text-indigo-400" : ""}`} />
            Refresh View
          </button>
        </div>

        {error && (
          <div className="p-4 rounded-2xl bg-rose-500/10 border border-rose-500/20 text-rose-300 text-xs flex items-center gap-2">
            <AlertTriangle className="w-4 h-4 shrink-0" />
            <span>{error}</span>
          </div>
        )}

        {/* 4 Executive KPI Cards */}
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
          <div className="p-5 rounded-2xl glass-panel border border-slate-800 flex items-center justify-between shadow-lg">
            <div>
              <p className="text-xs font-semibold text-slate-400 uppercase tracking-wider">Active Projects</p>
              <h3 className="text-2xl font-extrabold text-white mt-1">{data?.total_projects ?? 5}</h3>
              <span className="text-[11px] text-emerald-400 flex items-center gap-1 mt-1 font-medium">
                <TrendingUp className="w-3 h-3" /> Tracked across GitHub & Trello
              </span>
            </div>
            <div className="w-12 h-12 rounded-2xl bg-indigo-500/10 border border-indigo-500/20 flex items-center justify-center text-indigo-400">
              <FolderGit2 className="w-6 h-6" />
            </div>
          </div>

          <div className="p-5 rounded-2xl glass-panel border border-slate-800 flex items-center justify-between shadow-lg">
            <div>
              <p className="text-xs font-semibold text-slate-400 uppercase tracking-wider">Engineers & Leads</p>
              <h3 className="text-2xl font-extrabold text-white mt-1">{data?.total_employees ?? 12}</h3>
              <span className="text-[11px] text-cyan-400 flex items-center gap-1 mt-1 font-medium">
                <Users className="w-3 h-3" /> Unified by lowercase email
              </span>
            </div>
            <div className="w-12 h-12 rounded-2xl bg-cyan-500/10 border border-cyan-500/20 flex items-center justify-center text-cyan-400">
              <Users className="w-6 h-6" />
            </div>
          </div>

          <div className="p-5 rounded-2xl glass-panel border border-slate-800 flex items-center justify-between shadow-lg">
            <div>
              <p className="text-xs font-semibold text-slate-400 uppercase tracking-wider">Tracked Tasks</p>
              <h3 className="text-2xl font-extrabold text-white mt-1">{data?.total_tasks ?? 65}</h3>
              <span className="text-[11px] text-indigo-400 flex items-center gap-1 mt-1 font-medium">
                <CheckSquare className="w-3 h-3" /> Synchronized cards
              </span>
            </div>
            <div className="w-12 h-12 rounded-2xl bg-emerald-500/10 border border-emerald-500/20 flex items-center justify-center text-emerald-400">
              <CheckSquare className="w-6 h-6" />
            </div>
          </div>

          <div className="p-5 rounded-2xl glass-panel border border-slate-800 flex items-center justify-between shadow-lg">
            <div>
              <p className="text-xs font-semibold text-slate-400 uppercase tracking-wider">At-Risk Deliverables</p>
              <h3 className="text-2xl font-extrabold text-rose-400 mt-1">
                {(data?.risk_distribution.high ?? 0) + (data?.risk_distribution.critical ?? 0)}
              </h3>
              <span className="text-[11px] text-rose-400/80 flex items-center gap-1 mt-1 font-medium">
                <AlertTriangle className="w-3 h-3" /> Exceeding high threshold
              </span>
            </div>
            <div className="w-12 h-12 rounded-2xl bg-rose-500/10 border border-rose-500/20 flex items-center justify-center text-rose-400">
              <AlertTriangle className="w-6 h-6" />
            </div>
          </div>
        </div>

        {/* Charts & Analytics Section */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Risk Distribution Chart */}
          <div className="lg:col-span-1 rounded-2xl glass-panel p-5 border border-slate-800 shadow-xl flex flex-col justify-between">
            <div>
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-sm font-bold text-white uppercase tracking-wider">
                  Risk Band Distribution
                </h3>
                <span className="text-[11px] text-slate-500 font-mono">ML SCORING</span>
              </div>
              <p className="text-xs text-slate-400 mb-4">
                Projects partitioned into calibrated risk severity tiers.
              </p>
              <div className="h-56 w-full">
                <ResponsiveContainer width="100%" height="100%">
                  <BarChart data={riskChartData}>
                    <XAxis dataKey="name" stroke="#64748b" fontSize={11} />
                    <YAxis stroke="#64748b" fontSize={11} allowDecimals={false} />
                    <Tooltip
                      contentStyle={{ backgroundColor: "#0f172a", borderColor: "#334155", borderRadius: "12px", fontSize: "12px" }}
                      itemStyle={{ color: "#f8fafc" }}
                    />
                    <Bar dataKey="count" radius={[6, 6, 0, 0]}>
                      {riskChartData.map((entry, index) => (
                        <Cell key={`cell-${index}`} fill={entry.color} />
                      ))}
                    </Bar>
                  </BarChart>
                </ResponsiveContainer>
              </div>
            </div>
            <div className="grid grid-cols-4 gap-2 pt-3 border-t border-slate-800 text-center text-xs">
              {riskChartData.map((d) => (
                <div key={d.name} className="p-2 rounded-xl bg-slate-900/60">
                  <div className="text-[10px] text-slate-400 uppercase font-semibold">{d.name}</div>
                  <div className="text-sm font-bold text-white mt-0.5">{d.count}</div>
                </div>
              ))}
            </div>
          </div>

          {/* Overdue Tasks Alert List */}
          <div className="lg:col-span-2 rounded-2xl glass-panel p-5 border border-slate-800 shadow-xl flex flex-col justify-between">
            <div>
              <div className="flex items-center justify-between mb-3">
                <h3 className="text-sm font-bold text-white uppercase tracking-wider flex items-center gap-2">
                  <Clock className="w-4 h-4 text-rose-400" />
                  Overdue Deliverables & Bottlenecks
                </h3>
                <span className="text-xs text-slate-400 font-mono">
                  {data?.overdue_tasks.length ?? 0} active
                </span>
              </div>
              <p className="text-xs text-slate-400 mb-4">
                Critical path deliverables where the target deadline has elapsed without completion.
              </p>

              <div className="space-y-2.5 max-h-60 overflow-y-auto pr-1">
                {data?.overdue_tasks.slice(0, 5).map((task) => (
                  <div
                    key={task.id}
                    className="p-3 rounded-xl bg-slate-900/70 border border-slate-800 flex items-center justify-between hover:border-slate-700 transition"
                  >
                    <div className="space-y-1">
                      <div className="text-xs font-bold text-slate-200">{task.title}</div>
                      <div className="text-[11px] text-slate-400 flex items-center gap-2">
                        <span className="text-indigo-400 font-medium">{task.project_name}</span>
                        <span>•</span>
                        <span>Assignee: {task.assignee_name}</span>
                      </div>
                    </div>
                    <div className="text-right">
                      <span className="px-2 py-0.5 rounded-full text-[10px] font-bold bg-rose-500/10 text-rose-400 border border-rose-500/30">
                        {task.days_overdue}d overdue
                      </span>
                    </div>
                  </div>
                ))}
              </div>
            </div>

            <div className="pt-3 border-t border-slate-800 flex items-center justify-between text-xs text-slate-400">
              <span>Automatic notification sent to assigned project managers</span>
              <span className="text-indigo-400 font-semibold cursor-pointer hover:underline">
                View all tasks →
              </span>
            </div>
          </div>
        </div>

        {/* Top 5 At-Risk Projects Grid */}
        <div>
          <div className="flex items-center justify-between mb-4">
            <div>
              <h2 className="text-lg font-bold text-white flex items-center gap-2">
                <Zap className="w-4 h-4 text-amber-400" />
                Priority At-Risk Projects
              </h2>
              <p className="text-xs text-slate-400">
                Ranked by machine learning risk scores with explainable dominant factors
              </p>
            </div>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5">
            {data?.top_at_risk_projects.map((proj) => (
              <ProjectCard key={proj.project_id} project={proj} />
            ))}
          </div>
        </div>

        {/* Workload Heatmap & Sync Health */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Workload Heatmap */}
          <div className="rounded-2xl glass-panel p-5 border border-slate-800 shadow-xl">
            <h3 className="text-sm font-bold text-white uppercase tracking-wider mb-2">
              Team Workload Heatmap
            </h3>
            <p className="text-xs text-slate-400 mb-4">
              Workload distribution across team members to identify operational bottlenecks.
            </p>

            <div className="space-y-3">
              {data?.workload_heatmap.map((emp) => (
                <div key={emp.employee_id} className="p-3 rounded-xl bg-slate-900/60 border border-slate-800/80">
                  <div className="flex items-center justify-between mb-1.5">
                    <span className="text-xs font-bold text-slate-200">{emp.name}</span>
                    <span className="text-[11px] font-mono text-slate-400">
                      {emp.active_tasks} active tasks ({emp.completed_tasks} done)
                    </span>
                  </div>
                  {/* Progress bar */}
                  <div className="w-full bg-slate-800 h-2 rounded-full overflow-hidden">
                    <div
                      className={`h-full rounded-full transition-all duration-500 ${
                        emp.workload_score > 0.8
                          ? "bg-rose-500"
                          : emp.workload_score > 0.6
                          ? "bg-amber-500"
                          : "bg-indigo-500"
                      }`}
                      style={{ width: `${Math.min(100, Math.round(emp.workload_score * 100))}%` }}
                    />
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Platform Connections & Sync Status */}
          <div className="rounded-2xl glass-panel p-5 border border-slate-800 shadow-xl flex flex-col justify-between">
            <div>
              <h3 className="text-sm font-bold text-white uppercase tracking-wider mb-2">
                Platform Ingestion Health
              </h3>
              <p className="text-xs text-slate-400 mb-4">
                Incremental synchronization status across official enterprise connectors.
              </p>

              <div className="space-y-3">
                {data?.sync_health.map((sync) => (
                  <div
                    key={sync.platform}
                    className="p-3 rounded-xl bg-slate-900/60 border border-slate-800 flex items-center justify-between"
                  >
                    <div className="flex items-center gap-3">
                      <div className="w-8 h-8 rounded-lg bg-indigo-500/10 border border-indigo-500/20 flex items-center justify-center font-bold text-indigo-400 text-xs uppercase">
                        {sync.platform.slice(0, 2)}
                      </div>
                      <div>
                        <div className="text-xs font-bold text-slate-200 capitalize">{sync.platform}</div>
                        <div className="text-[11px] text-slate-400">
                          {sync.records_synced} normalized records synced
                        </div>
                      </div>
                    </div>
                    <span className="px-2.5 py-1 rounded-full text-[10px] font-bold uppercase tracking-wider bg-emerald-500/10 text-emerald-400 border border-emerald-500/30">
                      {sync.status}
                    </span>
                  </div>
                ))}
              </div>
            </div>

            <div className="pt-4 border-t border-slate-800 flex items-center justify-between text-xs text-slate-400">
              <span className="flex items-center gap-1.5 text-emerald-400 font-medium">
                <ShieldCheck className="w-3.5 h-3.5" />
                Zero credentials required in mock mode
              </span>
            </div>
          </div>
        </div>
      </div>
    </RoleGuard>
  );
}
