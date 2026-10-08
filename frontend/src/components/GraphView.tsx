"use client";

import React, { useState, useMemo } from "react";
import { GraphOverview, GraphNode, GraphRelationship } from "@/lib/types";
import {
  Search,
  Filter,
  Maximize2,
  ZoomIn,
  ZoomOut,
  Info,
  X,
  ExternalLink,
} from "lucide-react";

interface GraphViewProps {
  overview: GraphOverview;
  selectedNodeId?: string;
  onSelectNode?: (nodeId: string) => void;
}

const LABEL_COLORS: Record<string, { bg: string; fill: string; stroke: string }> = {
  Employee: { bg: "#06b6d4", fill: "rgba(6, 182, 212, 0.2)", stroke: "#22d3ee" },
  Project: { bg: "#6366f1", fill: "rgba(99, 102, 241, 0.25)", stroke: "#818cf8" },
  Task: { bg: "#10b981", fill: "rgba(16, 185, 129, 0.2)", stroke: "#34d399" },
  Deadline: { bg: "#f59e0b", fill: "rgba(245, 158, 11, 0.2)", stroke: "#fbbf24" },
  Repository: { bg: "#3b82f6", fill: "rgba(59, 130, 246, 0.2)", stroke: "#60a5fa" },
  Commit: { bg: "#a855f7", fill: "rgba(168, 85, 247, 0.2)", stroke: "#c084fc" },
  Email: { bg: "#f43f5e", fill: "rgba(244, 63, 94, 0.2)", stroke: "#fb7185" },
  Event: { bg: "#ec4899", fill: "rgba(236, 72, 153, 0.2)", stroke: "#f472b6" },
};

export const GraphView: React.FC<GraphViewProps> = ({
  overview,
  selectedNodeId,
  onSelectNode,
}) => {
  const [search, setSearch] = useState("");
  const [activeFilters, setActiveFilters] = useState<string[]>([]);
  const [selectedNode, setSelectedNode] = useState<GraphNode | null>(null);
  const [zoom, setZoom] = useState(1);

  // Filter nodes
  const filteredNodes = useMemo(() => {
    return overview.nodes.filter((node) => {
      if (activeFilters.length > 0 && !activeFilters.includes(node.label)) {
        return false;
      }
      if (search.trim()) {
        const q = search.toLowerCase();
        const name = (node.properties?.name || node.properties?.title || node.id || "").toLowerCase();
        return name.includes(q);
      }
      return true;
    });
  }, [overview.nodes, activeFilters, search]);

  const filteredNodeIds = useMemo(() => new Set(filteredNodes.map((n) => n.id)), [filteredNodes]);

  // Filter relationships
  const filteredRelationships = useMemo(() => {
    return overview.relationships.filter(
      (rel) => filteredNodeIds.has(rel.source) && filteredNodeIds.has(rel.target)
    );
  }, [overview.relationships, filteredNodeIds]);

  // Compute 2D node layout positions deterministically
  const nodePositions = useMemo(() => {
    const positions: Record<string, { x: number; y: number }> = {};
    const count = filteredNodes.length;
    const width = 850;
    const height = 550;
    const centerX = width / 2;
    const centerY = height / 2;

    filteredNodes.forEach((node, i) => {
      // Group in concentric rings by entity label
      let radius = 180;
      if (node.label === "Project") radius = 80;
      else if (node.label === "Employee") radius = 150;
      else if (node.label === "Task") radius = 230;
      else radius = 270;

      const angle = (i / Math.max(1, count)) * 2 * Math.PI;
      const x = centerX + radius * Math.cos(angle);
      const y = centerY + radius * Math.sin(angle);
      positions[node.id] = { x, y };
    });
    return positions;
  }, [filteredNodes]);

  const handleNodeClick = (node: GraphNode) => {
    setSelectedNode(node);
    onSelectNode?.(node.id);
  };

  const toggleFilter = (label: string) => {
    if (activeFilters.includes(label)) {
      setActiveFilters(activeFilters.filter((l) => l !== label));
    } else {
      setActiveFilters([...activeFilters, label]);
    }
  };

  const labels = Object.keys(overview.node_counts || {});

  return (
    <div className="relative rounded-2xl glass-panel border border-slate-800 overflow-hidden shadow-2xl flex flex-col h-[650px]">
      {/* Top Toolbar */}
      <div className="p-3.5 border-b border-slate-800 bg-surface/80 flex flex-wrap items-center justify-between gap-3">
        {/* Search */}
        <div className="relative w-64">
          <Search className="w-4 h-4 text-slate-400 absolute left-3 top-2.5" />
          <input
            type="text"
            placeholder="Search nodes in graph..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="w-full pl-9 pr-3 py-1.5 rounded-xl bg-slate-900 border border-slate-700 text-xs text-white placeholder-slate-500 focus:outline-none focus:border-indigo-500"
          />
        </div>

        {/* Node Labels Filter Pills */}
        <div className="flex items-center gap-1.5 flex-wrap">
          {labels.map((lbl) => {
            const count = overview.node_counts[lbl] || 0;
            const isSelected = activeFilters.includes(lbl);
            const color = LABEL_COLORS[lbl]?.bg || "#94a3b8";
            return (
              <button
                key={lbl}
                onClick={() => toggleFilter(lbl)}
                className={`px-2.5 py-1 rounded-lg text-xs font-medium border transition flex items-center gap-1.5 ${
                  isSelected
                    ? "bg-slate-700 text-white border-slate-500"
                    : "bg-slate-900/60 text-slate-300 border-slate-800 hover:border-slate-700"
                }`}
              >
                <span className="w-2 h-2 rounded-full" style={{ backgroundColor: color }} />
                <span>{lbl}</span>
                <span className="text-[10px] opacity-60">({count})</span>
              </button>
            );
          })}
        </div>

        {/* Zoom Controls */}
        <div className="flex items-center gap-1 bg-slate-900/80 rounded-xl p-1 border border-slate-800">
          <button
            onClick={() => setZoom((z) => Math.max(0.6, z - 0.15))}
            className="p-1 hover:bg-slate-800 rounded text-slate-400 hover:text-white"
            title="Zoom Out"
          >
            <ZoomOut className="w-3.5 h-3.5" />
          </button>
          <span className="text-[11px] font-mono text-slate-400 px-1">{Math.round(zoom * 100)}%</span>
          <button
            onClick={() => setZoom((z) => Math.min(1.8, z + 0.15))}
            className="p-1 hover:bg-slate-800 rounded text-slate-400 hover:text-white"
            title="Zoom In"
          >
            <ZoomIn className="w-3.5 h-3.5" />
          </button>
          <button
            onClick={() => setZoom(1)}
            className="p-1 hover:bg-slate-800 rounded text-slate-400 hover:text-white"
            title="Reset Zoom"
          >
            <Maximize2 className="w-3.5 h-3.5" />
          </button>
        </div>
      </div>

      {/* SVG Interactive Canvas */}
      <div className="flex-1 overflow-hidden relative bg-[#060911] cursor-grab active:cursor-grabbing">
        <svg
          className="w-full h-full"
          viewBox="0 0 850 550"
          style={{ transform: `scale(${zoom})`, transformOrigin: "center center", transition: "transform 0.15s ease" }}
        >
          {/* Edges / Relationships */}
          <g className="edges">
            {filteredRelationships.map((rel, i) => {
              const start = nodePositions[rel.source];
              const end = nodePositions[rel.target];
              if (!start || !end) return null;
              return (
                <line
                  key={`${rel.source}-${rel.type}-${rel.target}-${i}`}
                  x1={start.x}
                  y1={start.y}
                  x2={end.x}
                  y2={end.y}
                  stroke="#334155"
                  strokeWidth="1.2"
                  strokeOpacity="0.4"
                  strokeDasharray={rel.type === "HAS_DEADLINE" ? "3,3" : undefined}
                />
              );
            })}
          </g>

          {/* Nodes */}
          <g className="nodes">
            {filteredNodes.map((node) => {
              const pos = nodePositions[node.id];
              if (!pos) return null;
              const isSelected = selectedNode?.id === node.id || selectedNodeId === node.id;
              const col = LABEL_COLORS[node.label] || { bg: "#94a3b8", fill: "rgba(148,163,184,0.2)", stroke: "#cbd5e1" };
              const labelText = node.properties?.name || node.properties?.title || node.id;

              return (
                <g
                  key={node.id}
                  transform={`translate(${pos.x}, ${pos.y})`}
                  onClick={() => handleNodeClick(node)}
                  className="cursor-pointer group"
                >
                  <circle
                    r={isSelected ? 18 : 12}
                    fill={col.fill}
                    stroke={isSelected ? "#ffffff" : col.stroke}
                    strokeWidth={isSelected ? 2.5 : 1.5}
                    className="transition-all duration-200 group-hover:scale-125"
                  />
                  <circle r={isSelected ? 6 : 4} fill={col.bg} />
                  <text
                    y={22}
                    textAnchor="middle"
                    fill="#94a3b8"
                    fontSize={10}
                    fontFamily="sans-serif"
                    className="select-none pointer-events-none group-hover:fill-white font-medium"
                  >
                    {labelText.length > 16 ? labelText.slice(0, 14) + "..." : labelText}
                  </text>
                </g>
              );
            })}
          </g>
        </svg>

        {/* Selected Node Inspector Drawer */}
        {selectedNode && (
          <div className="absolute right-4 top-4 bottom-4 w-80 rounded-2xl glass-panel border border-slate-700 p-5 shadow-2xl flex flex-col justify-between animate-in slide-in-from-right-4">
            <div>
              <div className="flex items-center justify-between pb-3 border-b border-slate-800">
                <span
                  className="px-2.5 py-0.5 rounded-full text-[11px] font-bold uppercase tracking-wider"
                  style={{
                    backgroundColor: LABEL_COLORS[selectedNode.label]?.fill || "rgba(255,255,255,0.1)",
                    color: LABEL_COLORS[selectedNode.label]?.stroke || "#fff",
                  }}
                >
                  {selectedNode.label}
                </span>
                <button
                  onClick={() => setSelectedNode(null)}
                  className="p-1 text-slate-400 hover:text-white rounded"
                >
                  <X className="w-4 h-4" />
                </button>
              </div>

              <div className="mt-4">
                <h4 className="text-base font-bold text-white mb-1">
                  {selectedNode.properties?.name || selectedNode.properties?.title || selectedNode.id}
                </h4>
                <p className="text-xs text-slate-400 font-mono break-all">{selectedNode.id}</p>
              </div>

              {/* Properties Grid */}
              <div className="mt-4 space-y-2 max-h-[350px] overflow-y-auto pr-1">
                {Object.entries(selectedNode.properties || {}).map(([key, val]) => {
                  if (key === "id" || key === "name" || key === "title") return null;
                  return (
                    <div key={key} className="text-xs p-2 rounded-lg bg-slate-900/60 border border-slate-800">
                      <span className="text-slate-400 font-medium capitalize">{key.replace("_", " ")}: </span>
                      <span className="text-slate-200 font-mono">{String(val)}</span>
                    </div>
                  );
                })}
              </div>
            </div>

            <div className="pt-3 border-t border-slate-800 text-[11px] text-slate-500 flex items-center justify-between">
              <span>Source: {selectedNode.properties?.source || "sync"}</span>
              <span className="flex items-center gap-1 text-indigo-400">
                <Info className="w-3.5 h-3.5" />
                Knowledge Graph
              </span>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};
