"""Demo log generator for testing the analyzer."""
from __future__ import annotations

import os
import random
import threading
import time
from datetime import datetime, timedelta


class DemoLogGenerator:
    def __init__(self, log_file: str = "logs/application.log"):
        self.log_file = log_file
        self.running = False
        self.thread: threading.Thread | None = None

    def _ensure_log_dir(self) -> None:
        """Create logs directory if it doesn't exist."""
        log_dir = os.path.dirname(self.log_file)
        if log_dir and not os.path.exists(log_dir):
            os.makedirs(log_dir)

    def _generate_log_entry(self) -> str:
        """Generate a single realistic log entry."""
        services = ["UserService", "PaymentService", "AuthService", "DatabaseService", "CacheService"]
        levels = ["INFO", "WARN", "ERROR"]

        # Weighted distribution: more INFO, less ERROR
        level = random.choices(levels, weights=[0.6, 0.3, 0.1])[0]
        service = random.choice(services)

        # Create realistic messages
        info_msgs = [
            "User login success",
            "API request completed",
            "Database connection established",
            "Cache hit for key",
            "Task scheduled successfully",
        ]
        warn_msgs = [
            "High memory usage detected",
            "Slow query execution",
            "Rate limit approaching",
            "Connection timeout warning",
            "Disk space running low",
        ]
        error_msgs = [
            "Payment failed",
            "Database connection lost",
            "Authentication failed",
            "Service unavailable",
            "Request timeout exceeded",
            "Duplicate entry detected",
        ]

        if level == "INFO":
            message = random.choice(info_msgs)
        elif level == "WARN":
            message = random.choice(warn_msgs)
        else:
            message = random.choice(error_msgs)

        # Generate timestamp
        now = datetime.now()
        timestamp = now.strftime("%Y-%m-%d %H:%M:%S")

        return f"{timestamp} {level} {service} {message}\n"

    def start(self, interval: int = 2) -> None:
        """Start generating logs in background."""
        if self.running:
            return

        self._ensure_log_dir()
        self.running = True
        self.thread = threading.Thread(target=self._run, args=(interval,), daemon=True)
        self.thread.start()

    def _run(self, interval: int) -> None:
        """Background thread that generates logs."""
        while self.running:
            try:
                entry = self._generate_log_entry()
                with open(self.log_file, "a", encoding="utf-8") as f:
                    f.write(entry)
                time.sleep(interval)
            except Exception as e:
                print(f"Error in log generator: {e}")
                break

    def stop(self) -> None:
        """Stop generating logs."""
        self.running = False
        if self.thread:
            self.thread.join(timeout=5)
