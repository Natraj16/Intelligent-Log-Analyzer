from __future__ import annotations

from typing import Dict, List, Optional

import numpy as np
from sklearn.ensemble import IsolationForest


class LogAnomalyDetector:
    def __init__(self, contamination: float = 0.05, random_state: int = 42) -> None:
        self.model = IsolationForest(
            contamination=contamination,
            random_state=random_state,
            n_estimators=100,
        )
        self.is_trained = False
        self.quantiles = None  # Will be set from calibration data

    def train(self, training_features: np.ndarray) -> None:
        if training_features.size == 0:
            raise ValueError("Training features are empty.")

        self.model.fit(training_features)
        self.is_trained = True

    def predict(self, features: np.ndarray) -> List[int]:
        if not self.is_trained:
            raise RuntimeError("Model must be trained before prediction.")
        if features.size == 0:
            return []

        # IsolationForest returns -1 for anomalies, 1 for normal points.
        return self.model.predict(features).tolist()

    def anomaly_scores(self, features: np.ndarray) -> List[float]:
        if not self.is_trained:
            raise RuntimeError("Model must be trained before scoring.")
        if features.size == 0:
            return []

        # Lower scores indicate higher anomaly likelihood.
        return self.model.decision_function(features).tolist()

    def set_quantile_calibration(self, quantiles: Optional[dict]) -> None:
        """Set quantile thresholds for severity mapping."""
        self.quantiles = quantiles


def is_anomaly(score: float) -> bool:
    """Use the decision score as a lightweight anomaly gate."""
    return score < 0.0


def severity_from_anomaly_score(
    score: float,
    quantiles: Optional[Dict[float, float]],
) -> str:
    """
    Map anomaly score to severity level using quantile calibration.

    Model-based approach: Severity determined purely by model's confidence.
    Severity = how far into the anomaly distribution the score falls.

    Args:
        score: Anomaly score from Isolation Forest (lower = more anomalous)
        quantiles: Dict mapping percentiles to scores {0.1: -0.42, 0.25: -0.31, ...}

    Returns:
        Severity level: "Critical", "High", "Medium", or "Low"
    """
    # Fallback if quantiles not available
    if quantiles is None:
        return "Low"

    # Pure model-based severity mapping (no domain rules)
    if score < quantiles.get(0.10, float('-inf')):
        return "Critical"
    elif score < quantiles.get(0.25, float('-inf')):
        return "High"
    elif score < quantiles.get(0.50, float('-inf')):
        return "Medium"
    else:
        return "Low"
