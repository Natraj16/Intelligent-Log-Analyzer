"""Generate report-ready visualizations for the LogSight project."""
from __future__ import annotations

import argparse
from collections import Counter
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch

from feature_engineering import extract_features
from model import severity_from_anomaly_score
from model_training import load_or_train_model
from parser import parse_log_file


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Generate LogSight figures for final project report.",
    )
    parser.add_argument(
        "--log-file",
        default="logs/application.log",
        help="Path to log file used for data-driven charts.",
    )
    parser.add_argument(
        "--output-dir",
        default=r"project report\generated_figures",
        help="Directory where figures are saved.",
    )
    parser.add_argument(
        "--max-logs",
        type=int,
        default=500,
        help="Maximum number of recent logs to analyze.",
    )
    return parser.parse_args()


def _make_demo_logs(size: int = 120) -> list[dict[str, str]]:
    base_time = datetime.now() - timedelta(minutes=size)
    services = [
        "UserService",
        "PaymentService",
        "AuthService",
        "DatabaseService",
        "CacheService",
    ]
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
    level_cycle = ["INFO"] * 6 + ["WARN"] * 3 + ["ERROR"] * 1
    entries: list[dict[str, str]] = []

    for i in range(size):
        level = level_cycle[i % len(level_cycle)]
        if level == "INFO":
            message = info_msgs[i % len(info_msgs)]
        elif level == "WARN":
            message = warn_msgs[i % len(warn_msgs)]
        else:
            message = error_msgs[i % len(error_msgs)]

        timestamp = (base_time + timedelta(seconds=30 * i)).strftime("%Y-%m-%d %H:%M:%S")
        entries.append(
            {
                "raw_line": f"{timestamp} {level} {services[i % len(services)]} {message}",
                "timestamp": timestamp,
                "level": level,
                "service": services[i % len(services)],
                "message": message,
            }
        )
    return entries


def _load_runtime_config(config_path: Path) -> dict[str, Any]:
    defaults: dict[str, Any] = {
        "log_levels": ["INFO", "WARN", "ERROR"],
        "keywords": "",
    }
    if not config_path.exists():
        return defaults
    try:
        import json

        parsed = json.loads(config_path.read_text(encoding="utf-8"))
        if not isinstance(parsed, dict):
            return defaults
        log_levels = parsed.get("log_levels", defaults["log_levels"])
        if not isinstance(log_levels, list) or not log_levels:
            log_levels = defaults["log_levels"]
        keywords = parsed.get("keywords", defaults["keywords"])
        if not isinstance(keywords, str):
            keywords = defaults["keywords"]
        return {"log_levels": log_levels, "keywords": keywords}
    except Exception:
        return defaults


def _apply_runtime_filters(parsed_logs: list[dict[str, str]], config: dict[str, Any]) -> list[dict[str, str]]:
    selected_levels = config.get("log_levels", ["INFO", "WARN", "ERROR"])
    filtered = [entry for entry in parsed_logs if entry.get("level") in selected_levels]

    keywords = config.get("keywords", "")
    if keywords:
        keyword_list = [kw.strip().lower() for kw in keywords.split(",") if kw.strip()]
        if keyword_list:
            filtered = [
                entry
                for entry in filtered
                if any(kw in entry.get("message", "").lower() for kw in keyword_list)
            ]
    return filtered


def _collect_data(log_file: Path, max_logs: int) -> dict[str, Any]:
    parsed_logs = parse_log_file(str(log_file)) if log_file.exists() else []
    if not parsed_logs:
        parsed_logs = _make_demo_logs()
    config = _load_runtime_config(Path("config/config.json"))
    parsed_logs = _apply_runtime_filters(parsed_logs, config)[-max_logs:]
    if not parsed_logs:
        parsed_logs = _apply_runtime_filters(_make_demo_logs(), config)[-max_logs:]
    features, diagnostics = extract_features(parsed_logs)
    detector = load_or_train_model()

    if features.size == 0:
        raise ValueError("No valid logs found to build visualizations.")

    predictions = detector.predict(features)
    scores = detector.anomaly_scores(features)
    severities: list[str] = [severity_from_anomaly_score(score, detector.quantiles) for score in scores]

    return {
        "logs": parsed_logs,
        "features": features,
        "diagnostics": diagnostics,
        "predictions": predictions,
        "scores": scores,
        "severities": severities,
        "quantiles": detector.quantiles,
        "config": config,
    }


def _save(fig: plt.Figure, output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(output_path, dpi=300, bbox_inches="tight")
    plt.close(fig)


def _draw_box(
    ax: plt.Axes,
    x: float,
    y: float,
    w: float,
    h: float,
    label: str,
    fc: str,
    fontsize: int = 10,
) -> None:
    box = FancyBboxPatch(
        (x, y),
        w,
        h,
        boxstyle="round,pad=0.01,rounding_size=0.02",
        linewidth=1.2,
        edgecolor="#334155",
        facecolor=fc,
    )
    ax.add_patch(box)
    ax.text(
        x + w / 2,
        y + h / 2,
        label,
        ha="center",
        va="center",
        fontsize=fontsize,
        linespacing=1.25,
        wrap=True,
    )


def _draw_arrow(ax: plt.Axes, x1: float, y1: float, x2: float, y2: float) -> None:
    arrow = FancyArrowPatch((x1, y1), (x2, y2), arrowstyle="->", mutation_scale=12, linewidth=1.1)
    ax.add_patch(arrow)


def generate_architecture_diagram(output_dir: Path) -> None:
    fig, ax = plt.subplots(figsize=(16, 9))
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis("off")
    ax.set_title("LogSight System Architecture", fontsize=18, fontweight="bold", pad=14)

    nodes = [
        (0.03, 0.62, 0.16, 0.13, "Log File\nlogs/application.log", "#e2e8f0"),
        (0.23, 0.62, 0.14, 0.13, "LogWatcher\n(1s polling)", "#dbeafe"),
        (0.41, 0.62, 0.13, 0.13, "Parser\n(regex)", "#dbeafe"),
        (0.58, 0.62, 0.17, 0.13, "Feature Engineering\n(4 features)", "#dcfce7"),
        (0.79, 0.62, 0.17, 0.13, "IsolationForest\npredict + score", "#fef3c7"),
        (0.79, 0.38, 0.17, 0.13, "Quantile Severity Mapping\nfrom anomaly score", "#fee2e2"),
        (0.58, 0.18, 0.17, 0.13, "AlertsStorage\n(in-memory)", "#ede9fe"),
        (0.38, 0.18, 0.17, 0.13, "LogsStorage\n(in-memory)", "#ede9fe"),
        (0.13, 0.18, 0.2, 0.13, "Flask Dashboard + APIs\n/, /api/alerts, /api/logs", "#cffafe"),
    ]
    for x, y, w, h, label, color in nodes:
        _draw_box(ax, x, y, w, h, label, color)

    _draw_arrow(ax, 0.19, 0.685, 0.23, 0.685)
    _draw_arrow(ax, 0.37, 0.685, 0.41, 0.685)
    _draw_arrow(ax, 0.54, 0.685, 0.58, 0.685)
    _draw_arrow(ax, 0.75, 0.685, 0.79, 0.685)
    _draw_arrow(ax, 0.875, 0.62, 0.875, 0.51)
    _draw_arrow(ax, 0.79, 0.445, 0.75, 0.245)
    _draw_arrow(ax, 0.79, 0.445, 0.55, 0.245)
    _draw_arrow(ax, 0.38, 0.245, 0.33, 0.245)
    _draw_arrow(ax, 0.58, 0.245, 0.33, 0.245)

    _save(fig, output_dir / "fig01_system_architecture.png")


def generate_pipeline_diagram(output_dir: Path) -> None:
    fig, ax = plt.subplots(figsize=(16, 6.2))
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis("off")
    ax.set_title("LogSight Processing Workflow", fontsize=18, fontweight="bold", pad=14)

    steps = [
        "1. New\nlog line",
        "2. Parse\nTimestamp, Level,\nService, Message",
        "3. Filter by\nselected levels\nand keywords",
        "4. Extract 4\nnumerical\nfeatures",
        "5. IsolationForest\npredict (-1/1)\nand decision score",
        "6. Map severity\nusing model\nscore quantiles",
        "7. Save logs + alerts\nand expose via\nDashboard/API",
    ]
    x_start = 0.02
    width = 0.12
    gap = 0.02
    for i, text in enumerate(steps):
        x = x_start + i * (width + gap)
        _draw_box(ax, x, 0.33, width, 0.34, text, "#f8fafc", fontsize=9)
        if i < len(steps) - 1:
            _draw_arrow(ax, x + width, 0.5, x + width + gap, 0.5)

    _save(fig, output_dir / "fig02_processing_pipeline.png")


def generate_parsing_example(output_dir: Path) -> None:
    fig, ax = plt.subplots(figsize=(14, 6))
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis("off")
    ax.set_title("Log Parsing Example", fontsize=17, fontweight="bold", pad=14)

    input_line = "2026-04-20 10:30:45 ERROR PaymentService Transaction failed"
    fields = [
        ("timestamp", "2026-04-20 10:30:45"),
        ("level", "ERROR"),
        ("service", "PaymentService"),
        ("message", "Transaction failed"),
    ]

    _draw_box(ax, 0.05, 0.62, 0.9, 0.2, f"Raw Log Line:\n{input_line}", "#e2e8f0")
    _draw_arrow(ax, 0.5, 0.62, 0.5, 0.48)

    y = 0.3
    for idx, (k, v) in enumerate(fields):
        _draw_box(ax, 0.1 + idx * 0.21, y, 0.19, 0.14, f"{k}\n{v}", "#dcfce7")

    _save(fig, output_dir / "fig03_log_parsing_example.png")


def generate_feature_table(output_dir: Path, data: dict[str, Any]) -> None:
    logs = data["logs"]
    features = data["features"]
    diagnostics = data["diagnostics"]

    rows = min(8, len(logs))
    if rows == 0:
        fig, ax = plt.subplots(figsize=(14, 4))
        ax.axis("off")
        ax.set_title("Feature Engineering Output (Sample Rows)", fontsize=16, fontweight="bold", pad=12)
        ax.text(0.5, 0.5, "No data available", ha="center", va="center", fontsize=12, color="#475569")
        _save(fig, output_dir / "fig04_feature_engineering_table.png")
        return

    table_rows = []
    for i in range(rows):
        message = logs[i]["message"]
        if len(message) > 30:
            message = f"{message[:27]}..."
        table_rows.append(
            [
                logs[i]["level"],
                logs[i]["service"],
                message,
                int(features[i, 0]),
                int(features[i, 1]),
                diagnostics[i]["error_frequency"],
                diagnostics[i]["repeated_message_count"],
            ]
        )

    headers = [
        "Level",
        "Service",
        "Message",
        "Level Enc.",
        "Msg Length",
        "Error Freq (win=10)",
        "Repetition",
    ]

    fig, ax = plt.subplots(figsize=(15, 5.6))
    ax.axis("off")
    ax.set_title("Feature Engineering Output (Sample Rows)", fontsize=16, fontweight="bold", pad=12)
    table = ax.table(
        cellText=table_rows,
        colLabels=headers,
        loc="center",
        cellLoc="center",
        colLoc="center",
        colWidths=[0.10, 0.16, 0.24, 0.11, 0.12, 0.16, 0.11],
    )
    table.auto_set_font_size(False)
    table.set_fontsize(9.5)
    table.scale(1.0, 1.55)

    for (row, col), cell in table.get_celld().items():
        cell.set_edgecolor("#cbd5e1")
        cell.set_linewidth(0.8)
        if row == 0:
            cell.set_facecolor("#334155")
            cell.get_text().set_color("white")
            cell.get_text().set_fontweight("bold")
            cell.PAD = 0.08
        else:
            cell.set_facecolor("#f8fafc" if row % 2 == 0 else "white")
            if col in (1, 2):  # Service, Message
                cell.get_text().set_ha("left")
            cell.PAD = 0.06

    fig.text(
        0.5,
        0.06,
        "Level Enc.: INFO=0, WARN=1, ERROR=2  |  Error Freq uses rolling window of 10 logs",
        ha="center",
        va="center",
        fontsize=9,
        color="#475569",
    )
    _save(fig, output_dir / "fig04_feature_engineering_table.png")


def generate_severity_logic_chart(output_dir: Path, data: dict[str, Any]) -> None:
    scores = np.array(data["scores"], dtype=float)
    quantiles = data.get("quantiles")
    if not isinstance(quantiles, dict):
        quantiles = {
            0.10: float(np.percentile(scores, 10)),
            0.25: float(np.percentile(scores, 25)),
            0.50: float(np.percentile(scores, 50)),
        }

    q10 = quantiles.get(0.10, float(np.percentile(scores, 10)))
    q25 = quantiles.get(0.25, float(np.percentile(scores, 25)))
    q50 = quantiles.get(0.50, float(np.percentile(scores, 50)))

    sample_score = float(np.median(scores))
    sample_severity = severity_from_anomaly_score(sample_score, quantiles)

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5))
    fig.suptitle("Quantile-Based Severity Mapping", fontsize=17, fontweight="bold")

    ax1.hist(scores, bins=25, color="#93c5fd", edgecolor="#1e3a8a", alpha=0.85)
    ax1.axvline(q10, color="#dc2626", linestyle="--", linewidth=1.6, label=f"Q10 ({q10:.3f})")
    ax1.axvline(q25, color="#f97316", linestyle="--", linewidth=1.6, label=f"Q25 ({q25:.3f})")
    ax1.axvline(q50, color="#f59e0b", linestyle="--", linewidth=1.6, label=f"Q50 ({q50:.3f})")
    ax1.set_title("Anomaly Score Distribution")
    ax1.set_xlabel("Decision Score (lower = more anomalous)")
    ax1.set_ylabel("Count")
    ax1.grid(axis="y", alpha=0.25)
    ax1.legend(fontsize=8)

    bands = [
        ("Critical", -0.5, q10, "#ef4444"),
        ("High", q10, q25, "#f97316"),
        ("Medium", q25, q50, "#f59e0b"),
        ("Low", q50, 0.5, "#10b981"),
    ]
    for name, start, end, color in bands:
        ax2.axvspan(start, end, alpha=0.22, color=color, label=name)
    ax2.scatter([sample_score], [0.5], color="#1e293b", s=60, zorder=5)
    ax2.text(sample_score + 0.01, 0.56, f"Sample: {sample_score:.3f} ({sample_severity})", fontsize=9)
    ax2.set_xlim(min(-0.5, scores.min() - 0.05), max(0.5, scores.max() + 0.05))
    ax2.set_ylim(0, 1)
    ax2.set_yticks([])
    ax2.set_xlabel("Decision Score")
    ax2.set_title("Severity Bands from Quantiles")
    ax2.grid(axis="x", alpha=0.2)
    ax2.legend(loc="upper right", fontsize=8)

    _save(fig, output_dir / "fig05_severity_mapping_logic.png")


def generate_results_charts(output_dir: Path, data: dict[str, Any]) -> None:
    logs = data["logs"]
    severities = data["severities"]
    predictions = data["predictions"]
    scores = data["scores"]

    severity_order = ["Critical", "High", "Medium", "Low"]
    severity_counts = Counter(severities)
    counts = [severity_counts.get(level, 0) for level in severity_order]

    level_counts = Counter(entry["level"] for entry in logs)
    level_labels = ["INFO", "WARN", "ERROR"]
    level_values = [level_counts.get(lvl, 0) for lvl in level_labels]

    anomalies = np.array([1 if p == -1 else 0 for p in predictions], dtype=int)
    anomaly_cumulative = np.cumsum(anomalies)
    x = np.arange(1, len(logs) + 1)

    fig, axes = plt.subplots(2, 2, figsize=(14, 9))
    fig.suptitle("LogSight Run Summary", fontsize=18, fontweight="bold")

    axes[0, 0].bar(severity_order, counts, color=["#ef4444", "#f97316", "#f59e0b", "#10b981"])
    axes[0, 0].set_title("Severity Distribution")
    axes[0, 0].set_ylabel("Count")
    axes[0, 0].grid(axis="y", alpha=0.25)

    axes[0, 1].pie(
        level_values,
        labels=level_labels,
        autopct="%1.0f%%",
        colors=["#94a3b8", "#f59e0b", "#ef4444"],
        startangle=120,
    )
    axes[0, 1].set_title("Log Level Split")

    axes[1, 0].plot(x, scores, linewidth=1.5, color="#2563eb")
    axes[1, 0].axhline(0.0, linestyle="--", color="#ef4444", linewidth=1)
    axes[1, 0].set_title("Anomaly Scores Over Logs")
    axes[1, 0].set_xlabel("Log Index")
    axes[1, 0].set_ylabel("Decision Score")
    axes[1, 0].grid(alpha=0.25)

    axes[1, 1].plot(x, anomaly_cumulative, linewidth=1.8, color="#7c3aed")
    axes[1, 1].set_title("Cumulative Anomalies (predict == -1)")
    axes[1, 1].set_xlabel("Log Index")
    axes[1, 1].set_ylabel("Total Anomalies")
    axes[1, 1].grid(alpha=0.25)

    _save(fig, output_dir / "fig06_results_summary.png")


def write_figure_manifest(output_dir: Path) -> None:
    manifest = """Figure 1: LogSight system architecture.
Figure 2: LogSight processing workflow.
Figure 3: Example of regex-based log parsing.
Figure 4: Feature engineering outputs used by the model.
Figure 5: Quantile-based severity mapping from anomaly scores.
Figure 6: Experimental run summary (severity, levels, scores, anomalies from model predictions).
"""
    (output_dir / "figure_captions.txt").write_text(manifest, encoding="utf-8")


def main() -> None:
    args = _parse_args()
    output_dir = Path(args.output_dir)
    log_file = Path(args.log_file)
    data = _collect_data(log_file=log_file, max_logs=args.max_logs)

    generate_architecture_diagram(output_dir)
    generate_pipeline_diagram(output_dir)
    generate_parsing_example(output_dir)
    generate_feature_table(output_dir, data)
    generate_severity_logic_chart(output_dir, data)
    generate_results_charts(output_dir, data)
    write_figure_manifest(output_dir)

    print(f"Generated figures in: {output_dir.resolve()}")


if __name__ == "__main__":
    main()
