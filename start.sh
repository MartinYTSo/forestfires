#!/bin/bash

# Exit if any command fails
set -e

echo "Installing Python dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

echo "Starting FastAPI backend..."
nohup uvicorn server:app --host localhost --port 8000 > fastapi.log 2>&1 &

echo "Starting Streamlit app..."
streamlit run app.py
