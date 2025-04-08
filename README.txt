DESCRIPTION
This project is for Georgia Tech’s CSE 6242 course. It predicts real estate prices in Los Angeles County based on wildfire risk. It features Streamlit and FastAPI for both front end and back end servers. It uses a boosting algorithm (XGBoost) which is trained on zip-level housing and environmental data to predict house prices. The app displays predicted prices visually on an interactive map. This helps users understand how fire risk affects real estate value.

INSTALLATION

Option 1: One-Click Installation (Windows/Mac)
1. Clone the repo.

2. Download the data files https://www.dropbox.com/scl/fo/e9f78zxipm0zev27khcs6/ABtPqI4RZWsonqLRZZATccYrlkey=y0l2c57l9ca4vep7acpuejmgp&st=egipoh09&dl=0

 and move them to the data/ folder.


3.
Windows: Run start.bat

Mac (make sure you run this command in the folder): 

chmod +x start.sh
./start.sh

Option 2: Manual Installation (Recommended for Developers)
1. Clone the repo and download data as above.
2. Create and activate a Python virtual environment (e.g., .venv).
3. Run pip install -r requirements.txt.
4. In one terminal, run uvicorn server:app --host localhost --port 8000.
5. In another terminal, run streamlit run app.py.

EXECUTION

1. Ensure your directory structure matches this:
APP/
├── data/
├── model/
├── .venv/
├── app.py
├── LAMapRendering.py
├── predictor.py
├── server.py
└── requirements.txt

2. Launch backend: uvicorn server:app --host localhost --port 8000
3. Launch frontend: streamlit run app.py
4. Access the app via browser (Streamlit will auto-open).

To shut down: Close the Streamlit terminal, and press Ctrl+C in the FastAPI terminal.

To uninstall:
- One-click: pip uninstall -r requirements.txt -y
- Manual: Delete the root folder.

If you wish to view how we collected and cleaned the data, please view Data Processing Instructions.pdf

