"use client";

import React, { useState, useEffect } from "react";
import { api } from "@/lib/api";
import { Task, TaskStatus } from "@/lib/types";
import { CheckSquare, Clock, AlertCircle, CheckCircle2, RefreshCw } from "lucide-react";

export default function MyWorkPage() {
  const [tasks, setTasks] = useState<Task[]>([]);
  const [loading, setLoading] = useState(true);
  const [updatingId, setUpdatingId] = useState<string | null>(null);
  const [feedback, setFeedback] = useState<string | null>(null);

  const loadTasks = async () => {
    setLoading(true);
    try {
      const res = await api.tasks.getMyTasks();
      setTasks(res);
    } catch {
      setTasks([]);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadTasks();
  }, []);

  const handleStatusChange = async (taskId: string, newStatus: TaskStatus) => {
    setUpdatingId(taskId);
    setFeedback(null);
    try {
      await api.tasks.updateStatus(taskId, newStatus);
      setTasks((prev) =>
        prev.map((t) => (t.id === taskId ? { ...t, status: newStatus } : t))
      );
      setFeedback(`Task ${taskId} status updated to ${newStatus}.`);
      setTimeout(() => setFeedback(null), 3000);
    } catch (err: any) {
      setFeedback(`Failed to update status: ${err.message}`);
    } finally {
      setUpdatingId(null);
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between pb-2 border-b border-slate-800">
        <div>
          <h1 className="text-2xl font-extrabold text-white tracking-tight flex items-center gap-2.5">
            <CheckSquare className="w-6 h-6 text-indigo-400" />
            My Assigned Work
          </h1>
          <p className="text-xs text-slate-400 mt-1">
            Personalized task queue synchronized with Knowledge Graph and organizational boards
          </p>
        </div>

        <button
          onClick={loadTasks}
          className="flex items-center gap-2 px-3.5 py-2 rounded-xl text-xs font-semibold glass-panel hover:bg-slate-800 border border-slate-700 text-slate-200 transition"
        >
          <RefreshCw className={`w-3.5 h-3.5 ${loading ? "animate-spin" : ""}`} />
          Refresh
        </button>
      </div>

      {feedback && (
        <div className="p-3 rounded-xl bg-indigo-500/10 border border-indigo-500/30 text-indigo-300 text-xs flex items-center gap-2 animate-in fade-in">
          <CheckCircle2 className="w-4 h-4 text-emerald-400 shrink-0" />
          <span>{feedback}</span>
        </div>
      )}

      {loading ? (
        <div className="py-20 text-center text-slate-500 text-xs animate-pulse">Loading assigned tasks...</div>
      ) : tasks.length > 0 ? (
        <div className="space-y-4">
          {tasks.map((task) => (
            <div
              key={task.id}
              className="p-5 rounded-2xl glass-panel border border-slate-800 flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 hover:border-slate-700 transition"
            >
              <div className="space-y-1.5 max-w-xl">
                <div className="flex items-center gap-2.5">
                  <h3 className="text-sm font-bold text-white">{task.title}</h3>
                  <span className="text-[10px] font-mono uppercase px-2 py-0.5 rounded-full bg-slate-800 text-slate-400 border border-slate-700">
                    {task.priority || "medium"}
                  </span>
                </div>
                {task.description && (
                  <p className="text-xs text-slate-400 leading-relaxed">{task.description}</p>
                )}
                <div className="flex items-center gap-3 text-[11px] text-slate-500 font-mono">
                  <span>ID: {task.id}</span>
                  {task.due_date && <span>Due: {task.due_date.slice(0, 10)}</span>}
                </div>
              </div>

              {/* Status Picker */}
              <div className="flex items-center gap-3 shrink-0">
                <span className="text-xs text-slate-400 font-medium">Status:</span>
                <select
                  value={task.status}
                  disabled={updatingId === task.id}
                  onChange={(e) => handleStatusChange(task.id, e.target.value as TaskStatus)}
                  className={`bg-slate-900 border text-xs font-semibold rounded-xl px-3 py-2 focus:outline-none transition ${
                    task.status === "done"
                      ? "text-emerald-400 border-emerald-500/40"
                      : task.status === "blocked"
                      ? "text-rose-400 border-rose-500/40"
                      : "text-amber-400 border-amber-500/40"
                  }`}
                >
                  <option value="todo">To Do</option>
                  <option value="in_progress">In Progress</option>
                  <option value="blocked">Blocked</option>
                  <option value="done">Done</option>
                </select>
              </div>
            </div>
          ))}
        </div>
      ) : (
        <div className="py-20 text-center text-slate-500 text-xs">
          No tasks currently assigned to your account.
        </div>
      )}
    </div>
  );
}
