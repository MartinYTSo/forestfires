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
from predictor import PropertyPricePredictor
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
    model = PropertyPricePredictor("lgbm_model_full.joblib","data/LA Prices 2019-2023 and Census.csv")
    # logger.info(f"submitted_data: {submitted_data}") #debug 
    
    input_df = pd.DataFrame(submitted_data)
    logger.info(f"submitted_data: {input_df}")

    # Predict prices
    predicted_prices_df = model.predict(input_df) 
    predicted_prices_df=pd.DataFrame(predicted_prices_df)
    logger.info(f"submitted_data: {predicted_prices_df}")

    

    # elev_df = pd.read_csv("data/elevation_data_downsampled.csv")
    # map_obj = LACountyMap(predicted_prices_df, elev_df, "data/LA_County_ZIP_Codes.geojson")
    # map_obj.load_and_prepare_data()
    # deck_json = map_obj.generate_map()  # Returns the pydeck JSON (not actual image)
    # with open("data/colorbar_legend_vertical.png", "rb") as img_file:
        # legend_base64 = base64.b64encode(img_file.read()).decode()
    
    return predicted_prices_df.to_dict(orient='records')
    # return JSONResponse(content={
    #     "deck_json": deck_json,
    #     "legend_image": legend_base64
    # })