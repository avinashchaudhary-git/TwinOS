import React from "react";
import { Citation } from "@/lib/types";
import { FileText, CheckSquare, GitCommit, Mail, Calendar, FolderGit2 } from "lucide-react";

interface SourceCitationProps {
  citation: Citation;
  onClick?: (citation: Citation) => void;
}

export const SourceCitation: React.FC<SourceCitationProps> = ({ citation, onClick }) => {
  const getIcon = () => {
    switch (citation.entity_type) {
      case "project":
        return <FolderGit2 className="w-3.5 h-3.5 text-indigo-400" />;
      case "task":
        return <CheckSquare className="w-3.5 h-3.5 text-emerald-400" />;
      case "commit":
        return <GitCommit className="w-3.5 h-3.5 text-purple-400" />;
      case "email":
        return <Mail className="w-3.5 h-3.5 text-amber-400" />;
      case "event":
        return <Calendar className="w-3.5 h-3.5 text-cyan-400" />;
      default:
        return <FileText className="w-3.5 h-3.5 text-slate-400" />;
    }
  };

  return (
    <button
      onClick={() => onClick?.(citation)}
      className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-lg bg-slate-800/80 hover:bg-slate-700/80 border border-slate-700 hover:border-indigo-500/50 text-[11px] font-medium text-slate-300 transition group cursor-pointer shadow-sm"
      title={`Click to view graph node: ${citation.entity_type}:${citation.entity_id}`}
    >
      {getIcon()}
      <span className="font-semibold text-slate-200 group-hover:text-indigo-300">
        {citation.label || citation.entity_id}
      </span>
      <span className="text-[10px] text-slate-500 font-mono uppercase">
        {citation.entity_type}
      </span>
    </button>
  );
};
