# predictor.py

import pandas as pd
import numpy as np
import joblib

class PropertyPricePredictor:
    def __init__(self, model_path: str, reference_data_path: str):
        self.model = joblib.load(model_path)
        self.test_data = pd.read_csv(reference_data_path)

    def map_property_type(self, df: pd.DataFrame, column_name="Property Type") -> pd.DataFrame:
        mapping = {
            "Single Family Residential": 3,
            "Low Density Residential": 2,
            "Condominium": 1
        }
        df["Property Type"] = df[column_name].map(mapping)
        df['Log_Improvement_Value'] = np.log1p(df['Improvement Value'])
        df['Log_Square_Footage'] = np.log1p(df['Square Footage'])
        return df

    def predict(self, data: dict) -> pd.DataFrame:
        # Flatten list values if needed
        for key, value in data.items():
            if isinstance(value, list) and len(value) == 1:
                data[key] = value[0]

        df = pd.DataFrame([data])
        df = self.map_property_type(df)

        sample = self.test_data[['Zip Code','Roll Year']]
        sample_df = sample.groupby("Zip Code").mean().reset_index()

        repeated_df = pd.concat([df] * len(sample_df), ignore_index=True)
        combined = pd.concat([sample_df, repeated_df], axis=1)

        combined = combined.rename(columns={
            "Housing Cost (%)": "Housing Cost % of Income",
            "Property Type": "Property Use Type Encoded"
        })

        feature_columns = [
            "Zip Code", "Roll Year", "Number of Buildings", "Bathrooms", "Number of Units",
            "Property Use Type Encoded", "Median Income", "Housing Cost % of Income",
            "Building Age", "Log_Improvement_Value", "Log_Square_Footage"
        ]

        for col in ["Zip Code", "Property Use Type Encoded"]:
            combined[col] = combined[col].astype("category")

        combined["Predicted Price"] = self.model.predict(combined[feature_columns])
        return combined
