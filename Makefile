VENV=.venv310
PYTHON=/opt/homebrew/bin/python3.10

.PHONY: venv install demo thumbnail test clean

venv:
	$(PYTHON) -m venv $(VENV)
	@echo "Created venv: $(VENV)"

install: venv
	source $(VENV)/bin/activate && pip install --upgrade pip setuptools wheel
	source $(VENV)/bin/activate && pip install -r foodrescue-agent/requirements.txt

demo:
	source $(VENV)/bin/activate && python scripts/generate_demo_data.py

submission: demo
	source $(VENV)/bin/activate && python scripts/kaggle_run.py --session daily_$(shell date +%Y%m%d) --out submission.csv

thumbnail:
	source $(VENV)/bin/activate && python scripts/generate_thumbnail.py --session daily_$(shell date +%Y%m%d)

test:
	source $(VENV)/bin/activate && pytest -q

clean:
	rm -rf $(VENV) .pytest_cache __pycache__ session_data/*.json assets/*.png submission/assets/*.png
