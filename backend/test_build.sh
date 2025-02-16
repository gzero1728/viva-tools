#!/bin/bash

echo "Creating virtual environment..."
python -m venv .venv

echo "Activating virtual environment..."
source .venv/bin/activate

echo "Installing dependencies..."
pip install -r requirements.txt

echo "Testing the application..."
PYTHONPATH=$PYTHONPATH:. uvicorn src.main:app --host 0.0.0.0 --port 8000 