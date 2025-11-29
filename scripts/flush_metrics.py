"""CLI helper to flush observability metrics to a JSON file.

Usage:
    python scripts/flush_metrics.py
Returns the path to the flushed metrics JSON file.
"""
import sys
from foodrescue_agent.observability import flush


def flush_metrics():
    path = flush()
    print(path)
    return path


if __name__ == '__main__':
    flush_metrics()
