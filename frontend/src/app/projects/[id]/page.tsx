"use client";

import React, { useState, useEffect } from "react";
import { useParams } from "next/navigation";
import { RoleGuard } from "@/components/RoleGuard";
import { RiskBadge } from "@/components/RiskBadge";
import { api } from "@/lib/api";
import { ProjectRiskSummary } from "@/lib/types";
import {
  FolderGit2,
  Calendar,
  AlertTriangle,
  Clock,
  GitCommit,
  CheckCircle2,
  ArrowLeft,
} from "lucide-react";
import Link from "next/link";

export default function ProjectDetailPage() {
  const params = useParams();
  const projectId = params?.id as string;
  const [project, setProject] = useState<ProjectRiskSummary | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (projectId) {
      api.risk
        .getProject(projectId)
        .then((res) => setProject(res))
        .catch(() => {})
        .finally(() => setLoading(false));
    }
  }, [projectId]);

  if (loading) {
    return <div className="py-20 text-center text-slate-500 text-xs animate-pulse">Loading project details...</div>;
  }

  if (!project) {
    return (
      <div className="py-20 text-center text-slate-400 text-sm">
        <p>Project not found.</p>
        <Link href="/projects" className="text-indigo-400 underline mt-2 inline-block">
          Back to Projects
        </Link>
      </div>
    );
  }

  return (
    <RoleGuard allowedRoles={["manager", "admin"]}>
      <div className="space-y-8 animate-in fade-in">
        {/* Navigation back */}
        <Link
          href="/projects"
          className="inline-flex items-center gap-2 text-xs font-semibold text-slate-400 hover:text-white transition"
        >
          <ArrowLeft className="w-4 h-4" />
          Back to All Projects
        </Link>

        {/* Project Header Banner */}
        <div className="p-6 rounded-3xl glass-panel border border-slate-800 flex flex-col md:flex-row items-start md:items-center justify-between gap-6 shadow-xl">
          <div className="flex items-start gap-4">
            <div className="w-14 h-14 rounded-2xl bg-indigo-500/10 border border-indigo-500/20 flex items-center justify-center text-indigo-400 shrink-0">
              <FolderGit2 className="w-7 h-7" />
            </div>
            <div>
              <h1 className="text-2xl font-extrabold text-white">{project.project_name}</h1>
              <div className="flex items-center gap-3 text-xs text-slate-400 mt-1 font-mono">
                <span>ID: {project.project_id}</span>
                <span>•</span>
                <span className="flex items-center gap-1">
                  <Calendar className="w-3.5 h-3.5 text-slate-500" /> Target Q4 Deliverable
                </span>
              </div>
            </div>
          </div>

          <div className="flex items-center gap-4">
            <RiskBadge
              band={project.band}
              score={project.score}
              confidence={project.confidence}
              size="lg"
            />
          </div>
        </div>

        {/* Risk Analysis & Recommendation */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div className="rounded-2xl glass-panel p-5 border border-slate-800 shadow-lg">
            <h3 className="text-xs font-bold uppercase tracking-wider text-white mb-3 flex items-center gap-2">
              <AlertTriangle className="w-4 h-4 text-amber-400" />
              Machine Learning Risk Factors
            </h3>
            <p className="text-xs text-slate-400 mb-4">
              Identified by the gradient boosting delay prediction model based on recent activity telemetry.
            </p>

            <div className="space-y-2.5">
              {project.top_factors?.map((f, i) => (
                <div key={i} className="p-3 rounded-xl bg-slate-900/70 border border-slate-800 flex items-start gap-3">
                  <span className="w-5 h-5 rounded-full bg-amber-500/10 text-amber-400 border border-amber-500/20 text-xs font-bold flex items-center justify-center shrink-0 mt-0.5">
                    {i + 1}
                  </span>
                  <span className="text-xs text-slate-200">{f}</span>
                </div>
              ))}
            </div>
          </div>

          <div className="rounded-2xl glass-panel p-5 border border-slate-800 shadow-lg flex flex-col justify-between">
            <div>
              <h3 className="text-xs font-bold uppercase tracking-wider text-white mb-3">
                Action Recommendation
              </h3>
              <p className="text-xs text-slate-400 mb-4">
                Automated prescriptive guidance derived from dominant risk bottlenecks.
              </p>

              <div className="p-4 rounded-xl bg-indigo-500/10 border border-indigo-500/20 text-xs text-indigo-200 leading-relaxed">
                {project.recommendation || "Maintain ongoing commit cadence and monitor open tasks for upcoming deadlines."}
              </div>
            </div>

            <div className="pt-4 border-t border-slate-800 text-[11px] text-slate-500">
              Confidence status: <span className="text-slate-300 font-semibold">{project.confidence}</span>
            </div>
          </div>
        </div>

        {/* Connected Tasks Overview */}
        <div className="rounded-2xl glass-panel p-6 border border-slate-800 shadow-xl">
          <h3 className="text-sm font-bold text-white uppercase tracking-wider mb-4 flex items-center gap-2">
            <CheckCircle2 className="w-4 h-4 text-emerald-400" />
            Synchronized Project Tasks
          </h3>

          <div className="space-y-3">
            {[
              { id: "task-01", title: "Implement OAuth token rotation", status: "in_progress", priority: "high", due: "2026-10-18" },
              { id: "task-02", title: "Migrate database schema partition", status: "blocked", priority: "critical", due: "2026-10-02" },
              { id: "task-03", title: "Configure Redis caching cluster", status: "done", priority: "medium", due: "2026-09-28" },
            ].map((t) => (
              <div
                key={t.id}
                className="p-3.5 rounded-xl bg-slate-900/70 border border-slate-800 flex items-center justify-between"
              >
                <div>
                  <h4 className="text-xs font-bold text-white">{t.title}</h4>
                  <span className="text-[11px] text-slate-500 font-mono">Due: {t.due}</span>
                </div>
                <div className="flex items-center gap-2">
                  <span className="text-[10px] uppercase font-bold px-2 py-0.5 rounded-full bg-slate-800 text-slate-300 border border-slate-700">
                    {t.priority}
                  </span>
                  <span
                    className={`text-[10px] uppercase font-bold px-2.5 py-0.5 rounded-full border ${
                      t.status === "done"
                        ? "bg-emerald-500/10 text-emerald-400 border-emerald-500/30"
                        : t.status === "blocked"
                        ? "bg-rose-500/10 text-rose-400 border-rose-500/30"
                        : "bg-amber-500/10 text-amber-400 border-amber-500/30"
                    }`}
                  >
                    {t.status}
                  </span>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </RoleGuard>
  );
}
