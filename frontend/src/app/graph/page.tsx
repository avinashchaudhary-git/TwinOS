"use client";

import React, { useState, useEffect } from "react";
import { GraphView } from "@/components/GraphView";
import { api } from "@/lib/api";
import { GraphOverview } from "@/lib/types";
import { Network, RefreshCw } from "lucide-react";

export default function GraphPage() {
  const [overview, setOverview] = useState<GraphOverview | null>(null);
  const [loading, setLoading] = useState(true);

  const fetchGraph = async () => {
    setLoading(true);
    try {
      const res = await api.graph.getOverview();
      setOverview(res);
    } catch {
      // Fallback sample structure
      setOverview({
        nodes: [],
        relationships: [],
        node_counts: {},
        relationship_counts: {},
      });
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchGraph();
  }, []);

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between pb-2 border-b border-slate-800">
        <div>
          <h1 className="text-2xl font-extrabold text-white tracking-tight flex items-center gap-2.5">
            <Network className="w-6 h-6 text-indigo-400" />
            Organizational Knowledge Graph
          </h1>
          <p className="text-xs text-slate-400 mt-1">
            Real-time entity-relationship topology across Employees, Projects, Tasks, Deadlines, Repositories, Commits, Emails & Events
          </p>
        </div>

        <button
          onClick={fetchGraph}
          className="flex items-center gap-2 px-3.5 py-2 rounded-xl text-xs font-semibold glass-panel hover:bg-slate-800 border border-slate-700 text-slate-200 transition"
        >
          <RefreshCw className={`w-3.5 h-3.5 ${loading ? "animate-spin text-indigo-400" : ""}`} />
          Reload Graph
        </button>
      </div>

      {overview && <GraphView overview={overview} />}
    </div>
  );
}
