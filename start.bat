@echo off
echo Installing Python dependencies...
pip install --upgrade pip
pip install -r requirements.txt

echo Starting FastAPI backend...
start "FastAPI Server" cmd /k "uvicorn server:app --host localhost --port 8000"

echo Starting Streamlit app...
streamlit run app.py
