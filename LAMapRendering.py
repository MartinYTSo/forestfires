import json
import pydeck as pdk
import dask.dataframe as dd
import pandas as pd
import streamlit as st
from PIL import Image
import numpy as np
import io
import base64
import matplotlib.pyplot as plt


@st.cache_data
def image_to_base64(image_path):
    with open(image_path, "rb") as f:
        data = f.read()
    return base64.b64encode(data).decode()


logo_base64 = image_to_base64("data/colorbar_legend_vertical.png")
logo_html = f"""
            <div style="position: absolute; top: 20px; left: 15px; z-index: 99;background: transparent;">
                <img src="data:image/png;base64,{logo_base64}" style="height: 400px;">
            </div>
        """


@st.cache_data
def build_geojson_with_predictions(geojson_path, zip_pred_dict):
    with open(geojson_path, "r") as f:
        geojson_data = json.load(f)

    for feature in geojson_data["features"]:
        zip_code = int(feature["properties"]["ZIPCODE"])
        feature["properties"]["prediction"] = zip_pred_dict.get(zip_code, 0)

    return geojson_data


class LACountyMap:
    def __init__(self, df: pd.DataFrame, elevdf:pd.DataFrame, geojson_path: str):
        # Convert to Dask DataFrame for faster parallel computation
        self.ddf = dd.from_pandas(df.copy(), npartitions=4)
        self.elevation_data = dd.from_pandas(elevdf.copy(), npartitions=4)
        self.geojson_path = geojson_path
        self.geojson_data = None
        self.layer = None
        self.scatter_layer = None
        self.bitmap_layer=None
    
    def load_and_prepare_data(self):

        # Compute and convert Dask DataFrame to Pandas for mapping
        computed_df = self.ddf[['Zip Code', 'Predicted Price']].compute()
        prediction_dict = dict(zip(
            computed_df['Zip Code'].astype(int),
            computed_df['Predicted Price']
        ))
        self.geojson_data = build_geojson_with_predictions(self.geojson_path, prediction_dict)


            


    def generate_map(self, center=[34.05, -118.25], zoom=9, width=1000, height=1030):
        if self.geojson_data is None:
            raise ValueError("GeoJSON not loaded. Call load_and_prepare_data() first.")
        
        
        self.layer = pdk.Layer(
            "GeoJsonLayer",
            self.geojson_data,
            pickable=True,
            auto_highlight=True,
            opacity=0.6,
            get_fill_color="""
                 properties.prediction < 13 ? [200, 200, 200, 180] :
                properties.prediction < 14 ? [255, 165, 0, 180] : 
                [0, 128, 0, 180]
            """,
            get_line_color=[255, 255, 255],
            line_width_min_pixels=1
        )
        show_elev_layer = st.checkbox("Show Elevation Layer", value=True)
        
        
        sample_data = pd.DataFrame({
            "lat": [34.0522, 34.0622, 34.0739, 34.0407],  # Downtown, Hollywood, Beverly Hills, USC
            "lon": [-118.2437, -118.3082, -118.4004, -118.2690],
            "size": [1000, 1500, 1200, 1300]
        })

        self.scatter_layer = pdk.Layer(
            "ScatterplotLayer",
            data=sample_data,
            get_position=['lon', 'lat'],
            get_radius='size',
            get_fill_color=[0, 0, 255, 160],
            pickable=True
        )
        
                    
        self.bitmap_layer = pdk.Layer(
            "BitmapLayer",
            data=None,
            image="data/downsampled_elevation.png",
            bounds=[-119.999861, 33.000139, -117.000139, 34.999861],
            opacity=0.2
        )    

        
        layers = [self.layer]
        if show_elev_layer:
            layers.append(self.bitmap_layer)
            st.markdown(logo_html, unsafe_allow_html=True) 
            

        view_state = pdk.ViewState(
            latitude=center[0],
            longitude=center[1],
            zoom=zoom,
            pitch=0
        )

        r = pdk.Deck(
            layers=layers,
            initial_view_state=view_state,
                tooltip={
                    "html": "<b>ZIP:</b> {ZIPCODE}<br><b>Prediction:</b> {prediction}",
                    "style": {
                        "backgroundColor": "white",
                        "color": "black",
                        "fontSize": "14px",
                        "padding": "8px",
                        "borderRadius": "4px"
                    }
                },
            map_style='mapbox://styles/mapbox/streets-v11'	
        )

        st.pydeck_chart(r, width=width, height=height)

