"""In-memory alert storage and management."""
from __future__ import annotations

import threading
from datetime import datetime
from typing import Dict, List, Optional


class AlertsStorage:
    def __init__(self, max_alerts: int = 500):
        self.alerts: List[Dict] = []
        self.max_alerts = max_alerts
        self.lock = threading.RLock()

    def add_alert(
        self,
        service: str,
        severity: str,
        log_level: str,
        timestamp: str,
        anomaly_score: float = 0.0,
    ) -> None:
        """Add a new alert to storage."""
        with self.lock:
            alert = {
                "id": len(self.alerts),
                "timestamp": datetime.now().isoformat(),
                "log_timestamp": timestamp,
                "service": service,
                "severity": severity,
                "log_level": log_level,
                "anomaly_score": round(anomaly_score, 4),
            }
            self.alerts.insert(0, alert)  # Most recent first

            # Trim old alerts if necessary
            if len(self.alerts) > self.max_alerts:
                self.alerts = self.alerts[:self.max_alerts]

    def get_alerts(
        self,
        severity: Optional[str] = None,
        limit: int = 100,
    ) -> List[Dict]:
        """Get alerts, optionally filtered by severity."""
        with self.lock:
            if severity:
                filtered = [a for a in self.alerts if a["severity"] == severity]
                return filtered[:limit]
            return self.alerts[:limit]

    def get_alert_count_by_severity(self) -> Dict[str, int]:
        """Get count of alerts grouped by severity."""
        with self.lock:
            counts: Dict[str, int] = {}
            for alert in self.alerts:
                severity = alert["severity"]
                counts[severity] = counts.get(severity, 0) + 1
            return counts

    def clear_all(self) -> None:
        """Clear all alerts."""
        with self.lock:
            self.alerts = []

    def get_total_count(self) -> int:
        """Get total number of alerts."""
        with self.lock:
            return len(self.alerts)
