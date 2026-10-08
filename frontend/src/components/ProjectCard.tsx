import React from "react";
import Link from "next/link";
import { ProjectRiskSummary } from "@/lib/types";
import { RiskBadge } from "./RiskBadge";
import { ArrowRight, AlertTriangle, CheckCircle2, Clock } from "lucide-react";

interface ProjectCardProps {
  project: ProjectRiskSummary;
}

export const ProjectCard: React.FC<ProjectCardProps> = ({ project }) => {
  return (
    <div className="rounded-2xl glass-panel p-5 border border-slate-800 hover:border-slate-700 transition flex flex-col justify-between group shadow-lg shadow-black/20">
      <div>
        {/* Header */}
        <div className="flex items-start justify-between gap-4 mb-3">
          <div>
            <h3 className="font-bold text-white text-base group-hover:text-indigo-400 transition">
              {project.project_name}
            </h3>
            <span className="text-xs text-slate-500 font-mono">{project.project_id}</span>
          </div>
          <RiskBadge
            band={project.band}
            score={project.score}
            confidence={project.confidence}
            size="sm"
          />
        </div>

        {/* Top Factors */}
        {project.top_factors && project.top_factors.length > 0 && (
          <div className="space-y-1.5 my-3">
            <div className="text-[11px] font-semibold text-slate-400 uppercase tracking-wider">
              Top Risk Signals
            </div>
            {project.top_factors.slice(0, 2).map((factor, idx) => (
              <div key={idx} className="flex items-start gap-2 text-xs text-slate-300">
                <AlertTriangle className="w-3.5 h-3.5 text-amber-400 shrink-0 mt-0.5" />
                <span className="line-clamp-1">{factor}</span>
              </div>
            ))}
          </div>
        )}

        {/* Recommendation */}
        {project.recommendation && (
          <div className="p-2.5 rounded-xl bg-indigo-500/10 border border-indigo-500/20 text-xs text-indigo-300 my-3">
            <span className="font-semibold text-indigo-200">Recommendation: </span>
            {project.recommendation}
          </div>
        )}
      </div>

      {/* Footer Metrics */}
      <div className="pt-3 border-t border-slate-800/80 flex items-center justify-between mt-2">
        <div className="flex items-center gap-4 text-xs text-slate-400">
          <span className="flex items-center gap-1.5">
            <CheckCircle2 className="w-3.5 h-3.5 text-emerald-400" />
            {project.task_count} Tasks
          </span>
          {project.overdue_task_count > 0 && (
            <span className="flex items-center gap-1.5 text-rose-400 font-medium">
              <Clock className="w-3.5 h-3.5" />
              {project.overdue_task_count} Overdue
            </span>
          )}
        </div>
        <Link
          href={`/projects/${project.project_id}`}
          className="text-xs font-semibold text-indigo-400 hover:text-indigo-300 flex items-center gap-1 transition"
        >
          Details
          <ArrowRight className="w-3.5 h-3.5" />
        </Link>
      </div>
    </div>
  );
};
