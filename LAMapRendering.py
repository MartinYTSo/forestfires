import json
import pydeck as pdk
import dask.dataframe as dd
import pandas as pd
import streamlit as st

class LACountyMap:
    def __init__(self, df: pd.DataFrame, geojson_path: str):
        # Convert to Dask DataFrame for faster parallel computation
        self.ddf = dd.from_pandas(df.copy(), npartitions=4)
        self.geojson_path = geojson_path
        self.geojson_data = None
        self.layer = None

    def load_and_prepare_data(self):
        with open(self.geojson_path, "r") as f:
            self.geojson_data = json.load(f)

        # Compute and convert Dask DataFrame to Pandas for mapping
        computed_df = self.ddf[['Zip Code', 'Predicted Price']].compute()
        prediction_dict = dict(zip(
            computed_df['Zip Code'].astype(int),
            computed_df['Predicted Price']
        ))

        for feature in self.geojson_data["features"]:
            zip_code = int(feature["properties"]["ZIPCODE"])
            feature["properties"]["prediction"] = prediction_dict.get(zip_code, 0)

    def generate_map(self, center=[34.05, -118.25], zoom=9, width=1000, height=600):
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

        view_state = pdk.ViewState(
            latitude=center[0],
            longitude=center[1],
            zoom=zoom,
            pitch=0
        )

        r = pdk.Deck(
            layers=[self.layer],
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

        st.pydeck_chart(r, use_container_width=False)
