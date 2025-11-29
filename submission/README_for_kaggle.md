# Submission README (Minimal)

This folder contains the exact files reviewers need to evaluate the submission.

Files included
- `submission.csv` — final CSV to upload to the competition (id, prediction)
- `assets/thumbnail.png` — 1200×630 thumbnail used in the listing
- `FINAL_SUBMISSION.md` — short submission description for the competition page
- `KAGGLE_CODE_SNIPPET.md` — brief headless command snippet to reproduce the CSV
- `RELEASE_NOTES.md` — high-level changelog

Quick reviewer instructions
1. Download `submission.zip` and verify checksum (optional):
```
shasum -a 256 submission.zip
```
2. Inspect `submission.csv` and upload to the competition.

Optional (reproducibility, only if you want to re-run):
```
# from repo root (dev environment)
python -m venv .venv
source .venv/bin/activate
pip install -r foodrescue-agent/requirements.txt
python scripts/kaggle_run.py --session daily_YYYYMMDD --out submission/submission.csv
```

Security
- No secrets or API keys are included. Set `GEMINI_API_KEY` locally only if you want to enable AI features.

That's it — everything else in the repository is for development. This README is intentionally minimal for Kaggle reviewers.
