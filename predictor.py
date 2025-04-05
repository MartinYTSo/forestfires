import pandas as pd
import numpy as np
from joblib import load
import dask.dataframe as dd
from typing import List, Dict

class XGBoostPredictor:
    expected_features = [
        'Zip Code', 'Roll Year', 'Number of Buildings', 'Bathrooms', 'Number of Units',
        'Location Latitude', 'Location Longitude', 'Property Use Type Encoded',
        'Median Income', 'Housing Cost % of Income', 'Building Age',
        'Log_Improvement_Value', 'Log_Square_Footage', 'Price Bin', 'Zip_Median_Price',
        'Fire Risk Score'
    ]

    rename_map = {
        "Zip_Code": "Zip Code",
        "Roll_Year": "Roll Year",
        "Number_of_Buildings": "Number of Buildings",
        "Bathrooms": "Bathrooms",
        "Square_Footage": "Square Footage",
        "Number_of_Units": "Number of Units",
        "Property_Type": "Property Type",
        "Median_Income": "Median Income",
        "Housing_Cost_Percentage": "Housing Cost (%)",
        "Building_Age": "Building Age",
        "Improvement_Value": "Improvement Value"
    }

    dtype_map = {
        'Zip Code': 'category',
        'Roll Year': 'category',
        'Number of Buildings': 'int64',
        'Bathrooms': 'float64',
        'Number of Units': 'int64',
        'Location Latitude': 'float64',
        'Location Longitude': 'float64',
        'Property Use Type Encoded': 'int64',
        'Median Income': 'int64',
        'Housing Cost % of Income': 'float64',
        'Building Age': 'int64',
        'Log_Improvement_Value': 'float64',
        'Log_Square_Footage': 'float64',
        'Price Bin': 'int64',
        'Zip_Median_Price': 'float64',
        'Fire Risk Score': 'int64'
    }

    fire_risk_map = {
        'No Fire': 0,
        'Low': 1,
        'Mid': 2,
        'Medium': 2,
        'High': 3
    }

    def __init__(self, submitted_data: List[Dict], csv_path: str, csv_path_firerisk: str):
        self.df = pd.DataFrame(submitted_data)
        self.df.rename(columns=self.rename_map, inplace=True)
        self.data_path = csv_path
        self.csv_path_firerisk = csv_path_firerisk
        self.dask_df = dd.read_csv(self.data_path)
        self.dask_fr_df = pd.read_csv(self.csv_path_firerisk)

    def map_property_type(self):
        mapping = {
            "Single Family Residential": 3,
            "Low Density Residential": 2,
            "Condominium": 1
        }
        self.df["Property Use Type Encoded"] = self.df["Property Type"].map(mapping)
        self.df['Log_Improvement_Value'] = np.log1p(self.df['Improvement Value'])
        self.df['Log_Square_Footage'] = np.log1p(self.df['Square Footage'])
        self.df['Housing Cost % of Income'] = self.df['Housing Cost (%)']

    def add_zip_median_price_and_coords(self):
        zip_to_median = {}
        zip_to_coords = {}

        for zip_code in self.df['Zip Code'].unique():
            filtered = self.dask_df[self.dask_df['Zip Code'] == zip_code]
            median_val = filtered["Total Value (2023 Adjusted)"].median_approximate().compute()
            lat_lon = filtered[['Location Latitude', 'Location Longitude']].compute().iloc[0]
            zip_to_median[zip_code] = median_val
            zip_to_coords[zip_code] = (lat_lon['Location Latitude'], lat_lon['Location Longitude'])

        self.df['Zip_Median_Price'] = self.df['Zip Code'].map(zip_to_median)
        self.df['Location Latitude'] = self.df['Zip Code'].map(lambda z: zip_to_coords[z][0])
        self.df['Location Longitude'] = self.df['Zip Code'].map(lambda z: zip_to_coords[z][1])

    def add_price_bin(self):
        zip_bins = {}
        for zip_code in self.df['Zip Code'].unique():
            filtered = self.dask_df[self.dask_df['Zip Code'] == zip_code].compute()
            filtered["Price Bin"] = pd.qcut(
                filtered['Total Value (2023 Adjusted)'], q=20, labels=False, duplicates="drop"
            )
            avg_bin = filtered["Price Bin"].mean()
            zip_bins[zip_code] = round(avg_bin)
        self.df['Price Bin'] = self.df['Zip Code'].map(zip_bins)

    def add_fire_risk_score(self):
        merged = self.df.merge(
            self.dask_fr_df, how='inner', left_on="Zip Code", right_on="Zip_Code"
        )
        merged.rename(columns={
            'Average_Elevation_m': 'Elevation',
            'Class_Label': 'Fire Class Label'
        }, inplace=True)
        merged['Fire Risk Score'] = merged['Fire Class Label'].map(self.fire_risk_map)
        self.df = merged

    def enforce_column_types(self):
        for col, dtype in self.dtype_map.items():
            if col in self.df.columns:
                self.df[col] = self.df[col].astype(dtype)

    def process_all(self):
        self.map_property_type()
        self.add_zip_median_price_and_coords()
        self.add_price_bin()
        self.add_fire_risk_score()
        self.df = self.df[self.expected_features]
        self.enforce_column_types()
        return self.df
            
    
    def predict_price(self, base_model_path="model/model_xgb_base_fire.joblib", high_model_path="model/model_xgb_high_fire.joblib", cutoff=1_500_000):
        df_to_pass= self.process_all() #returns a dataframe 
        model_base = load(base_model_path)
        model_high = load(high_model_path)
        df_over_thresh= df_to_pass[df_to_pass['Zip_Median_Price']>cutoff]
        df_under_thresh=df_to_pass[df_to_pass['Zip_Median_Price']<cutoff]
        df_under_thresh['Predicted Price']= np.expm1(model_base.predict(df_under_thresh))
        df_over_thresh['Predicted Price']= np.expm1(model_high.predict(df_over_thresh))
        df_final= pd.concat([df_under_thresh, df_over_thresh], ignore_index=True)
        self.df=df_final
        return self.df