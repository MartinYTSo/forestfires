
import streamlit as st
st.set_page_config(layout="wide",initial_sidebar_state = "expanded")
import requests
import numpy as np
import pandas as pd
import requests
from predictor import XGBoostPredictor
from LAMapRendering import LACountyMap
import logging 
import geopandas as gpd 
import dask.dataframe as dd



### Functions ############

@st.cache_data #read data 
def read_geojson_data():
    geodata= gpd.read_file('data/LA_County_ZIP_Codes.geojson')
    return geodata 


@st.cache_data #read data 
def read_fire_hazard_data():
    geodata= gpd.read_file('data/fire_hazard_zones.geojson')
    return geodata 


@st.cache_data(show_spinner=False)
def get_cleaned_geodata(pred_df, _geojson_gdf,_fd):
    map_obj = LACountyMap(pred_df, _geojson_gdf,_fd)
    return map_obj.load_and_prepare_data()



##########################################

geodata=read_geojson_data()

firehazard_data=read_fire_hazard_data()

st.title("CSE 6242 Predicting Real Estate Risks via Forest Fires")


st.sidebar.info(
    """
    - GitHub repository\n
    <https://github.com/martinytso/forestfires>
    """
)


st.sidebar.title("Made By")
st.sidebar.info(
    """
  Team 12\n 
  Ryan Cherry, Martin So, Lida Goldchteine, Katrina Silvorski
    """
    
)
data={}

# Full-width container
main_container = st.container()

with main_container:
    # Two main columns: map on left, sliders on right
    left_col, right_col = st.columns([5, 1])  # Adjust ratio if needed

    with right_col:
        st.subheader("Adjust Parameters")
        ZipCodeSelector = st.selectbox("Choose a zip code",
                                       (90047,90011))
        BuildingsParameter = st.slider("Number of Buildings", 1, 5, 3)
        BathroomsParameter = st.slider("Bathrooms", 1, 4, 3)
        SquareFootage = st.slider("Square Footage", 1, 9000, 4285)

        NumberOfUnitsParameter = st.selectbox("No. of Units", options=[1, 2, 3, 4, 5], index=1)
        PropertyUseTypeParameter = st.radio(
            "Property Type",
            ["Single Family Residential", "Low Density Residential", "Condominium"],
            index=1,
        )

        MedianIncomeParameter = st.slider("Median Income", 1, 1000000, 426447)
        HousingCostPrameter = st.slider("Estimate (%) of Housing cost", 1, 100, 47)

        BuildingAgeParameter = st.slider("Building Age", 1, 100, 67)
        ImprovementValueParameter = st.slider("Improvement Value", 1, 1000000, 477686)

        if st.button("Analyze"):
            data = {
                "Zip Code":[ZipCodeSelector],
                "Roll Year":[2023],
                "Number of Buildings": [BuildingsParameter],
                "Bathrooms": [BathroomsParameter],
                "Square Footage": [SquareFootage],
                "Number of Units": [NumberOfUnitsParameter],
                "Property Type": [PropertyUseTypeParameter],
                "Median Income": [MedianIncomeParameter],
                "Housing Cost (%)": [HousingCostPrameter],
                "Building Age": [BuildingAgeParameter],
                "Improvement Value": [ImprovementValueParameter],
            }

            with st.spinner("Analyzing:"):
                response = requests.post("http://localhost:8000/submit_form/", json=data)
                if response.status_code == 200:
                    pred_response = requests.get("http://localhost:8000/get_df_predictions")
                    if pred_response.status_code==200:
                        st.session_state.prediction_data= pd.DataFrame(pred_response.json())
                    # st.session_state.prediction_data = pd.DataFrame([response.json()])
                        st.success("Prediction complete!")
                else:

                    st.error("Prediction Failed")
####delete soon
    with left_col:
        st.subheader("Wildfire Risk Map")
        with st.spinner("Rendering map..."):

            # Define default data regardless of condition
            default_data = pd.DataFrame({
                "Zip Code": [int(z) for z in geodata["ZIPCODE"]],
                "Roll Year": [2021.0] * len(geodata),
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
            })

            # Use predicted data if available, else default
            if 'prediction_data' in st.session_state:
                with st.spinner("Rendering map..."):
                    cleaned_data = get_cleaned_geodata(st.session_state.prediction_data, geodata,firehazard_data)
                    active_data = st.session_state.prediction_data
            else:
                with st.spinner("Loading default map..."):
                    cleaned_data = get_cleaned_geodata(default_data, geodata,firehazard_data)
                active_data = default_data

            # Render map using cleaned data (cached)
            map_obj = LACountyMap(active_data, geodata,firehazard_data)
            map_obj.geodata_cleaned = cleaned_data
            map_obj.generate_map()
