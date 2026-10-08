import random

import numpy as np
import pandas as pd


def generate_synthetic_data(n_samples: int = 3000, random_seed: int = 42) -> pd.DataFrame:
    """Generates synthetic project-week training data with realistic risk signals and noise."""
    np.random.seed(random_seed)
    random.seed(random_seed)

    data = []
    for _ in range(n_samples):
        # Latent risk propensity (0.0 = low risk, 1.0 = high risk)
        latent_risk = np.random.beta(a=2, b=3)

        # Generate correlated features
        commit_frequency_28d = float(
            np.random.poisson(lam=max(2.0, 35.0 * (1.0 - 0.7 * latent_risk)))
        )
        commit_frequency_7d = float(
            np.random.poisson(
                lam=max(0.5, (commit_frequency_28d / 4.0) * (1.0 - 0.5 * latent_risk))
            )
        )
        commit_trend = commit_frequency_7d - (commit_frequency_28d / 4.0)

        task_velocity = float(
            max(0.0, np.random.normal(loc=max(0.5, 6.0 * (1.0 - 0.8 * latent_risk)), scale=1.5))
        )
        open_task_ratio = float(
            np.clip(np.random.normal(loc=0.3 + 0.6 * latent_risk, scale=0.15), 0.05, 1.0)
        )
        overdue_task_count = float(np.random.poisson(lam=max(0.1, 7.0 * latent_risk)))
        deadline_slippage_days = float(
            max(0.0, np.random.exponential(scale=max(0.2, 8.0 * latent_risk)))
        )
        blocked_task_ratio = float(
            np.clip(np.random.normal(loc=0.05 + 0.5 * latent_risk, scale=0.12), 0.0, 0.95)
        )
        days_to_deadline = float(max(1.0, np.random.uniform(3.0, 90.0) * (1.0 - 0.4 * latent_risk)))
        workload_concentration = float(
            np.clip(np.random.normal(loc=0.2 + 0.6 * latent_risk, scale=0.15), 0.1, 1.0)
        )
        email_activity_trend = float(
            np.random.poisson(lam=max(1.0, 10.0 + 8.0 * latent_risk))
        )  # emails escalate during crisis
        meeting_load = float(np.random.poisson(lam=max(1.0, 5.0 + 6.0 * latent_risk)))

        # Target label based on latent risk with logistic probability and noise
        logit = (
            2.5 * latent_risk
            + 0.25 * overdue_task_count
            + 0.20 * blocked_task_ratio * 10
            + 0.15 * deadline_slippage_days
            + 0.18 * workload_concentration * 5
            - 0.15 * task_velocity
            - 0.05 * days_to_deadline
            - 1.5
        )
        prob = 1.0 / (1.0 + np.exp(-logit))
        target = 1 if np.random.rand() < prob else 0

        row = {
            "commit_frequency_7d": commit_frequency_7d,
            "commit_frequency_28d": commit_frequency_28d,
            "commit_trend": commit_trend,
            "task_velocity": task_velocity,
            "open_task_ratio": open_task_ratio,
            "overdue_task_count": overdue_task_count,
            "deadline_slippage_days": deadline_slippage_days,
            "blocked_task_ratio": blocked_task_ratio,
            "days_to_deadline": days_to_deadline,
            "workload_concentration": workload_concentration,
            "email_activity_trend": email_activity_trend,
            "meeting_load": meeting_load,
            "target": target,
        }
        data.append(row)

    return pd.DataFrame(data)
