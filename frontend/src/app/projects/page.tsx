"use client";

import React, { useState, useEffect } from "react";
import { RoleGuard } from "@/components/RoleGuard";
import { ProjectCard } from "@/components/ProjectCard";
import { api } from "@/lib/api";
import { ProjectRiskSummary } from "@/lib/types";
import { FolderGit2, Search, Filter } from "lucide-react";

export default function ProjectsPage() {
  const [projects, setProjects] = useState<ProjectRiskSummary[]>([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState("");
  const [bandFilter, setBandFilter] = useState<string>("all");

  useEffect(() => {
    api.risk
      .getProjects()
      .then((data) => setProjects(data))
      .catch(() => {})
      .finally(() => setLoading(false));
  }, []);

  const filtered = projects.filter((p) => {
    if (bandFilter !== "all" && p.band !== bandFilter) return false;
    if (search.trim()) {
      const q = search.toLowerCase();
      return p.project_name.toLowerCase().includes(q) || p.project_id.toLowerCase().includes(q);
    }
    return true;
  });

  return (
    <RoleGuard allowedRoles={["manager", "admin"]}>
      <div className="space-y-6">
        <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 pb-2 border-b border-slate-800">
          <div>
            <h1 className="text-2xl font-extrabold text-white tracking-tight flex items-center gap-2.5">
              <FolderGit2 className="w-6 h-6 text-indigo-400" />
              Organizational Projects & Delivery Health
            </h1>
            <p className="text-xs text-slate-400 mt-1">
              Active engineering projects monitored by predictive machine learning risk models
            </p>
          </div>

          {/* Search & Band Filter */}
          <div className="flex items-center gap-3 w-full sm:w-auto">
            <div className="relative flex-1 sm:w-60">
              <Search className="w-4 h-4 text-slate-400 absolute left-3 top-2.5" />
              <input
                type="text"
                placeholder="Search projects..."
                value={search}
                onChange={(e) => setSearch(e.target.value)}
                className="w-full pl-9 pr-3 py-1.5 rounded-xl bg-slate-900 border border-slate-700 text-xs text-white placeholder-slate-500 focus:outline-none focus:border-indigo-500"
              />
            </div>

            <select
              value={bandFilter}
              onChange={(e) => setBandFilter(e.target.value)}
              className="bg-slate-900 border border-slate-700 text-xs text-slate-300 rounded-xl px-3 py-2 focus:outline-none focus:border-indigo-500"
            >
              <option value="all">All Risk Bands</option>
              <option value="critical">Critical Only</option>
              <option value="high">High Risk</option>
              <option value="medium">Medium</option>
              <option value="low">Low Risk</option>
            </select>
          </div>
        </div>

        {loading ? (
          <div className="py-20 text-center text-slate-500 text-xs animate-pulse">Loading projects...</div>
        ) : filtered.length > 0 ? (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {filtered.map((proj) => (
              <ProjectCard key={proj.project_id} project={proj} />
            ))}
          </div>
        ) : (
          <div className="py-20 text-center text-slate-500 text-xs">No projects match the selected filter.</div>
        )}
      </div>
    </RoleGuard>
  );
}
