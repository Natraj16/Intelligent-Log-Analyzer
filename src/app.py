"""Main Flask application for the log analyzer."""
from __future__ import annotations

import json
import os
import webbrowser
from pathlib import Path
from threading import Timer
from typing import Any

from flask import Flask, render_template, request, jsonify

from alerts_storage import AlertsStorage
from log_generator import DemoLogGenerator
from log_watcher import LogWatcher
from logs_storage import LogsStorage
from model_training import load_or_train_model

# Initialize Flask app
app = Flask(__name__, template_folder="templates")

# Global state
CONFIG_FILE = "config/config.json"
alerts_storage = AlertsStorage()
logs_storage = LogsStorage()
demo_generator: DemoLogGenerator | None = None
log_watcher: LogWatcher | None = None
monitoring = False

# Default config
DEFAULT_CONFIG = {
    "log_path": "logs/application.log",
    "log_levels": ["INFO", "WARN", "ERROR"],
    "custom_levels": "",
    "keywords": "",
}


def load_config() -> dict[str, Any]:
    """Load configuration from file or use defaults."""
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, "r") as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            return DEFAULT_CONFIG.copy()
    return DEFAULT_CONFIG.copy()


def save_config(config: dict[str, Any]) -> None:
    """Save configuration to file."""
    with open(CONFIG_FILE, "w") as f:
        json.dump(config, f, indent=2)


def open_browser() -> None:
    """Open the application in the default web browser."""
    Timer(1.5, lambda: webbrowser.open("http://localhost:5000")).start()


# Load config on startup
current_config = load_config()

# Load ML model
print("Loading ML model...")
model = load_or_train_model()


@app.route("/")
def index() -> str:
    """Render unified dashboard."""
    config = load_config()
    return render_template(
        "dashboard.html",
        log_path=config.get("log_path", DEFAULT_CONFIG["log_path"]),
        log_levels=config.get("log_levels", DEFAULT_CONFIG["log_levels"]),
        custom_levels=config.get("custom_levels", ""),
        keywords=config.get("keywords", ""),
    )


@app.route("/alerts")
def alerts_page() -> str:
    """Redirect to main dashboard (alerts tab)."""
    return index()


@app.route("/logs")
def logs_page() -> str:
    """Redirect to main dashboard (logs tab)."""
    return index()


@app.route("/configure", methods=["POST"])
def configure() -> str:
    """Handle configuration form submission."""
    global current_config

    log_path = request.form.get("log_path", DEFAULT_CONFIG["log_path"]).strip()
    log_levels = request.form.getlist("log_levels")
    custom_levels = request.form.get("custom_levels", "").strip()
    keywords = request.form.get("keywords", "").strip()

    # Validate
    if not log_levels:
        log_levels = DEFAULT_CONFIG["log_levels"]

    # Save config
    current_config = {
        "log_path": log_path,
        "log_levels": log_levels,
        "custom_levels": custom_levels,
        "keywords": keywords,
    }
    save_config(current_config)

    return render_template(
        "dashboard.html",
        log_path=log_path,
        log_levels=log_levels,
        custom_levels=custom_levels,
        keywords=keywords,
    )



@app.route("/start_monitoring", methods=["POST"])
def start_monitoring() -> dict:
    """Start log monitoring."""
    global monitoring, log_watcher, demo_generator

    if monitoring:
        return {"success": False, "message": "Monitoring already running"}

    try:
        config = load_config()
        log_path = config.get("log_path", DEFAULT_CONFIG["log_path"])

        # Create logs directory if needed
        log_dir = os.path.dirname(log_path)
        if log_dir and not os.path.exists(log_dir):
            os.makedirs(log_dir)

        # Create empty log file if doesn't exist
        if not os.path.exists(log_path):
            Path(log_path).touch()

        logs_storage.clear_all()

        # Initialize log watcher
        log_watcher = LogWatcher(log_path, model, alerts_storage, logs_storage, config)
        log_watcher.start()

        # Start demo log generator
        demo_generator = DemoLogGenerator(log_path)
        demo_generator.start(interval=2)

        monitoring = True
        print("✓ Monitoring started")
        return {"success": True, "message": "Monitoring started"}

    except Exception as e:
        print(f"✗ Error starting monitoring: {e}")
        return {"success": False, "message": str(e)}


@app.route("/stop_monitoring", methods=["POST"])
def stop_monitoring() -> dict:
    """Stop log monitoring."""
    global monitoring, log_watcher, demo_generator

    try:
        if log_watcher:
            log_watcher.stop()
            log_watcher = None

        if demo_generator:
            demo_generator.stop()
            demo_generator = None

        monitoring = False
        print("✓ Monitoring stopped")
        return {"success": True, "message": "Monitoring stopped"}

    except Exception as e:
        print(f"✗ Error stopping monitoring: {e}")
        return {"success": False, "message": str(e)}


@app.route("/monitoring_status")
def monitoring_status() -> dict:
    """Get current monitoring status."""
    return {"monitoring": monitoring}


@app.route("/api/alerts")
def api_alerts() -> dict:
    """Get alerts in JSON format."""
    alerts = alerts_storage.get_alerts(limit=100)
    counts = alerts_storage.get_alert_count_by_severity()

    return {
        "alerts": alerts,
        "alert_counts": counts,
    }


@app.route("/api/clear_alerts", methods=["POST"])
def api_clear_alerts() -> dict:
    """Clear all alerts."""
    alerts_storage.clear_all()
    return {"success": True}


@app.route("/api/logs")
def api_logs() -> dict:
    """Get parsed logs in JSON format."""
    if not monitoring:
        return {"logs": []}
    return {"logs": logs_storage.get_logs(limit=500)}


if __name__ == "__main__":
    print("=" * 60)
    print("[START] Intelligent Log Analyzer")
    print("=" * 60)
    print(f"[CONFIG] {current_config}")
    print(f"[MODEL] {model.__class__.__name__}")
    print()
    print("Opening browser in 1.5 seconds...")
    print("=" * 60)

    open_browser()
    app.run(debug=False, host="127.0.0.1", port=5000, use_reloader=False)
