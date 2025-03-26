import streamlit as st
import requests
import numpy as np
import folium 
from streamlit_folium import st_folium
import pandas as pd

st.set_page_config(layout="wide",
                   initial_sidebar_state = "expanded")


### Functions ############
@st.cache_data #read data 
def read_data():
    data= pd.read_csv('data/LA Prices 2019-2023 and Census.csv')
    zip_codes_only=data['Zip Code'].to_list()
    return zip_codes_only 


def map_property_type(df):
    mapping = {
        "Single Family Residential": 3,
        "Low Density Residential": 2,
        "Condominium": 1
    }
    df["Property TypeTest"] = df["Property Type"].map(mapping)
    return df

##########################################


LAData =read_data()



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
        SquareFootage= st.slider("Square Footage",1,1000,2)
        
    with row1_col2:
        row1_col2.write("This is Column 2 inside the container")
        
        NumberOfUnitsParameter	 = st.slider("No. of Units", 1, 4, 2)
        PropertyUseTypeParameter = st.radio(
        "Property Type",
        ["Single Family Residential", "Low Density Residential","Condominium"],
        index=None,
    )


    with row1_col3:
        row1_col3.write("This is Column 3 inside the container")
        
        MedianIncomeParameter= st.slider("Median Income",1,1000,2)
        HousingCostPrameter=st.slider("Estimate (%) of Housing cost",1,100,1)
        
    with row1_col4:
        row1_col4.write("This is Column 4 inside the container")
        BuildingAgeParameter= st.slider("Age of Building",1,1000,2)
        ImprovementValueParameter= st.slider("Improvement Value",1,1000,2)
        if st.button("Save to DataFrame"): ##saves input data 
            
            data = {
            "Number of Buildings": [BuildingsParameter],
            "Bathrooms": [BathroomsParameter],
            "Square Footage": [SquareFootage],
            "No. of Units": [NumberOfUnitsParameter],
            "Property Type": [PropertyUseTypeParameter],
            "Median Income": [MedianIncomeParameter],
            "Housing Cost (%)": [HousingCostPrameter],
            "Age of Building": [BuildingAgeParameter],
            "Improvement Value": [ImprovementValueParameter]}
            
            df = pd.DataFrame(data)
            if data:
                
                df = pd.DataFrame(data)
                property_type_mapping = {
                    "Single Family Residential": 3,
                    "Low Density Residential": 2,
                    "Condominium": 1
                }
                df["Property Type"] = df["Property Type"].map(property_type_mapping)
                
st.write("Saved Data:")
st.dataframe(df)

        
        



# st.dataframe(LAData.head()) #debugging to load dataframe 

        
    

        
        
        
row3_row1_col1, row3_row1_col2 = st.columns([5, 1],border=True)
        
            
        
        

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
map_url = "http://localhost:8000/"
response = requests.get(map_url)

##########################################


with row3_row1_col1:
    st.components.v1.html(response.text, width=1680,height=1080)
    # st_data=st_folium(m, width=1000, height=440)

with row3_row1_col2:
    st.write("Additional information or content can be placed here.")



