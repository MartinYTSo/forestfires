import streamlit as st
import requests
import numpy as np
import pandas as pd
import requests
from predictor import PropertyPricePredictor
from LAMapRendering import LACountyMap
import logging 
st.set_page_config(layout="wide",
                   initial_sidebar_state = "expanded")


### Functions ############
@st.cache_data #read data 
def read_data():
    data= pd.read_csv('data/LA Prices 2019-2023 and Census.csv')
    zip_codes_only=data['Zip Code'].to_list()
    return zip_codes_only 


@st.cache_resource
def load_predictor():
    return PropertyPricePredictor(
        model_path="lgbm_model_full.joblib",
        reference_data_path="data/LA Prices 2019-2023 and Census.csv"
    )


##########################################


LAData =read_data()

predictor = load_predictor()




st.title("CSE 6242 Predicting Real Estate Risks via Forest Fires")


st.sidebar.info(
    """
    - Web App URL: http://xxx.com
    \n
    - GitHub repository: <https://github.com/martinytso/forestfires>
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
                    st.success("Sent")

    with left_col:
        st.subheader("Wildfire Risk Map")
        with st.spinner("Loading predictions and generating map..."):
            pred_response = requests.get("http://localhost:8000/get_data")
            if pred_response.status_code == 200 and pred_response.json():
                pred_response_data = pred_response.json()
                result_df = pd.DataFrame([pred_response_data])
                prediction_output = predictor.predict(pred_response_data)
                # st.write("### 🔍 Submitted Input Data")
                # st.write(pd.DataFrame(prediction_output))
            # else:
                # st.warning("No data submitted yet or prediction server did not respond.")
                
            prediction_dataframe=pd.DataFrame(prediction_output) 
            map_obj= LACountyMap(prediction_dataframe,"data/LA_County_ZIP_Codes.geojson")
            map_obj.load_and_prepare_data()
            map_obj.generate_map()   
                    

# row2= st.container(border=True