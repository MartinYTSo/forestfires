import streamlit as st
import requests
import numpy as np
import folium 
from streamlit_folium import st_folium
import pandas as pd
import requests
from predictor import PropertyPricePredictor
from LAMapRendering import LACountyMap
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

row1= st.container(border=True)
with row1:
    st.write("This is inside the container")

    # Create a two-column layout inside the container
    row1_col1, row1_col2,row1_col3,row1_col4 = st.columns(4, border=True)

    with row1_col1:
        row1_col1.write("This is Column 1 inside the container")
        BuildingsParameter = st.slider("Number of Buildings", 1, 5, 3)
        BathroomsParameter = st.slider("Bathrooms", 1, 4, 2)
        SquareFootage= st.slider("Square Footage",1,9000,2)
        
    with row1_col2:
        row1_col2.write("This is Column 2 inside the container")
        
        NumberOfUnitsParameter	 = st.slider("No. of Units", 1, 4, 2)
        PropertyUseTypeParameter = st.radio(
        "Property Type",
        ["Single Family Residential", "Low Density Residential","Condominium"],
        index=0,
    )


    with row1_col3:
        row1_col3.write("This is Column 3 inside the container")
        
        MedianIncomeParameter= st.slider("Median Income",1,1000000,2)
        HousingCostPrameter=st.slider("Estimate (%) of Housing cost",1,100,1)
        
    with row1_col4:
        row1_col4.write("This is Column 4 inside the container")
        BuildingAgeParameter= st.slider("Building Age",1,100,2)
        ImprovementValueParameter= st.slider("Improvement Value",1,1000000,2)
        
        if st.button("Analyze"): ##saves input data 
            
            data = {
            "Number of Buildings": [BuildingsParameter],
            "Bathrooms": [BathroomsParameter],
            "Square Footage": [SquareFootage],
            "Number of Units": [NumberOfUnitsParameter],
            "Property Type": [PropertyUseTypeParameter],
            "Median Income": [MedianIncomeParameter],
            "Housing Cost (%)": [HousingCostPrameter],
            "Building Age": [BuildingAgeParameter],
            "Improvement Value": [ImprovementValueParameter]}
            response = requests.post("http://localhost:8000/submit_form/", json=data)
            if response.status_code == 200:
                st.success("Sent")

                # Call the prediction API
            

        
        



pred_response = requests.get("http://localhost:8000/get_data")
if pred_response.status_code == 200 and pred_response.json():
    pred_response_data = pred_response.json()
    result_df = pd.DataFrame([pred_response_data])
    prediction_output = predictor.predict(pred_response_data)
    prediction_dataframe=pd.DataFrame(prediction_output)
    st.write("### 🔍 Submitted Input Data")
    st.write(pd.DataFrame(prediction_output))
else:
    st.warning("No data submitted yet or prediction server did not respond.")
    
map_obj= LACountyMap(prediction_dataframe,"data/LA_County_ZIP_Codes.geojson")
map_obj.load_and_prepare_data()
       
        

row2= st.container(border=True)

with row2:
    row2_col1, row2_col2,row2_col3 = st.columns(3, border=True)
    with row2_col1:
        row2_col1.write("This is Column 1 inside the container")

    with row2_col2:
        row2_col2.write("This is Column 2 inside the container")

    with row2_col3:
        row2_col3.write("This is Column 3 inside the container")





# Fetch the folium map from the FastAPI server
# map_url = "http://localhost:8000/"
# response = requests.get(map_url)

##########################################

row3_row1_col1, row3_row1_col2 = st.columns([5, 1],border=True)

with row3_row1_col1:
    # st.markdown("<div style='height: 500px;'></div>", unsafe_allow_html=True)
    map_obj.generate_map()

with row3_row1_col2:
    st.write("Additional information or content can be placed here.")