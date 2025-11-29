# Quick code snippet for the Kaggle "Code" section

Use this snippet in the Kaggle Code / Notebook area to help reviewers reproduce the submission artifacts quickly.

Commands (copy into a notebook cell or the Code panel in Kaggle):

```bash
# 1) Create and activate Python 3.10 venv (if supported in the environment)
python3.10 -m venv .venv310
source .venv310/bin/activate
.venv310/bin/python -m pip install --upgrade pip setuptools wheel
.venv310/bin/python -m pip install -r foodrescue-agent/requirements.txt

# 2) Generate demo data and a sample submission
python scripts/generate_demo_data.py
python scripts/kaggle_run.py --session daily_YYYYMMDD --out submission.csv

# 3) Generate thumbnail (optional)
python scripts/generate_thumbnail.py --session daily_YYYYMMDD

# 4) Inspect outputs
ls -lh submission.csv submission/assets/thumbnail.png
```

Notes
- If you want AI-backed reports in the notebook, set the environment variable `GEMINI_API_KEY` in the kernel (do NOT share keys publicly).
- The notebook `notebooks/kaggle_capstone_notebook.ipynb` already contains runnable cells that mirror these steps with explanatory text.
