import streamlit as st
import requests
import numpy as np
import folium 

st.set_page_config(layout="wide",
                   initial_sidebar_state = "expanded",
                       menu_items={'Get Help': 'https://www.extremelycoolapp.com/help',
        'Report a bug': "https://www.extremelycoolapp.com/bug",
        'About': "# This is a header. This is an *extremely* cool app!"
    })

st.title("CSE 6242 Predicting Real Estate Risks via Forest Fires")


st.sidebar.info(
    """
    - Web App URL: <https://streamlit.gishub.org>
    - GitHub repository: <https://github.com/martinytso/forestfires>
    """
)

st.sidebar.title("Contact")
st.sidebar.info(
    """
CSE 6242 Data and Visual Analytics  Team 12 |Ryan Cherry, Martin So | Lida Goldchteine| Katrina Silvorski
    """
)

with st.container(border=True) as container:
    st.write("This is inside the container")

    # Create a two-column layout inside the container
    col1, col2,col3,col4 = st.columns(4, border=True)

    with col1:
        col1.write("This is Column 1 inside the container")

    with col2:
        col2.write("This is Column 2 inside the container")

    with col3:
        col3.write("This is Column 3 inside the container")
    with col4:
        col4.write("This is Column 4 inside the container")

map= st.container(border=True)

with map:
    map.write("Test - This should be in the middle.")


row3_col1, row3_col2 = st.columns([6, 1],border=True)

# Fetch the folium map from the FastAPI server

with row3_col1:
    map_url = "https://forestfires-gy35.onrender.com"
    response = requests.get(map_url)

    if response.status_code == 200:
            
            st.components.v1.html(response.text, width=1000000,height=800)
    else:
        st.error("Failed to load the map. Ensure the FastAPI server is running.")
with row3_col2:
    st.write("Additional information or content can be placed here.")


