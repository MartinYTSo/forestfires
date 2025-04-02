# forestfires
Forest Fire Project For Data and Visual Analytics CSE 6242
## Step 1 
Make a `data` folder in your root directory. [Download all the items from this link](https://www.dropbox.com/scl/fo/e9f78zxipm0zev27khcs6/ABtPqI4RZWsonqLRZZATccY?rlkey=ut4opxix9gbhq6uxs5oxykohl&st=b98wbvig&dl=0 ) and move it in your `data` folder 

## Step 2 

Create an `.venv` with the latest version on python 

## Step 3 

run `pip install -r requirements.txt` 

## Step 4
open a terminal and run `uvicorn server:app --host localhost --port 8000`

## Step 5
Open another terminal window and run `streamlit run app.py`. It will automatically redirect you to the app


## Important!

Make sure your files structure is like this



## 📁 Project Structure

```
APP/
├── __pycache__/
├── .venv/

├── data/
│   ├── colorbar_legend_vertical.png
│   ├── downsampled_elevation.png
│   ├── elevation_data_downsampled.csv
│   ├── LA Prices 2019–2023 and Census.csv
│   ├── LA_County_ZIP_Codes.geojson
│   └── firehazard_legend.png
|   └──fire_hazard_zones.geojson

├── model/
│   ├── xgb_base.joblib
│   ├── xgb_high.joblib

├── app.py
├── LAMapRendering.py
├── predictor.py
├── server.py
└── requirements.txt
```



