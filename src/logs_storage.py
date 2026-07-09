"""In-memory log storage and management."""
from __future__ import annotations

import threading
from typing import Dict, List


class LogsStorage:
    def __init__(self, max_logs: int = 500):
        self.logs: List[Dict] = []
        self.max_logs = max_logs
        self.lock = threading.RLock()

    def add_logs(self, entries: List[Dict]) -> None:
        """Add parsed log entries to storage."""
        if not entries:
            return
        with self.lock:
            self.logs.extend(entries)
            if len(self.logs) > self.max_logs:
                self.logs = self.logs[-self.max_logs :]

    def get_logs(self, limit: int = 500) -> List[Dict]:
        """Get stored logs (oldest to newest)."""
        with self.lock:
            if limit <= 0:
                return []
            return self.logs[-limit:]

    def clear_all(self) -> None:
        """Clear all stored logs."""
        with self.lock:
            self.logs = []
