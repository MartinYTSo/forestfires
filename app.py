import streamlit as st
st.set_page_config(layout="wide", initial_sidebar_state="expanded")

import requests
import numpy as np
import pandas as pd
import geopandas as gpd
import streamlit.components.v1 as components
from LAMapRendering import PredictionRiskMap, FireHazardMap, ElevationMap
from io import BytesIO

from LAMapRendering import get_legend_html  
### Cached Data Loaders
@st.cache_data
def read_geojson_data(): #Get Zipcode Data for LA county  https://hub.arcgis.com/datasets/lacounty::la-county-zip-codes/about
    mapurl= requests.get("https://public.gis.lacounty.gov/public/rest/services/LACounty_Dynamic/Administrative_Boundaries/MapServer/5/query?outFields=*&where=1%3D1&f=geojson")
    gdf_zipcode = gpd.read_file(BytesIO(mapurl.content))
    return gdf_zipcode

@st.cache_data
def read_fire_hazard_data(): #Get Fire Hazard Data https://geohub.lacity.org/datasets/bf87f4b1e6954f4697006ff41420c083_0/explore?location=34.124500%2C-118.341207%2C10.46 
    urlresponse= requests.get("https://public.gis.lacounty.gov/public/rest/services/LACounty_Dynamic/Hazards/MapServer/2/query?where=1%3D1&outFields=*&f=geojson")
    gdf = gpd.read_file(BytesIO(urlresponse.content))
    return gdf

@st.cache_data(show_spinner=False)
def get_cleaned_geodata(pred_df, _geojson_gdf):
    map_obj = PredictionRiskMap(pred_df, _geojson_gdf)
    return map_obj.prepare_data()

# Load data
geodata = read_geojson_data()
firehazard_data = read_fire_hazard_data()

all_zipcodes= tuple(geodata['ZIPCODE'].astype(int).tolist())
# App title
st.title("CSE 6242 Predicting Real Estate Prices via Forest Fire Risk")

# Sidebar
st.sidebar.info("[GitHub Repository](https://github.com/martinytso/forestfires)")
st.sidebar.title("Made By")
st.sidebar.info("Team 12\nRyan Cherry, Martin So, Lida Goldchteine, Katrina Silvorski")

# Main layout
main_container = st.container()
with main_container:
    left_col, right_col = st.columns([5, 1])

    # === RIGHT PANEL: Parameters ===
    with right_col:
        st.subheader("Adjust Parameters")
        ZipCodeSelector = st.multiselect("Choose a zip code",all_zipcodes,90210)
        BuildingsParameter = st.slider("Number of Structures (i,e Garage, ADU)", 1, 5, 3) # aka Number_Of_Buildings
        BathroomsParameter = st.slider("Bathrooms", 1, 4, 3)
        SquareFootage = st.slider("Square Footage", 1, 9000, 4285)
        NumberOfUnitsParameter = st.selectbox("No. of Units", [1, 2, 3, 4, 5], index=1)
        PropertyUseTypeParameter = st.radio("Property Type",
                                            ["Single Family Residential", "Low Density Residential", "Condominium"],
                                            index=1)
        MedianIncomeParameter = st.slider("Median Income", 1, 1000000, 426447)
        HousingCostPrameter = st.slider("Estimate (%) of Housing cost", 1, 100, 47)
        BuildingAgeParameter = st.slider("Building Age", 1, 100, 67)
        ImprovementValueParameter = st.slider("Improvement Value", 1, 1000000, 477686)

        if st.button("Analyze"):
            all_data=[]
            for zip_code in ZipCodeSelector:
                entry = {
                    "Zip_Code": zip_code,
                    "Roll_Year": 2023,
                    "Number_of_Buildings": BuildingsParameter,
                    "Bathrooms": BathroomsParameter,
                    "Square_Footage": SquareFootage,
                    "Number_of_Units": NumberOfUnitsParameter,
                    "Property_Type": PropertyUseTypeParameter,
                    "Median_Income": MedianIncomeParameter,
                    "Housing_Cost_Percentage": HousingCostPrameter,
                    "Building_Age": BuildingAgeParameter,
                    "Improvement_Value": ImprovementValueParameter,
                }
                all_data.append(entry)
            with st.spinner("Analyzing..."):
                response = requests.post("http://localhost:8000/submit_form/", json=all_data)
                if response.status_code == 200:
                    pred_response = requests.get("http://localhost:8000/get_df_predictions")
                    # st.write(pred_response.json()) #debug only
                    if pred_response.status_code == 200:
                        st.session_state.prediction_data = pd.DataFrame(pred_response.json())
                        st.success("Prediction complete!")
                    else:
                        st.error("Failed to retrieve prediction data.")
                else:
                    st.error("Prediction failed.")

    # === LEFT PANEL: Map Display ===
    with left_col:
        st.subheader("Wildfire Risk Map")
        if st.button("Reset Map"):
            if "prediction_data" in st.session_state:
                del st.session_state["prediction_data"]
            st.rerun()


        # Layer toggles
        show_firehazard = st.checkbox("Overlay: Fire Hazard Zones", value=False)
        show_elevation = st.checkbox("Overlay: Elevation", value=False)

        with st.spinner("Rendering map..."):
            # Prepare data
            if 'prediction_data' in st.session_state:
                active_data = st.session_state.prediction_data
            else:
                active_data = pd.DataFrame({
                    "Zip Code": [int(z) for z in geodata["ZIPCODE"]],
                    "Roll Year": [2023.0] * len(geodata),
                    "Number of Buildings": [0] * len(geodata),
                    "Bathrooms": [0] * len(geodata),
                    "Square Footage": [0] * len(geodata),
                    "Number of Units": [0] * len(geodata),
                    "Property Type": ["Low Density Residential"] * len(geodata),
                    "Median Income": [0] * len(geodata),
                    "Housing Cost (%)": [0] * len(geodata),
                    "Building Age": [0] * len(geodata),
                    "Improvement Value": [0] * len(geodata),
                    "Log_Improvement_Value": [0.0] * len(geodata),
                    "Log_Square_Footage": [0.0] * len(geodata),
                    "Predicted Price": [0.0] * len(geodata),
                    "Fire Risk Score": [5] * len(geodata), #random number to make it white
                })

            cleaned_data = get_cleaned_geodata(active_data, geodata)

            # Build base map
            pred_map = PredictionRiskMap(active_data, geodata)
            pred_map.cleaned_gdf = cleaned_data
            layers = [pred_map.get_map_layer()]

            # Add overlays
            if show_firehazard:
                fire_map = FireHazardMap(firehazard_data)
                layers.append(fire_map.get_map_layer())

            if show_elevation:
                elev_map = ElevationMap()
                layers.append(elev_map.get_map_layer())

            # Render as HTML and embed
            html_str = pred_map.render_combined_map(layers).to_html(as_string=True)
            
            legend_html = get_legend_html(show_elevation, show_firehazard)
            html_with_legend = html_str.replace(
                "<body>", f"<body>{legend_html}"
)
            components.html(html_with_legend, height=650)

            
        
            
