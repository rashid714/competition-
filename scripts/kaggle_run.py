"""Headless runner to produce a Kaggle-style submission.csv using the app's models.

This script loads demo donations, runs the impact/report generation pipeline
and writes a simple `submission.csv` with `id,prediction` columns as an example.

Usage: python scripts/kaggle_run.py --session <session_id>
"""
import os
import sys
import argparse
import csv
import json

WORKSPACE_ROOT = os.path.dirname(os.path.dirname(__file__))
# Ensure the agent package directory is on sys.path so imports like `from agent import FoodRescueAgent` work
AGENT_DIR = os.path.join(WORKSPACE_ROOT, 'foodrescue-agent')
if AGENT_DIR not in sys.path:
    sys.path.insert(0, AGENT_DIR)

from memory import Memory
from agent import FoodRescueAgent


def build_submission(session_id, out_path='submission.csv'):
    # Memory expects its default data_dir; change CWD so it resolves correctly
    mem = Memory()
    agent = FoodRescueAgent()

    donations = mem.get_donations(session_id)
    if not donations:
        print(f"No donations found for session '{session_id}'")
        return 1

    dashboard = agent.get_dashboard(session_id)

    # Example prediction: ranking stores by total weight descending
    totals = {}
    for d in donations:
        store = d.get('store', 'unknown')
        totals[store] = totals.get(store, 0) + float(d.get('weight', 0))

    ranked = sorted(totals.items(), key=lambda kv: -kv[1])

    # Create a simple submission mapping store -> score
    with open(out_path, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['id', 'prediction'])
        for i, (store, total) in enumerate(ranked):
            writer.writerow([store, round(total, 1)])

    print(f"Wrote submission to {out_path}")
    return 0


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--session', '-s', required=True, help='session id (demo file stem)')
    p.add_argument('--out', '-o', default='submission.csv')
    args = p.parse_args()

    return build_submission(args.session, args.out)


if __name__ == '__main__':
    raise SystemExit(main())
