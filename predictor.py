import pandas as pd
import numpy as np
from joblib import load
import pandas as pd
import numpy as np
import dask.dataframe as dd



class XGBoostPredictor:
    def __init__(self, submitted_data: dict, csv_path: str):
        self.df = pd.DataFrame(submitted_data)
        self.zip_code = int(self.df['Zip Code'].unique()[0])
        self.data_path = csv_path
        self.dask_df = dd.read_csv(self.data_path)

    def map_property_type(self):
        mapping = {
            "Single Family Residential": 3,
            "Low Density Residential": 2,
            "Condominium": 1
        }
        self.df["Property Use Type Encoded"] = self.df["Property Type"].map(mapping)
        self.df['Log_Improvement_Value'] = np.log1p(self.df['Improvement Value'])
        self.df['Log_Square_Footage'] = np.log1p(self.df['Square Footage'])
        self.df['Housing Cost % of Income']= self.df['Housing Cost (%)']

    def add_zip_median_price_and_coords(self):
        filtered = self.dask_df[self.dask_df['Zip Code'] == self.zip_code]
        median_value = filtered["Total Value (2023 Adjusted)"].median_approximate().compute()
        lat_lon = filtered[['Location Latitude', 'Location Longitude']].compute().iloc[0]

        self.df['Zip_Median_Price'] = median_value
        self.df['Location Latitude'] = int(np.ceil(lat_lon['Location Latitude']))
        self.df['Location Longitude'] = int(np.ceil(lat_lon['Location Longitude']))

    def add_price_bin(self):
        filtered = self.dask_df[self.dask_df['Zip Code'] == self.zip_code].compute()
        filtered["Price Bin"] = pd.qcut(
            filtered['Total Value (2023 Adjusted)'], q=20, labels=False, duplicates="drop"
        )
        average_bin = filtered["Price Bin"].mean()
        self.df['Price Bin'] = round(average_bin)
        
    def select_model_features(self):
        expected_features = [
            'Zip Code', 'Roll Year', 'Number of Buildings', 'Bathrooms', 'Number of Units',
            'Location Latitude', 'Location Longitude', 'Property Use Type Encoded',
            'Median Income', 'Housing Cost % of Income', 'Building Age',
            'Log_Improvement_Value', 'Log_Square_Footage', 'Price Bin', 'Zip_Median_Price'
        ]
        self.df = self.df[expected_features]
        
        
    def enforce_column_types(self):
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
            'Zip_Median_Price': 'float64'
        }
        for col, dtype in dtype_map.items():
            if col in self.df.columns:
                self.df[col] = self.df[col].astype(dtype)
        

    def process_all(self):
        self.map_property_type()
        self.add_zip_median_price_and_coords()
        self.add_price_bin()
        self.select_model_features()
        self.enforce_column_types() 
        return self.df
    
    def predict_price(self, base_model_path="model/xgb_base.joblib", high_model_path="model/xgb_high.joblib", cutoff=1_500_000):
        self.process_all()
        model_base = load(base_model_path)
        model_high = load(high_model_path)

        if self.df['Zip_Median_Price'].item() < cutoff:
            prediction = np.expm1(model_base.predict(self.df))
            self.model_used = "xgb_base"
            
        else:
            prediction = np.expm1(model_high.predict(self.df))
            self.model_used = "xgb_high"

        self.df['Predicted Price'] = prediction
        return self.df
