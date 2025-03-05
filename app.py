import streamlit as st
import requests

st.title("Fire Hazard Map")

# Fetch the folium map from the FastAPI server
map_url = "http://localhost:8000/"
response = requests.get(map_url)

if response.status_code == 200:
    st.components.v1.html(response.text, height=600)
else:
    st.error("Failed to load the map. Ensure the FastAPI server is running.")
