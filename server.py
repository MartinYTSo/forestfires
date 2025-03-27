from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
import geopandas as gpd
import folium
import numpy as np 
import pandas as pd
import requests
import joblib
import json 
app = FastAPI()
fire_hazard_path =  "data/Fire_Hazard_Severity_Zones.geojson"
fire_hazard_zones = gpd.read_file(fire_hazard_path)
test_data = pd.read_csv("data/LA Prices 2019-2023 and Census.csv")

model = joblib.load("lgbm_model_full.joblib")


m = folium.Map(location=[34.05, -118.25], zoom_start=9)


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # adjust this in production
    allow_methods=["*"],
    allow_headers=["*"],
)


##store submitted data 
submitted_data = None # oonly store the latest

# Define fire hazard color mapping

def fire_hazard_style(feature):
    hazard = feature["properties"].get("HAZ_CLASS", "Unknown")  # Get hazard classification
    color_dict = {
        "Moderate": "yellow",
        "High": "orange",
        "Very High": "red"
    }
    return {
        "color": "black",  # Black border for all zones
        "weight": 1.2,  
        "fillColor": color_dict.get(hazard, "gray"),  # Default gray if unknown
        "fillOpacity": 0.5
    }
    
    
    
def map_property_type(df, column_name="Property Type"):
    mapping = {
        "Single Family Residential": 3,
        "Low Density Residential": 2,
        "Condominium": 1
    }
    df["Property Type"] = df[column_name].map(mapping)
    df['Log_Improvement_Value'] = np.log1p(df['Improvement Value'])
    df['Log_Square_Footage'] = np.log1p(df['Square Footage'])

    return df

@app.get("/", response_class=HTMLResponse)
def get_map():
    m = folium.Map(location=[34.05, -118.25], zoom_start=9, tiles="cartodbpositron")
    folium.GeoJson(fire_hazard_zones, name="Fire Hazard Zones", style_function=fire_hazard_style).add_to(m)
    folium.TileLayer(
        tiles="https://basemap.nationalmap.gov/arcgis/rest/services/USGSTopo/MapServer/tile/{z}/{y}/{x}",
        attr="UGS National Map",
        name="USGS Elevation (Contours)",
        overlay=False).add_to(m)
    folium.LayerControl().add_to(m)

    return HTMLResponse(m._repr_html_())

@app.post("/submit_form/")
async def receive_form_data(data: dict):
    global submitted_data
    submitted_data = data
    return {"message": "Data received successfully"}

@app.get("/get_data/")
def get_submitted_data():
    return submitted_data


@app.get("/LGBMPredict")
def predict_price():
    global submitted_data
    if submitted_data is None:
        return {"error": "No data submitted yet."}

    # submitted_data_to_json=json.loads(submitted_data.text)
    # submitted_data_to_json = submitted_data.json()
    dataframe = pd.DataFrame([submitted_data])
    dataframe = map_property_type(dataframe)

    sample = test_data[['Zip Code', 'Roll Year']]
    sample_df = sample.groupby("Zip Code").mean().reset_index()
    repeated_df = pd.concat([dataframe] * len(sample_df), ignore_index=True)
    combined = pd.concat([sample_df, repeated_df], axis=1)

    combined = combined.rename(columns={
        "Housing Cost (%)": "Housing Cost % of Income",
        "Property Type": "Property Use Type Encoded"
    })

    feature_columns = [
        "Zip Code", "Roll Year", "Number of Buildings", "Bathrooms", "Number of Units",
        "Property Use Type Encoded", "Median Income", "Housing Cost % of Income",
        "Building Age", "Log_Improvement_Value", "Log_Square_Footage"
    ]

    categorical_cols = ["Zip Code", "Property Use Type Encoded"]
    for col in categorical_cols:
        combined[col] = combined[col].astype("category")

    predictions = model.predict(combined[feature_columns])
    combined["Predicted Price"] = predictions

    return combined.to_dict(orient="records")