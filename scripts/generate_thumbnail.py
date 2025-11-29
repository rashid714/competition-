"""Generate a thumbnail PNG by running the parallel agents and plotting results.

Saves `assets/thumbnail.png` and prints the path.
"""
import os
import json
from pathlib import Path

WORK_DIR = Path(__file__).resolve().parent.parent
ASSETS_DIR = WORK_DIR / 'assets'
ASSETS_DIR.mkdir(exist_ok=True)

def main(session_id=None, out_path=None):
    # Local import to avoid heavy deps at module import time
    # Make the agent module importable (agents live in the `foodrescue-agent` folder)
    import sys
    agent_dir = str(WORK_DIR / 'foodrescue-agent')
    if agent_dir not in sys.path:
        sys.path.insert(0, agent_dir)
    from agent import FoodRescueAgent
    import plotly.express as px
    import pandas as pd

    if out_path is None:
        out_path = ASSETS_DIR / 'thumbnail.png'
    else:
        out_path = Path(out_path)

    agent = FoodRescueAgent()
    # pick session_id default if not provided
    if not session_id:
        # choose the latest session file
        import glob
        sessions = glob.glob(str(WORK_DIR / 'session_data' / '*.json'))
        if not sessions:
            raise SystemExit('No sessions found: run scripts/generate_demo_data.py first')
        session_id = Path(sessions[-1]).stem

    res = agent.run_multi_agents(session_id)
    results = res.get('orchestration', {}).get('results', {})

    # Prefer allocations if available, else summary totals
    if 'allocations' in results:
        df = pd.DataFrame(list(results['allocations'].items()), columns=['store', 'fraction'])
        df['score'] = df['fraction']
        title = f"Allocations — {session_id}"
        fig = px.bar(df, x='store', y='score', title=title, color='store')
    elif 'summary' in results:
        summary = results['summary']
        df = pd.DataFrame([summary])
        title = f"Summary — {session_id}"
        fig = px.bar(x=['total_weight'], y=[summary.get('total_weight', 0)], title=title)
    else:
        # fallback: write a tiny placeholder image
        import PIL.Image as Image, PIL.ImageDraw as ImageDraw, PIL.ImageFont as ImageFont
        img = Image.new('RGBA', (1200, 630), (255, 255, 255, 255))
        d = ImageDraw.Draw(img)
        text = 'FoodRescue\nNo visual data available'
        try:
            font = ImageFont.load_default()
        except Exception:
            font = None
        d.multiline_text((40, 40), text, fill=(20, 20, 20), font=font)
        img.save(out_path)
        print(out_path)
        return str(out_path)

    fig.update_layout(margin=dict(l=20, r=20, t=50, b=20), template='plotly_white')
    # write PNG
    fig.write_image(str(out_path), width=1200, height=630)
    print(out_path)
    return str(out_path)


if __name__ == '__main__':
    import argparse
    p = argparse.ArgumentParser()
    p.add_argument('--session', '-s', help='session id (optional)')
    p.add_argument('--out', '-o', help='output path for thumbnail PNG')
    args = p.parse_args()
    main(args.session, args.out)
