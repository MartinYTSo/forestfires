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
from functools import lru_cache
from folium import Choropleth

app = FastAPI()

@lru_cache(maxsize=1)
def get_fire_hazard_data():
    return gpd.read_file("data/Fire_Hazard_Severity_Zones.geojson")

@lru_cache(maxsize=1)
def get_census_data():
    return pd.read_csv("data/LA Prices 2019-2023 and Census.csv")

@lru_cache(maxsize=1)
def read_data_zipcodes():
    geodata= gpd.read_file('data/LA_County_ZIP_Codes.geojson')
    return geodata 




# fire_hazard_zones = gpd.read_file(fire_hazard_path)
# test_data = pd.read_csv("data/LA Prices 2019-2023 and Census.csv")

fire_hazard_zones = get_fire_hazard_data()
census_data = get_census_data()
geojson_df_zip=read_data_zipcodes()

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
zipcode_data=None 
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

@app.get("/get_data_with_predictions/")
def get_submitted_data():
    return submitted_data


@app.post("/retrieve_calculated_dataframe/")
def get_calculated_dataframe(data_zip:dict):
    global latest_zipcode_data
    latest_zipcode_data=data_zip['data']
    print("📩 Received POST at /get_calculated_dataframe/:", latest_zipcode_data)  #
    return  latest_zipcode_data

@app.get("/get_zipcode/") #for debugging gettting dataframe 
def get_submitted_data():
    return latest_zipcode_data

@app.get("/render_map/", response_class=HTMLResponse)
def render_map():
    global latest_zipcode_data, geojson_df_zip
    latest_zipcode_data=pd.DataFrame(latest_zipcode_data)

    test_df_prepare_to_join = latest_zipcode_data[['Zip Code', 'Predicted Price']]
    test_df_prepare_to_join['Zip Code'] = test_df_prepare_to_join['Zip Code'].astype(int)
    geojson_df_zip['ZIPCODE'] = geojson_df_zip['ZIPCODE'].astype(int)

    gdf = geojson_df_zip.merge(
        test_df_prepare_to_join,
        how='inner',
        left_on='ZIPCODE',
        right_on='Zip Code'
    )
    m = folium.Map(location=[34.05, -118.25], zoom_start=9, tiles="cartodbpositron")
    folium.GeoJson(gdf).add_to(m)

    Choropleth(
        geo_data=gdf,
        data=gdf,
        columns=['ZIPCODE', 'Predicted Price'],
        key_on='feature.properties.ZIPCODE',
        fill_color='YlGnBu',  # Or 'BuPu', 'YlOrRd' etc.
        fill_opacity=0.7,
        line_opacity=0.2,
        legend_name='Predicted Price',
        highlight=True
    ).add_to(m)
    # For now, return success message or render a template
    return HTMLResponse(m._repr_html_())