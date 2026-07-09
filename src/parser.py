from __future__ import annotations

from datetime import datetime
import re
from typing import Dict, List, Optional

LOG_PATTERN = re.compile(
    r"^(?P<date>\d{4}-\d{2}-\d{2})\s+(?P<time>\d{2}:\d{2}:\d{2})\s+"
    r"(?P<level>INFO|WARN|ERROR|WARNING)\s+(?P<service>\S+)\s+(?P<message>.+)$"
)


def parse_log_line(line: str) -> Optional[Dict[str, str]]:
    """Parse one log line into a structured dictionary."""
    raw = line.strip()
    if not raw:
        return None

    match = LOG_PATTERN.match(raw)
    if not match:
        return None

    level = match.group("level")
    if level == "WARNING":
        level = "WARN"

    timestamp_str = f"{match.group('date')} {match.group('time')}"
    timestamp = datetime.strptime(timestamp_str, "%Y-%m-%d %H:%M:%S")

    return {
        "raw_line": raw,
        "timestamp": timestamp.isoformat(sep=" "),
        "level": level,
        "service": match.group("service"),
        "message": match.group("message").strip(),
    }


def parse_log_file(file_path: str) -> List[Dict[str, str]]:
    """Read and parse all valid log lines from a file."""
    parsed_logs: List[Dict[str, str]] = []

    with open(file_path, "r", encoding="utf-8") as log_file:
        for line in log_file:
            parsed = parse_log_line(line)
            if parsed:
                parsed_logs.append(parsed)

    return parsed_logs
