"use client";

import React, { useState, useRef, useEffect } from "react";
import { Citation, AssistantResponse } from "@/lib/types";
import { SourceCitation } from "./SourceCitation";
import { api } from "@/lib/api";
import {
  Send,
  Sparkles,
  BotMessageSquare,
  User,
  Clock,
  HelpCircle,
  ShieldCheck,
  AlertCircle,
} from "lucide-react";

interface Message {
  id: string;
  sender: "user" | "assistant";
  text: string;
  citations?: Citation[];
  usedQueries?: string[];
  confidence?: string;
  timestamp: string;
}

interface ChatPanelProps {
  onCitationClick?: (citation: Citation) => void;
  defaultProjectId?: string;
}

const STARTER_QUESTIONS = [
  "Which of my team's projects are most likely to slip this month, and why?",
  "What are the primary bottlenecks across active tasks?",
  "Who has the highest workload concentration currently?",
  "What recent commits were merged across repositories?",
];

export const ChatPanel: React.FC<ChatPanelProps> = ({
  onCitationClick,
  defaultProjectId,
}) => {
  const [messages, setMessages] = useState<Message[]>([
    {
      id: "msg-welcome",
      sender: "assistant",
      text: "Hello! I am TwinOS Assistant, connected to your organization's real-time Knowledge Graph and predictive delay risk models. Ask me anything about project delivery health, tasks, blockers, or team workload.",
      timestamp: "Just now",
    },
  ]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [projectId, setProjectId] = useState<string | undefined>(defaultProjectId);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, loading]);

  const handleSend = async (questionText?: string) => {
    const q = (questionText || input).trim();
    if (!q || loading) return;

    const userMsg: Message = {
      id: `usr-${Date.now()}`,
      sender: "user",
      text: q,
      timestamp: new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" }),
    };

    setMessages((prev) => [...prev, userMsg]);
    setInput("");
    setLoading(true);

    try {
      const res: AssistantResponse = await api.assistant.query(q, projectId);
      const assistantMsg: Message = {
        id: `ast-${Date.now()}`,
        sender: "assistant",
        text: res.answer,
        citations: res.citations,
        usedQueries: res.used_graph_queries,
        confidence: res.confidence,
        timestamp: new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" }),
      };
      setMessages((prev) => [...prev, assistantMsg]);
    } catch (err: any) {
      const errorMsg: Message = {
        id: `err-${Date.now()}`,
        sender: "assistant",
        text: `Error connecting to RAG Assistant: ${err.message || "Failed to process query."}`,
        timestamp: new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" }),
      };
      setMessages((prev) => [...prev, errorMsg]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flex flex-col h-[700px] rounded-2xl glass-panel border border-slate-800 shadow-2xl overflow-hidden">
      {/* Header */}
      <div className="p-4 border-b border-slate-800 bg-surface/80 flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div className="w-9 h-9 rounded-xl bg-gradient-to-tr from-indigo-600 to-cyan-400 p-0.5 flex items-center justify-center">
            <div className="w-full h-full bg-[#090d16] rounded-[10px] flex items-center justify-center">
              <BotMessageSquare className="w-5 h-5 text-indigo-400" />
            </div>
          </div>
          <div>
            <h3 className="font-bold text-white text-sm flex items-center gap-2">
              Organizational Intelligence Assistant
              <span className="flex items-center gap-1 text-[10px] font-semibold text-emerald-400 bg-emerald-500/10 px-2 py-0.5 rounded-full border border-emerald-500/30">
                <ShieldCheck className="w-3 h-3" /> Grounded RAG
              </span>
            </h3>
            <p className="text-[11px] text-slate-400">Strictly cites verified graph nodes and indexed documents</p>
          </div>
        </div>

        {/* Project Scoping Filter */}
        <select
          value={projectId || ""}
          onChange={(e) => setProjectId(e.target.value || undefined)}
          className="bg-slate-900 border border-slate-700 text-xs text-slate-300 rounded-xl px-3 py-1.5 focus:outline-none focus:border-indigo-500"
        >
          <option value="">All Projects Scope</option>
          <option value="proj-core-platform">Core Platform v2.0</option>
          <option value="proj-cloud-migration">Cloud Migration (At Risk)</option>
          <option value="proj-auth-federation">SSO & Identity</option>
          <option value="proj-analytics-pipeline">Telemetry Pipeline</option>
        </select>
      </div>

      {/* Message Feed */}
      <div className="flex-1 overflow-y-auto p-4 sm:p-6 space-y-5 bg-[#090d16]/40">
        {messages.map((m) => (
          <div
            key={m.id}
            className={`flex gap-3.5 ${m.sender === "user" ? "flex-row-reverse" : "flex-row"}`}
          >
            {/* Avatar */}
            <div
              className={`w-8 h-8 rounded-xl flex items-center justify-center shrink-0 text-xs font-bold ${
                m.sender === "user"
                  ? "bg-indigo-600 text-white shadow-md shadow-indigo-600/30"
                  : "bg-slate-800 text-indigo-400 border border-slate-700"
              }`}
            >
              {m.sender === "user" ? <User className="w-4 h-4" /> : <Sparkles className="w-4 h-4" />}
            </div>

            {/* Bubble */}
            <div className={`max-w-[80%] space-y-2 ${m.sender === "user" ? "text-right" : "text-left"}`}>
              <div
                className={`p-4 rounded-2xl text-xs sm:text-sm leading-relaxed ${
                  m.sender === "user"
                    ? "bg-indigo-600 text-white rounded-tr-none shadow-lg shadow-indigo-600/20"
                    : "glass-card text-slate-200 border border-slate-700/60 rounded-tl-none shadow-md"
                }`}
              >
                <div className="whitespace-pre-wrap">{m.text}</div>

                {/* Citations block for Assistant responses */}
                {m.citations && m.citations.length > 0 && (
                  <div className="mt-3.5 pt-3 border-t border-slate-700/60 text-left">
                    <div className="text-[10px] font-bold uppercase tracking-wider text-slate-400 mb-1.5 flex items-center gap-1.5">
                      <HelpCircle className="w-3 h-3 text-indigo-400" />
                      Grounded Evidence Citations
                    </div>
                    <div className="flex flex-wrap gap-1.5">
                      {m.citations.map((c, idx) => (
                        <SourceCitation
                          key={`${c.entity_type}-${c.entity_id}-${idx}`}
                          citation={c}
                          onClick={onCitationClick}
                        />
                      ))}
                    </div>
                  </div>
                )}
              </div>

              {/* Timestamp */}
              <div className="text-[10px] text-slate-500 font-mono flex items-center gap-1 px-1">
                <Clock className="w-3 h-3" />
                {m.timestamp}
                {m.confidence && m.confidence === "low" && (
                  <span className="text-amber-400 ml-2">(Low Confidence / Cold Start)</span>
                )}
              </div>
            </div>
          </div>
        ))}

        {loading && (
          <div className="flex gap-3.5 items-center text-xs text-indigo-400 animate-pulse">
            <div className="w-8 h-8 rounded-xl bg-slate-800 border border-slate-700 flex items-center justify-center">
              <Sparkles className="w-4 h-4 animate-spin text-indigo-400" />
            </div>
            <span>Synthesizing answer from Knowledge Graph & Vector Store...</span>
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      {/* Suggested Starters */}
      <div className="px-4 py-2 border-t border-slate-800/80 bg-surface/40 flex items-center gap-2 overflow-x-auto text-xs">
        <span className="text-slate-500 text-[11px] font-semibold uppercase tracking-wider shrink-0">
          Suggested:
        </span>
        {STARTER_QUESTIONS.map((q, idx) => (
          <button
            key={idx}
            onClick={() => handleSend(q)}
            className="shrink-0 px-3 py-1 rounded-full bg-slate-800/80 hover:bg-slate-700 text-slate-300 hover:text-white border border-slate-700 text-[11px] transition"
          >
            {q}
          </button>
        ))}
      </div>

      {/* Input Form */}
      <form
        onSubmit={(e) => {
          e.preventDefault();
          handleSend();
        }}
        className="p-3.5 border-t border-slate-800 bg-surface/90 flex items-center gap-2"
      >
        <input
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder="Ask a question about project status, risks, tasks, or team activity..."
          className="flex-1 bg-slate-900 border border-slate-700 rounded-xl px-4 py-2.5 text-xs sm:text-sm text-white placeholder-slate-500 focus:outline-none focus:border-indigo-500 transition"
        />
        <button
          type="submit"
          disabled={!input.trim() || loading}
          className={`px-4 py-2.5 rounded-xl text-xs sm:text-sm font-semibold flex items-center gap-2 transition ${
            !input.trim() || loading
              ? "bg-slate-800 text-slate-500 cursor-not-allowed border border-slate-700"
              : "bg-indigo-600 hover:bg-indigo-500 text-white shadow-lg shadow-indigo-600/30"
          }`}
        >
          <span>Ask</span>
          <Send className="w-4 h-4" />
        </button>
      </form>
    </div>
  );
};
