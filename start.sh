#!/bin/bash

# Exit if any command fails
set -e

# Check if venv exists
if [ ! -d ".venv" ]; then
  echo "Creating virtual environment..."
  python3 -m venv .venv
fi

# Activate the venv
source .venv/bin/activate

# Install dependencies
echo "Installing Python dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

# Run FastAPI backend in background
echo "Starting FastAPI backend..."
nohup uvicorn server:app --host localhost --port 8000 > fastapi.log 2>&1 &

# Run Streamlit frontend
echo "Starting Streamlit app..."
streamlit run app.py
