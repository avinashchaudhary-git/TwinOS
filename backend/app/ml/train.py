import json
from pathlib import Path

import joblib
import numpy as np
from sklearn.ensemble import GradientBoostingClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, precision_score, recall_score, roc_auc_score
from sklearn.model_selection import cross_val_score, train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

from app.core.logging import logger
from app.ml.features import FEATURE_NAMES
from app.ml.synthetic import generate_synthetic_data

ARTIFACTS_DIR = Path(__file__).resolve().parent / "artifacts"
ARTIFACTS_DIR.mkdir(parents=True, exist_ok=True)


def train_and_evaluate():
    logger.info("Generating synthetic training dataset...")
    df = generate_synthetic_data(n_samples=3500, random_seed=42)

    X = df[FEATURE_NAMES]
    y = df["target"]

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )

    # 1. Baseline Logistic Regression Pipeline
    lr_pipeline = Pipeline(
        [
            ("scaler", StandardScaler()),
            ("clf", LogisticRegression(random_state=42, max_iter=500)),
        ]
    )
    lr_cv_auc = float(
        np.mean(cross_val_score(lr_pipeline, X_train, y_train, cv=5, scoring="roc_auc"))
    )

    # 2. Gradient Boosting Pipeline
    gb_pipeline = Pipeline(
        [
            ("scaler", StandardScaler()),
            (
                "clf",
                GradientBoostingClassifier(
                    n_estimators=100, learning_rate=0.1, max_depth=4, random_state=42
                ),
            ),
        ]
    )
    gb_cv_auc = float(
        np.mean(cross_val_score(gb_pipeline, X_train, y_train, cv=5, scoring="roc_auc"))
    )

    logger.info(f"Model Comparison - Logistic Regression CV ROC-AUC: {lr_cv_auc:.4f}")
    logger.info(f"Model Comparison - Gradient Boosting CV ROC-AUC: {gb_cv_auc:.4f}")

    if gb_cv_auc >= lr_cv_auc:
        selected_model_name = "GradientBoostingClassifier"
        best_pipeline = gb_pipeline
        best_cv_auc = gb_cv_auc
    else:
        selected_model_name = "LogisticRegression"
        best_pipeline = lr_pipeline
        best_cv_auc = lr_cv_auc

    # Fit best model on train split and evaluate on holdout test set
    best_pipeline.fit(X_train, y_train)
    y_pred_proba = best_pipeline.predict_proba(X_test)[:, 1]
    y_pred = (y_pred_proba >= 0.5).astype(int)

    test_auc = float(roc_auc_score(y_test, y_pred_proba))
    test_acc = float(accuracy_score(y_test, y_pred))
    test_prec = float(precision_score(y_test, y_pred))
    test_rec = float(recall_score(y_test, y_pred))

    logger.info(
        f"Selected: {selected_model_name} (Test ROC-AUC: {test_auc:.4f}, Accuracy: {test_acc:.4f})"
    )

    # Save model artifact
    model_path = ARTIFACTS_DIR / "risk_model.joblib"
    joblib.dump(best_pipeline, model_path)
    logger.info(f"Model artifact saved to {model_path}")

    # Generate model_card.json
    model_card = {
        "model_name": selected_model_name,
        "version": "1.0.0",
        "features": FEATURE_NAMES,
        "metrics": {
            "cv_roc_auc": round(best_cv_auc, 4),
            "test_roc_auc": round(test_auc, 4),
            "test_accuracy": round(test_acc, 4),
            "test_precision": round(test_prec, 4),
            "test_recall": round(test_rec, 4),
            "baseline_lr_cv_roc_auc": round(lr_cv_auc, 4),
            "gradient_boosting_cv_roc_auc": round(gb_cv_auc, 4),
        },
        "training_data": {
            "samples": len(df),
            "source": "synthetic_generator",
            "seed": 42,
            "correlations": "task velocity, overdue counts, slippage, blocked ratio, workload concentration",
        },
        "threshold_bands": {
            "low": "< 0.35",
            "medium": "0.35 - 0.59",
            "high": "0.60 - 0.79",
            "critical": ">= 0.80",
        },
    }

    card_path = ARTIFACTS_DIR / "model_card.json"
    with open(card_path, "w") as f:
        json.dump(model_card, f, indent=2)
    logger.info(f"Model card generated at {card_path}")

    return model_card


if __name__ == "__main__":
    train_and_evaluate()
