# Submission README

This folder contains the Kaggle submission files and the minimal assets and instructions reviewers need to reproduce the results.

Included files
- `submission.csv` — final predictions (id, prediction)
- `assets/thumbnail.png` — project thumbnail (1200×630)
- `FINAL_SUBMISSION.md` — concise submission description and instructions for reviewers
- `KAGGLE_CODE_SNIPPET.md` — a short runnable snippet to reproduce the headless run
- `RELEASE_NOTES.md` — release notes describing the package contents
- `submission.zip.sha256` — SHA256 checksum of `submission.zip` (also present at repo root)

Reproduce the submission (recommended quick steps)
1. From the project root, create and activate a Python 3.10+ virtualenv:
```
python3.10 -m venv .venv310
source .venv310/bin/activate
```
2. Install dependencies:
```
pip install -r foodrescue-agent/requirements.txt
```
3. Generate demo data and run the headless submission (example):
```
python scripts/generate_demo_data.py
python scripts/kaggle_run.py --session daily_20251128 --out submission/submission.csv
```
4. (Optional) Regenerate the thumbnail:
```
python scripts/generate_thumbnail.py --session daily_20251128 --out submission/assets/thumbnail.png
```

Security note
- No API keys or secrets are included in this folder. To enable Gemini features locally, set `GEMINI_API_KEY` in your environment or `foodrescue-agent/.env` (do NOT commit keys).

If you want me to further trim or add a single-page PDF summary for the Kaggle submission, tell me and I will generate it.
