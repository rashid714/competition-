Release Notes — FoodRescue Capstone

Version: 1.0.0
Date: 2025-11-28

Summary
- Polished UI to a single dark professional theme.
- Added safe, lazy Gemini integration with validation and fallback messages.
- Implemented parallel agent prototype (Summarizer, Allocator, Reporter) with observability.
- Added reproducible scripts and a Kaggle notebook to generate `submission.csv` and the thumbnail.

Important security fix
- Removed an accidentally included API key from `.env.example` and replaced it with a placeholder. If you previously added any real keys to repository files, rotate/revoke them now.

Included artifacts
- `submission.zip` (packaged submission files)
- `submission/*` — pitch, README, assets, and notebook

How to reproduce
- See `submission/FINAL_SUBMISSION.md` and `README.md` for exact commands.
