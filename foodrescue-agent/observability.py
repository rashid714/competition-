"""Simple observability helper: in-memory metrics and JSON flush for logs."""
import threading
import time
import json
import os
from typing import Any, Dict

_lock = threading.Lock()
_metrics: Dict[str, Any] = {
    'counters': {},
    'gauges': {},
    'timers': {}
}

LOG_DIR = os.path.join(os.path.dirname(__file__), '..', 'logs')
os.makedirs(LOG_DIR, exist_ok=True)


def incr(name: str, amount: int = 1) -> None:
    with _lock:
        _metrics['counters'][name] = _metrics['counters'].get(name, 0) + amount


def gauge(name: str, value: float) -> None:
    with _lock:
        _metrics['gauges'][name] = float(value)


def timing(name: str, seconds: float) -> None:
    with _lock:
        _metrics['timers'][name] = float(seconds)


def snapshot() -> Dict[str, Any]:
    with _lock:
        return json.loads(json.dumps(_metrics))


def flush(path: str = None) -> str:
    """Write metrics snapshot to a JSON file and return the file path."""
    snap = snapshot()
    ts = int(time.time())
    if path is None:
        path = os.path.join(LOG_DIR, f"metrics_{ts}.json")
    with open(path, 'w') as f:
        json.dump(snap, f, indent=2)
    return path
