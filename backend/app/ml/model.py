from pathlib import Path
from typing import Any

import joblib
import pandas as pd

from app.core.logging import logger
from app.ml.features import FEATURE_NAMES

ARTIFACTS_DIR = Path(__file__).resolve().parent / "artifacts"
MODEL_PATH = ARTIFACTS_DIR / "risk_model.joblib"


class RiskModelEngine:
    """Manages risk model loading, prediction, explainability, and cold-start handling."""

    def __init__(self):
        self.model = None
        self._load_model()

    def _load_model(self):
        if MODEL_PATH.exists():
            try:
                self.model = joblib.load(MODEL_PATH)
                logger.info(f"Loaded ML risk model from {MODEL_PATH}")
            except Exception as e:
                logger.error(f"Failed to load risk model: {e}")
        else:
            logger.info("Risk model artifact not found. Will train or use rule-based fallback.")

    def explain_top_factors(self, feature_dict: dict[str, float]) -> list[str]:
        """Produces plain-English explanations for the top contributing risk signals without SHAP."""
        factors = []

        if feature_dict.get("overdue_task_count", 0) > 0:
            count = int(feature_dict["overdue_task_count"])
            factors.append(f"{count} tasks are overdue past their deadline")

        if feature_dict.get("blocked_task_ratio", 0) > 0.20:
            pct = int(feature_dict["blocked_task_ratio"] * 100)
            factors.append(f"{pct}% of active tasks are marked as blocked")

        if feature_dict.get("workload_concentration", 0) > 0.50:
            pct = int(feature_dict["workload_concentration"] * 100)
            factors.append(f"High workload bottleneck: single engineer holds {pct}% of open tasks")

        if feature_dict.get("deadline_slippage_days", 0) > 3.0:
            days = round(feature_dict["deadline_slippage_days"], 1)
            factors.append(f"Historical task completion slippage averaging {days} days")

        if feature_dict.get("task_velocity", 0) < 1.0:
            factors.append("Low completion velocity (fewer than 1 task completed per week)")

        if feature_dict.get("commit_trend", 0) < -1.0:
            factors.append("Sharp downward trend in code commit frequency")

        if not factors:
            factors.append("Stable sprint velocity and healthy commit cadence")

        return factors[:3]

    def predict(
        self,
        features: dict[str, float],
        min_history_days: int = 14,
        history_days: int = 30,
        thresholds: dict[str, float] | None = None,
    ) -> dict[str, Any]:
        """Scores project risk. Enforces TC-05 cold-start logic if history is sparse."""
        thresh = thresholds or {"medium": 0.35, "high": 0.60, "critical": 0.80}

        # TC-05 Cold start check: sparse history -> low confidence flag, no false precision
        total_signals = features.get("commit_frequency_28d", 0) + features.get("meeting_load", 0)
        if history_days < min_history_days or total_signals < 2:
            return {
                "score": 0.0,
                "band": "low",
                "confidence": "low",
                "top_factors": ["Insufficient historical activity data (cold start)"],
                "recommendation": "Maintain project activity for at least 14 days to enable predictive risk scoring.",
                "is_cold_start": True,
            }

        # Predict probability
        if self.model is None:
            self._load_model()

        if self.model is not None:
            df = pd.DataFrame([[features[f] for f in FEATURE_NAMES]], columns=FEATURE_NAMES)
            score = float(self.model.predict_proba(df)[0][1])
        else:
            # Deterministic heuristic fallback if model artifact is absent
            heuristic = (
                0.3 * min(1.0, features.get("overdue_task_count", 0) / 4.0)
                + 0.3 * features.get("blocked_task_ratio", 0)
                + 0.2 * features.get("workload_concentration", 0)
                + 0.2 * (1.0 if features.get("commit_trend", 0) < 0 else 0.0)
            )
            score = min(0.99, max(0.01, heuristic))

        # Band classification
        if score >= thresh.get("critical", 0.80):
            band = "critical"
        elif score >= thresh.get("high", 0.60):
            band = "high"
        elif score >= thresh.get("medium", 0.35):
            band = "medium"
        else:
            band = "low"

        top_factors = self.explain_top_factors(features)

        # Recommendation rules
        recommendation = None
        if band in ("high", "critical"):
            if features.get("workload_concentration", 0) > 0.5:
                recommendation = (
                    "Reassign 2-3 open tasks from the primary contributor to balance workload."
                )
            elif features.get("blocked_task_ratio", 0) > 0.2:
                recommendation = (
                    "Schedule an unblocking session to resolve external technical dependencies."
                )
            elif features.get("overdue_task_count", 0) > 0:
                recommendation = (
                    "Renegotiate milestone timeline or reduce scope for remaining tasks."
                )
            else:
                recommendation = "Conduct immediate project health check with team leads."

        return {
            "score": round(score, 3),
            "band": band,
            "confidence": "normal",
            "top_factors": top_factors,
            "recommendation": recommendation,
            "is_cold_start": False,
        }


risk_model_engine = RiskModelEngine()
