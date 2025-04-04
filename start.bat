@echo off
SETLOCAL

REM Check if venv exists
IF NOT EXIST ".venv" (
    echo Creating virtual environment...
    python -m venv .venv
)

REM Activate venv
call .venv\Scripts\activate.bat

REM Install requirements
echo Installing Python dependencies...
pip install --upgrade pip
pip install -r requirements.txt

REM Start FastAPI server in a new terminal
start "FastAPI Server" cmd /k ".venv\Scripts\activate.bat && uvicorn server:app --host localhost --port 8000"

REM Start Streamlit app
echo Starting Streamlit app...
streamlit run app.py

ENDLOCAL
