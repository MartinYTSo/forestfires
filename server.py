from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
import geopandas as gpd
import numpy as np
import pandas as pd
import requests
import joblib
import json
import time
import logging
from LAMapRendering import LACountyMap
import base64
from predictor import XGBoostPredictor
from fastapi.responses import JSONResponse
# Initialize FastAPI app
app = FastAPI()

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Globals
submitted_data = None


# Logging on startup
@app.on_event("startup")
async def startup_event():
    logger.info("Starting FastAPI app...")

    logger.info("Loading Datasets...")
    time.sleep(1)

    logger.info("Loading model...")
    time.sleep(1)
    logger.info("Model loaded!")

    logger.info("Preparing reference data...")
    time.sleep(1)
    logger.info("Reference data loaded.")

    logger.info("Server is ready to accept requests.\n")

# Root endpoint
@app.get("/")
def root():
    return {"message": "FastAPI server running"}

# Style function for fire hazard zones


# Preprocess submitted form data

# API endpoint to receive form data
@app.post("/submit_form/")
async def receive_form_data(data: dict):
    global submitted_data
    submitted_data = data
    return {"message": "Data received successfully"}

# API endpoint to return the latest submitted data
@app.get("/get_data/")
def get_submitted_data():
    return submitted_data

# API endpoint to run prediction

@app.get("/get_df_predictions/")
def get_map():
    global submitted_data
    if not submitted_data:
        return {"error": "No data submitted yet."}

    # Load predictor model (or import your predictor class)
    model = XGBoostPredictor(submitted_data,"data/LA Prices 2019-2023 and Census.csv")
    # logger.info(f"submitted_data: {submitted_data}") #debug 
    
    # input_df = pd.DataFrame(submitted_data)
    logger.info(f"submitted_data: {submitted_data}")
    logger.info(f"submitted_data: {type(submitted_data)}")

    # Predict prices
    predicted_prices_df = model.predict_price()
    # predicted_prices_df=pd.DataFrame(predicted_prices_df)
    # logger.info(f"submitted_data: {predicted_prices_df}")

    
    return predicted_prices_df.to_dict(orient='records')
