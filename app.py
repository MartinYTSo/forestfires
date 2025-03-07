import streamlit as st
import requests
import numpy as np
import folium 
from streamlit_folium import st_folium

st.set_page_config(layout="wide",
                   initial_sidebar_state = "expanded")

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

row1= st.container(border=True)
with row1:
    st.write("This is inside the container")

    # Create a two-column layout inside the container
    row1_col1, row1_col2,row1_col3,row1_col4 = st.columns(4, border=True)

    with row1_col1:
        row1_col1.write("This is Column 1 inside the container")

    with row1_col2:
        row1_col2.write("This is Column 2 inside the container")

    with row1_col3:
        row1_col3.write("This is Column 3 inside the container")
    with row1_col4:
        row1_col4.write("This is Column 4 inside the container")

row2= st.container(border=True)

with row2:
    row2_col1, row2_col2,row2_col3 = st.columns(3, border=True)
    with row2_col1:
        row2_col1.write("This is Column 1 inside the container")

    with row2_col2:
        row2_col2.write("This is Column 2 inside the container")

    with row2_col3:
        row2_col3.write("This is Column 3 inside the container")


row3_row1_col1, row3_row1_col2 = st.columns([5, 1],border=True)


# Fetch the folium map from the FastAPI server
map_url = "https://forestfires-gy35.onrender.com"
response = requests.get(map_url)

##########################################


with row3_row1_col1:
    st.components.v1.html(response.text, width=1680,height=1080)
    # st_data=st_folium(m, width=1000, height=440)

with row3_row1_col2:
    st.write("Additional information or content can be placed here.")



