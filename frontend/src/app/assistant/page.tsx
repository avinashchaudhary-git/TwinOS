"use client";

import React, { useState } from "react";
import { ChatPanel } from "@/components/ChatPanel";
import { Citation } from "@/lib/types";
import { api } from "@/lib/api";
import { Sparkles, Info, X } from "lucide-react";

export default function AssistantPage() {
  const [selectedCitation, setSelectedCitation] = useState<Citation | null>(null);
  const [neighborData, setNeighborData] = useState<any | null>(null);
  const [loadingNeighbor, setLoadingNeighbor] = useState(false);

  const handleCitationClick = async (citation: Citation) => {
    setSelectedCitation(citation);
    setLoadingNeighbor(true);
    try {
      const res = await api.graph.getNeighbors(citation.entity_id);
      setNeighborData(res);
    } catch {
      setNeighborData(null);
    } finally {
      setLoadingNeighbor(false);
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between pb-2 border-b border-slate-800">
        <div>
          <h1 className="text-2xl font-extrabold text-white tracking-tight flex items-center gap-2.5">
            <Sparkles className="w-6 h-6 text-indigo-400" />
            TwinOS RAG Assistant
          </h1>
          <p className="text-xs text-slate-400 mt-1">
            Plain-English natural-language queries answered with verified citations back to Knowledge Graph nodes
          </p>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2">
          <ChatPanel onCitationClick={handleCitationClick} />
        </div>

        {/* Citation Knowledge Graph Inspector */}
        <div className="lg:col-span-1 rounded-2xl glass-panel p-5 border border-slate-800 flex flex-col justify-between">
          <div>
            <div className="flex items-center justify-between pb-3 border-b border-slate-800">
              <h3 className="text-xs font-bold uppercase tracking-wider text-white flex items-center gap-2">
                <Info className="w-4 h-4 text-indigo-400" />
                Citation Inspector
              </h3>
              {selectedCitation && (
                <button
                  onClick={() => {
                    setSelectedCitation(null);
                    setNeighborData(null);
                  }}
                  className="p-1 text-slate-400 hover:text-white"
                >
                  <X className="w-3.5 h-3.5" />
                </button>
              )}
            </div>

            {selectedCitation ? (
              <div className="mt-4 space-y-4 animate-in fade-in">
                <div>
                  <span className="text-[10px] uppercase font-bold px-2 py-0.5 rounded-full bg-indigo-500/20 text-indigo-300 border border-indigo-500/30">
                    {selectedCitation.entity_type}
                  </span>
                  <h4 className="text-base font-bold text-white mt-2">{selectedCitation.label}</h4>
                  <p className="text-xs font-mono text-slate-400 break-all">{selectedCitation.entity_id}</p>
                </div>

                {selectedCitation.snippet && (
                  <div className="p-3 rounded-xl bg-slate-900 border border-slate-800 text-xs text-slate-300">
                    <span className="font-semibold text-slate-400 block mb-1">Snippet:</span>
                    {selectedCitation.snippet}
                  </div>
                )}

                {/* 1-Hop Graph Neighbors */}
                <div>
                  <h5 className="text-xs font-semibold uppercase tracking-wider text-slate-400 mb-2">
                    Connected Knowledge Graph Neighbors
                  </h5>
                  {loadingNeighbor ? (
                    <div className="text-xs text-indigo-400 animate-pulse">Querying 1-hop graph edges...</div>
                  ) : neighborData?.neighbors?.length > 0 ? (
                    <div className="space-y-1.5 max-h-56 overflow-y-auto">
                      {neighborData.neighbors.map((n: any) => (
                        <div
                          key={n.id}
                          className="p-2 rounded-lg bg-slate-900/60 border border-slate-800 flex items-center justify-between text-xs"
                        >
                          <span className="font-medium text-slate-200">
                            {n.properties?.name || n.properties?.title || n.id}
                          </span>
                          <span className="text-[10px] text-slate-500 font-mono uppercase">{n.label}</span>
                        </div>
                      ))}
                    </div>
                  ) : (
                    <p className="text-xs text-slate-500">No adjacent neighbors found for this node.</p>
                  )}
                </div>
              </div>
            ) : (
              <div className="my-16 text-center space-y-3">
                <div className="w-12 h-12 rounded-2xl bg-slate-800 border border-slate-700 mx-auto flex items-center justify-center text-slate-500">
                  <Info className="w-6 h-6" />
                </div>
                <p className="text-xs text-slate-400 leading-relaxed px-4">
                  Click any bracketed source citation chip in assistant responses to inspect its full properties and 1-hop connected graph neighbors.
                </p>
              </div>
            )}
          </div>

          <div className="pt-3 border-t border-slate-800 text-[11px] text-slate-500">
            Enforces Employee project scoping on graph queries
          </div>
        </div>
      </div>
    </div>
  );
}
