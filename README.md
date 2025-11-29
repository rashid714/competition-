# FoodRescue — Competition Agent & Kaggle Submission Kit

FoodRescue is a reproducible multi-agent prototype that helps community food coordinators log surplus donations, calculate impact metrics, and generate donor-facing reports. The repository is trimmed specifically for Kaggle review: every script, notebook, and asset required to recreate the final submission is included, nothing more.

## Why this repo
- **Deterministic**: JSON-backed memory, schema validation, and lightweight observability make runs auditable.
- **Multi-agent orchestration**: Summarizer, Allocator, Reporter, and optional GeminiReporter work in parallel with retries and fallbacks.
- **Turnkey Kaggle packaging**: One command produces `submission.csv`, thumbnail, release notes, and SHA256 checksum.
- **Safety-first AI**: Gemini integration is opt-in, lazily initialized, validated, and wrapped with deterministic fallbacks so outputs never block delivery.

## Architecture at a glance
![FoodRescue architecture diagram](assets/architecture.svg)

1. **Donor inputs** (demo JSON sessions or live Streamlit form) feed the Memory layer.
2. **Memory & validation** enforces schemas, cleans data, and exposes session APIs.
3. **Parallel agents** (Summarizer, Allocator, Reporter, GeminiReporter) process the session concurrently.
4. **Streamlit UI & Observability** present dashboards and expose health/metrics endpoints.
5. **Automation scripts** (`generate_demo_data.py`, `kaggle_run.py`, `generate_thumbnail.py`) produce the Kaggle artifacts: `submission.csv`, thumbnail, release notes, etc.

## Repository layout
- `foodrescue-agent/` — Streamlit app, agent orchestration, memory, observability utilities, and CSS theme.
- `scripts/` — reproducible automation: demo data generator, Kaggle headless runner, thumbnail exporter, metrics flush, env setup.
- `submission/` — cleaned Kaggle package (`submission.csv`, README, release notes, thumbnail, checksum, summary doc).
- `notebooks/kaggle_capstone_notebook.ipynb` — end-to-end reproducible notebook for Kaggle Code section.
- `assets/architecture.svg` — diagram referenced above (safe to reuse in presentations/pitch decks).
- `Makefile` — convenience shortcuts (create venv, run tests, package submission).

## Quick start (macOS/Linux)
> Commands assume zsh and Python 3.10+. Adjust paths if your interpreter lives elsewhere.

### 1. Clone & create a virtual environment
```bash
git clone https://github.com/rashid714/competition-.git foodrescue
cd foodrescue
/opt/homebrew/bin/python3.10 -m venv .venv310
source .venv310/bin/activate
python -m pip install --upgrade pip setuptools wheel
pip install -r foodrescue-agent/requirements.txt
```

### 2. Run automated demo & produce submission
```bash
python scripts/generate_demo_data.py
python scripts/kaggle_run.py --session daily_20251128 --out submission/submission.csv
```

### 3. Launch the Streamlit UI
```bash
streamlit run foodrescue-agent/app.py
```
Use the left sidebar to toggle demo mode, enable Gemini (optional), and view health diagnostics.

### 4. Generate thumbnail & metrics (optional but recommended)
```bash
python scripts/generate_thumbnail.py --session daily_20251128 --out submission/assets/thumbnail.png
python scripts/flush_metrics.py
```

### 5. Package everything for Kaggle reviewers
```bash
zip -r submission.zip submission
shasum -a 256 submission.zip > submission/submission.zip.sha256
```
The repo already ships with a cleaned `submission/` folder and a ready-made `submission.zip`, but the commands above let you regenerate from scratch.

## How the agent works
1. **Ingestion & memory**: Donations are logged via Streamlit or loaded from `session_data/*.json`. `memory.py` validates payloads, merges sessions, and exposes typed helpers.
2. **Parallel agents** (`prototype_agents.py`):
	- *Summarizer*: totals weight, meals, stores, and donation counts.
	- *Allocator*: produces a normalized allocation table for partner organizations.
	- *Reporter*: crafts donor-facing copy; uses deterministic templates when AI is disabled.
	- *GeminiReporter* (optional): wraps Google Gemini with retries/backoff, tone/length validation, and safe fallbacks.
3. **FoodRescueAgent** orchestrates memory lookups, kicks off the thread pool, and returns a dashboard-ready payload consumed by Streamlit, scripts, and the notebook.
4. **Automation**: `generate_demo_data.py` seeds reproducible sessions, `kaggle_run.py` writes the official `submission.csv`, and `generate_thumbnail.py` renders a 1200×630 Plotly/Kaleido graphic for Kaggle listings.

## Gemini / API key configuration (optional)
1. Obtain a Gemini API key from [ai.google.dev](https://ai.google.dev/).
2. Set it locally (never commit secrets):
```bash
export GEMINI_API_KEY="sk-your-key"
# or create foodrescue-agent/.env and add GEMINI_API_KEY there
```
3. Restart Streamlit or rerun scripts. The sidebar shows real-time health, and Reporter gracefully falls back if Gemini is unavailable or returns an empty response.

## Kaggle submission workflow
1. Run the commands in **Quick start** to regenerate `submission/submission.csv` and `submission/assets/thumbnail.png`.
2. Upload `notebooks/kaggle_capstone_notebook.ipynb` to Kaggle Code > New Notebook (set to GPU Off, Internet Off for reproducibility).
3. In the Kaggle “Data” tab, upload `submission.zip` (contains README, release notes, thumbnail, checksum, and the CSV).
4. Copy/paste short/long descriptions from `submission/FINAL_SUBMISSION.md`.
5. Attach `submission/assets/thumbnail.png` as the competition thumbnail.
6. Submit `submission/submission.csv` in the competition portal.

## Troubleshooting
- **`ModuleNotFoundError`**: ensure `foodrescue-agent` is on `PYTHONPATH` (the scripts do this automatically) or run commands from repo root after activating the venv.
- **Gemini errors (404 or quota)**: confirm the key has access to the chosen model (`gemini-1.5-flash`). The Reporter logs warnings and falls back automatically.
- **Plotly/Kaleido export fails**: install a Chromium browser or set `KaleidoScope` path via env vars (macOS with Chrome/Edge works out of the box).
- **Streamlit warnings about `ScriptRunContext`**: they appear only if you import `app.py` directly. Use `streamlit run foodrescue-agent/app.py` instead.

## License
This project is released under the MIT License. See [LICENSE](LICENSE) for details.

Need refinements (CI pipeline, extra benchmarks, more visual polish)? Open an issue or reach out and I’ll extend the agent to match your competition goals.
