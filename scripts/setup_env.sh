#!/usr/bin/env bash
# Simple setup script for the project (macOS / zsh)
set -euo pipefail

VENV=.venv310
PYTHON=/opt/homebrew/bin/python3.10

if [ ! -x "$PYTHON" ]; then
  echo "Python 3.10 not found at $PYTHON. Please install Python 3.10 or update the script." >&2
  exit 1
fi

echo "Creating virtualenv $VENV"
$PYTHON -m venv "$VENV"
source "$VENV/bin/activate"
python -m pip install --upgrade pip setuptools wheel
echo "Installing requirements for foodrescue-agent"
pip install -r foodrescue-agent/requirements.txt
echo "Setup complete. Activate with: source $VENV/bin/activate"
