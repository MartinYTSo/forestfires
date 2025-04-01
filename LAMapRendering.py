import json
import pydeck as pdk
import dask.dataframe as dd
import pandas as pd
import streamlit as st
from PIL import Image
import numpy as np
from lightgbm import LGBMRegressor
import base64
import geopandas as gpd

@st.cache_data
def image_to_base64(image_path):
    with open(image_path, "rb") as f:
        data = f.read()
    return base64.b64encode(data).decode()


legend_elev_base64 = image_to_base64("data/colorbar_legend_vertical.png")
legend_firehazards=image_to_base64("data/firehazard_legend.png")


legend_elev_html = f"""
            <div style="position: absolute; top: 24px; left: 15px; z-index: 99;background: transparent;">
                <img src="data:image/png;base64,{legend_elev_base64}" style="height: 400px;">
            </div>
        """
legend_firehazards_html = f"""
            <div style="position: absolute; top: 10px; left: 20px; z-index: 99;background: transparent;">
                <img src="data:image/png;base64,{legend_firehazards}" style="height: 200px;">
            </div>
        """
            
        
# Define it outside the class
def classify_color(haz_class):
    if haz_class == 3:
        return [255, 255, 200, 180]
    elif haz_class == 2:
        return [255, 165, 220, 180]
    elif haz_class == 1:
        return [255, 140, 250, 180]
    else:
        return [0, 128, 0, 180]




class LACountyMap:
    def __init__(self, df: pd.DataFrame, gdf: gpd.GeoDataFrame, firehazard_df: gpd.GeoDataFrame):
        self.ddf = dd.from_pandas(df.copy(), npartitions=4)
        self.geojson_data = gdf.copy()
        self.geodata_cleaned = None
        self.layer = None
        self.scatter_layer = None
        self.bitmap_layer = None
        self.firehazard_data = firehazard_df.copy()

        # Just apply it here
        self.firehazard_data["fill_color"] = self.firehazard_data["HAZ_CODE"].apply(classify_color)
        # self.firehazard_data["fill_color"] = self.firehazard_data["fill_color"].apply(lambda x: list(x))  # Make sure it's JSON serializable

    
    def load_and_prepare_data(self):

        # Compute and convert Dask DataFrame to Pandas for mapping
        computed_df = self.ddf[['Zip Code', 'Predicted Price']].compute()
        self.geojson_data['ZIPCODE']=self.geojson_data['ZIPCODE'].astype(int)
        merged_gdf = self.geojson_data.merge(computed_df, how='left', left_on='ZIPCODE', right_on='Zip Code')
        merged_gdf['Predicted Price']= merged_gdf['Predicted Price'].fillna(0)
        merged_gdf.rename(columns={"Predicted Price":'prediction'},inplace=True)
        self.geodata_cleaned= merged_gdf
        return self.geodata_cleaned

            


    def generate_map(self ,center=[34.05, -118.25], zoom=9, width=1000, height=1030):
        if self.geodata_cleaned is None:
            raise ValueError("GeoJSON not loaded. Call load_and_prepare_data() first.")
        geojson_data = json.loads(self.geodata_cleaned.to_json())
        fh_data= json.loads(self.firehazard_data.to_json())
        
        col1, col2 = st.columns(2)

        with col1:
            show_elevation = st.checkbox("Show Elevation Layer", value=False, key="show_elevation_checkbox")

        with col2:
            show_firehazard = st.checkbox("Firehazard Layer", value=False, key="show_firehazard_checkbox")

        
        self.layer = pdk.Layer(
            "GeoJsonLayer",
            geojson_data,
            pickable=True,
            auto_highlight=True,
            opacity=0.2,
            get_fill_color="""
                properties.prediction < 13 ? [200, 200, 200, 180] :
                properties.prediction < 14 ? [255, 165, 0, 180] : 
                [0, 128, 0, 180]
            """,
            get_line_color=[255, 255, 255],
            line_width_min_pixels=1
        )
        
        
        self.firehazard_layer = pdk.Layer(
            "GeoJsonLayer",
            fh_data,
            pickable=True,
            auto_highlight=True,
            opacity=0.4,
            get_fill_color="""
            
            properties.HAZ_CODE ==1? [255, 255, 0]:
            properties.HAZ_CODE ==2? [255, 165, 0]:
            properties.HAZ_CODE ==3? [255, 0, 0]:
            [0,128,0,180]
            """,
            get_line_color=[255, 255, 255],
            line_width_min_pixels=1
        )
        
                    
        self.bitmap_layer = pdk.Layer(
            "BitmapLayer",
            data=None,
            image="data/downsampled_elevation.png",
            bounds=[-119.999861, 33.000139, -117.000139, 34.999861],
            opacity=0.2
        )    

        
        layers = [self.layer]
        if show_elevation:
            layers.append(self.bitmap_layer)
            st.markdown(legend_elev_html, unsafe_allow_html=True) 
            
        if show_firehazard:
            layers.append(self.firehazard_layer)
            st.markdown(legend_firehazards_html, unsafe_allow_html=True) 
        layers.append(self.layer)
            

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
            map_style='mapbox://styles/mapbox/streets-v10'	
        )

        st.pydeck_chart(r, width=width, height=height)

