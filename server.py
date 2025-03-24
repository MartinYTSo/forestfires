from fastapi import FastAPI
from fastapi.responses import HTMLResponse
import geopandas as gpd
import folium

app = FastAPI()
fire_hazard_path =  "data/Fire_Hazard_Severity_Zones.geojson"
fire_hazard_zones = gpd.read_file(fire_hazard_path)
m = folium.Map(location=[34.05, -118.25], zoom_start=9)




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
    folium.GeoJson(fire_hazard_zones, name= "Fire Hazard Zones", style_function=fire_hazard_style).add_to(m)
    folium.TileLayer(
    tiles="https://basemap.nationalmap.gov/arcgis/rest/services/USGSTopo/MapServer/tile/{z}/{y}/{x}",
    attr= "UGS National Map",
    name= "USGS Elevation (Contours)",
    overlay=False).add_to(m)
    folium.LayerControl().add_to(m)

    return HTMLResponse(m._repr_html_())