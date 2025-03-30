# %% [markdown]
# ### PreProcess Data
from fastapi import FastAPI
from fastapi.responses import HTMLResponse
import geopandas as gpd
import folium
import numpy as np 
import pandas as pd 
from fastapi import Request
from fastapi.middleware.cors import CORSMiddleware
app = FastAPI()

import requests
import pandas as pd
import numpy as np 
# Fetch the data from FastAPI
import joblib
model = joblib.load("lgbm_model_full.joblib")

test_data= pd.read_csv("data/LA Prices 2019-2023 and Census.csv")


response = requests.get("http://localhost:8000/get_data/")
if response.status_code == 200:
    data = response.json()
    dataframe = pd.DataFrame(data)
else:
    print("Failed to retrieve data")



def map_property_type(df, column_name="Property Type"):
    mapping = {
        "Single Family Residential": 3,
        "Low Density Residential": 2,
        "Condominium": 1
    }
    df["Property Type"] = df[column_name].map(mapping)
    df['Log_Improvement_Value'] = np.log1p(df['Improvement Value'])
    df['Log_Square_Footage'] = np.log1p(df['Square Footage'])

    return df


dataframe=map_property_type(dataframe)


sample = test_data[['Zip Code','Roll Year']]

sample_df=sample.groupby("Zip Code").mean().reset_index()



repeated_df = pd.concat([dataframe]*len(sample_df), ignore_index=True)

# Concatenate along columns
combined = pd.concat([sample_df, repeated_df], axis=1)
 


dataframe=combined.rename(columns={"Housing Cost (%)": "Housing Cost % of Income","Property Type": "Property Use Type Encoded"})





feature_columns = [
    "Zip Code",
    "Roll Year",
    "Number of Buildings",
    "Bathrooms",
    "Number of Units",
    "Property Use Type Encoded",
    "Median Income",
    "Housing Cost % of Income",
    "Building Age",
    "Log_Improvement_Value",
    "Log_Square_Footage"
]


categorical_cols = ["Zip Code", "Property Use Type Encoded"]
for col in categorical_cols:
    dataframe[col] = dataframe[col].astype("category")

predictions = model.predict(dataframe[feature_columns]) #predicts on dataframe 

# Display results
dataframe["Predicted Price"] = predictions
# print(test_data[["Zip Code", "Predicted Price"]])



@app.get("/LGBMPredict")
def return_dataframe():
    return dataframe.to_json(orient='records')




# %%
