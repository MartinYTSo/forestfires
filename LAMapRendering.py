import pydeck as pdk
import geopandas as gpd
import pandas as pd
import json
import streamlit as st
import base64

############### Wildifre Risk Prediction Class ######################

class PredictionRiskMap:
    def __init__(self, prediction_df: pd.DataFrame,geo_df: gpd.GeoDataFrame):
        self.gdf = geo_df.copy()
        self.pred_df = prediction_df.copy()
        self.cleaned_gdf = None

    def prepare_data(self):
        # Ensure ZIP Code column matches
        self.pred_df["Zip Code"] = self.pred_df["Zip Code"].astype(int)
        self.pred_df['predprice'] = self.pred_df['Predicted Price'].apply(lambda x: f"${x:,.0f}")
        self.pred_df.rename(columns={"Predicted Price":"prednum"},inplace=True)
        self.gdf["ZIPCODE"] = self.gdf["ZIPCODE"].astype(int)
        merged_gdf = self.gdf.merge(self.pred_df, how='left', left_on='ZIPCODE', right_on='Zip Code')
        self.cleaned_gdf=merged_gdf
        return self.cleaned_gdf #debugging

    def get_map_layer(self):
        if self.cleaned_gdf is None:
            raise RuntimeError("Run prepare_data() first.")
        geojson = json.loads(self.cleaned_gdf.to_json())
        return pdk.Layer(
            "GeoJsonLayer",
            data=geojson,
            pickable=True,
            auto_highlight=True,
            opacity=0.4,
            get_fill_color="""
                properties.prednum < 300000 ? [200, 200, 200, 200] :
                properties.prednum > 400000 ? [255, 165, 0, 180] :
                [0, 128, 0, 180]
            """,
            get_line_color=[255, 255, 255],
            line_width_min_pixels=1,
        )

    def render_combined_map(self, layers, center=[34.05, -118.25], zoom=9):
        view_state = pdk.ViewState(
            latitude=center[0],
            longitude=center[1],
            zoom=zoom,
            pitch=0
        )
        return pdk.Deck(
            layers=layers,
            initial_view_state=view_state,
            map_style="https://basemaps.cartocdn.com/gl/voyager-gl-style/style.json",
            tooltip={
                "html": "<b>ZIP:</b> {ZIPCODE}<br><b>Prediction:</b> {predprice}",
                "style": {"backgroundColor": "white", "color": "black"}
            }
        )





############### FireHazard Class######################
def classify_color(haz_code):
    if haz_code == 3:  # High
        return [204, 0, 0, 180]  # Deep red
    elif haz_code == 2:  # Moderate
        return [255, 140, 0, 180]  # Orange
    elif haz_code == 1:  # Low
        return [255, 255, 0, 160]  # Yellow
    else:
        return [200, 200, 200, 50]  # Unknown / fallback


class FireHazardMap:
    def __init__(self, firehazard_df: gpd.GeoDataFrame):
        self.df = firehazard_df.copy()
        self.df["fill_color"] = self.df["HAZ_CODE"].apply(classify_color)
        
    @st.cache_data(show_spinner=False)
    def get_geojson(self):
        return json.loads(self.df.to_json())


    def get_map(self, center=[34.05, -118.25], zoom=9):
        geojson = json.loads(self.df.to_json())

        layer = pdk.Layer(
            "GeoJsonLayer",
            data=geojson,
            pickable=False,
            opacity=0.3,
            get_fill_color="properties.fill_color",
            get_line_color=[0, 0, 0],
            line_width_min_pixels=1,
        )

        view_state = pdk.ViewState(
            latitude=center[0],
            longitude=center[1],
            zoom=zoom,
            pitch=0
        )

        deck = pdk.Deck(
            layers=[layer],
            initial_view_state=view_state,
            map_style="https://basemaps.cartocdn.com/gl/voyager-gl-style/style.json"
        )

        return deck
    
    def get_map_layer(self):
        geojson = json.loads(self.df.to_json())
        return pdk.Layer(
            "GeoJsonLayer",
            data=geojson,
            pickable=False,
            opacity=0.3,
            get_fill_color="properties.fill_color",
            get_line_color=[0, 0, 0],
            line_width_min_pixels=1,
        )   
############### Elevation ######################
class ElevationMap:
    def __init__(self, image_path="data/downsampled_elevation.png"):
        self.image_path = image_path

    @staticmethod
    @st.cache_resource(show_spinner=False)
    def _cached_layer(image_path):
        return pdk.Layer(
            "BitmapLayer",
            data=None,
            image=image_path,
            bounds=[-119.999861, 33.000139, -117.000139, 34.999861],
            opacity=0.2
        )

    def get_map_layer(self):
        return self._cached_layer(self.image_path)
    
    
##################Legends##############



@st.cache_data
def image_to_base64(image_path):
    with open(image_path, "rb") as f:
        data = f.read()
    return base64.b64encode(data).decode()

def get_legend_html(show_elev=False, show_fire=False):
    legend_html = ""
    if show_elev:
        legend_elev_base64 = image_to_base64("data/colorbar_legend_vertical.png")
        legend_html += f"""
            <div style="position: absolute; top: 24px; left: 15px; z-index: 999;">
                <img src="data:image/png;base64,{legend_elev_base64}" style="height: 400px;">
            </div>
        """
    if show_fire:
        legend_firehazards = image_to_base64("data/firehazard_legend.png")
        legend_html += f"""
            <div style="position: absolute; top: 10px; left: 40px; z-index: 999;">
                <img src="data:image/png;base64,{legend_firehazards}" style="height: 200px;">
            </div>
        """
    return legend_html

