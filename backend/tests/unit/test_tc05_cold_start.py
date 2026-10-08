from app.ml.model import risk_model_engine


def test_tc05_sparse_history_returns_low_confidence_flag():
    """TC-05: Sparse history gives low-confidence flag, not a false-precise score."""
    sparse_features = {
        "commit_frequency_7d": 0.0,
        "commit_frequency_28d": 0.0,
        "commit_trend": 0.0,
        "task_velocity": 0.0,
        "open_task_ratio": 1.0,
        "overdue_task_count": 0.0,
        "deadline_slippage_days": 0.0,
        "blocked_task_ratio": 0.0,
        "days_to_deadline": 45.0,
        "workload_concentration": 0.5,
        "email_activity_trend": 0.0,
        "meeting_load": 0.0,
    }

    # 1. Project with only 5 days history (min_history_days = 14)
    pred_sparse = risk_model_engine.predict(
        features=sparse_features,
        min_history_days=14,
        history_days=5,
    )

    assert pred_sparse["confidence"] == "low", (
        f"Expected confidence 'low', got {pred_sparse['confidence']}"
    )
    assert pred_sparse["score"] == 0.0, f"Expected 0.0 score, got {pred_sparse['score']}"
    assert pred_sparse["is_cold_start"] is True
    assert any("Insufficient" in f for f in pred_sparse["top_factors"])

    # 2. Project with 30 days history and activity
    mature_features = {**sparse_features, "commit_frequency_28d": 25.0, "commit_frequency_7d": 6.0}
    pred_mature = risk_model_engine.predict(
        features=mature_features,
        min_history_days=14,
        history_days=30,
    )

    assert pred_mature["confidence"] == "normal"
    assert pred_mature["is_cold_start"] is False
    assert 0.0 < pred_mature["score"] < 1.0
