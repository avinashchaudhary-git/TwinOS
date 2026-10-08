import React from "react";
import { RiskBand, RiskConfidence } from "@/lib/types";

interface RiskBadgeProps {
  band: RiskBand;
  score?: number;
  confidence?: RiskConfidence;
  size?: "sm" | "md" | "lg";
}

export const RiskBadge: React.FC<RiskBadgeProps> = ({
  band,
  score,
  confidence = "normal",
  size = "md",
}) => {
  const isColdStart = confidence === "low";

  const config = {
    low: {
      bg: "bg-emerald-500/10 text-emerald-400 border-emerald-500/30",
      dot: "bg-emerald-400",
      label: "LOW RISK",
    },
    medium: {
      bg: "bg-amber-500/10 text-amber-400 border-amber-500/30",
      dot: "bg-amber-400",
      label: "MEDIUM RISK",
    },
    high: {
      bg: "bg-orange-500/10 text-orange-400 border-orange-500/30",
      dot: "bg-orange-400",
      label: "HIGH RISK",
    },
    critical: {
      bg: "bg-rose-500/10 text-rose-400 border-rose-500/30 pulse-critical",
      dot: "bg-rose-400",
      label: "CRITICAL",
    },
  }[band] || {
    bg: "bg-slate-500/10 text-slate-400 border-slate-500/30",
    dot: "bg-slate-400",
    label: band.toUpperCase(),
  };

  const sizeClass = {
    sm: "px-2 py-0.5 text-xs",
    md: "px-2.5 py-1 text-xs",
    lg: "px-3.5 py-1.5 text-sm font-medium",
  }[size];

  if (isColdStart) {
    return (
      <span
        className={`inline-flex items-center gap-1.5 rounded-full border border-dashed border-slate-600 bg-slate-800/40 text-slate-400 ${sizeClass}`}
        title="Insufficient historical data (cold start)"
      >
        <span className="h-1.5 w-1.5 rounded-full bg-slate-500" />
        Insufficient Data
      </span>
    );
  }

  return (
    <span className={`inline-flex items-center gap-1.5 rounded-full border font-semibold tracking-wider ${config.bg} ${sizeClass}`}>
      <span className={`h-2 w-2 rounded-full ${config.dot}`} />
      <span>{config.label}</span>
      {score !== undefined && (
        <span className="ml-1 opacity-75 font-mono text-[11px]">
          ({score.toFixed(2)})
        </span>
      )}
    </span>
  );
};
