# CSE 6242 Predicting Real Estate Prices via Forest Fire Risk
Class Project for Georgia Tech's Data and Visual Analytics CSE 6242

Authors:  Lidia Goldchteine, Katrina Slivorski, Ryan Cherry, Martin Yip Toll So

# Installation
There are 2 ways to install the repo.
 - 1.The fast, one click installation for Windows and MacOS
 - 2.The manual installation (which requires a few command lines)

Use the fast installation if you do not care about packages installing to your root python directory.

Use the manual isntallation if you prefer to create a virtual environment `.venv` and installing the app there


# One Click Installation
## Step 1 
Clone this repository to your local folder. [Download all the items from this link](https://www.dropbox.com/scl/fo/e9f78zxipm0zev27khcs6/ABtPqI4RZWsonqLRZZATccY?rlkey=ut4opxix9gbhq6uxs5oxykohl&st=b98wbvig&dl=0 ) and move it into the `data` folder in the repo **ensure you do not change the file names**:  

![image](https://github.com/user-attachments/assets/07a5771c-ad2e-440b-89b9-5c4974797481)


## Step 2 
Open the root directory and double click  `start.bat` (for Windows Users) or `start.sh` for MacOS users

You will know everything works fine if you have 2 command prompt windows pop up. One for the backend FASTAPI server, and the other for the frontend streamlit server
![image](https://github.com/user-attachments/assets/07681a9b-57a1-4948-96b9-c9556ff363b1)



# Manual Installation 
## Step 1 
Clone this repository to your local folder. [Download all the items from this link](https://www.dropbox.com/scl/fo/e9f78zxipm0zev27khcs6/ABtPqI4RZWsonqLRZZATccY?rlkey=ut4opxix9gbhq6uxs5oxykohl&st=b98wbvig&dl=0 ) and move it into the `data` folder in the repo **ensure you do not change the file names**:  

![image](https://github.com/user-attachments/assets/65166b7a-e764-4f9f-949a-69e6f3a287f2)


## Step 2 

Create an `.venv` with the latest version on python. If you are using VSCode the steps are:
1. `Ctrl+Shift+P`
2. `Python: Create Environment` -> Select your envrionment
3. Wait till VSCode finishes setting up the environment
4. Type `.venv/Scripts/activate` and enter in your terminal. This will activate the virtual environment for your packages to be installed there. Deleting the virtual environment will delete all packages associated with the app seamlessly.



## Step 3 
Ensure your virtual envrionment activated. You will know if the terminal has a `(.venv)` prefix upon running Step 2 

![image](https://github.com/user-attachments/assets/afeb99f2-c2b4-4ebd-9fe7-27e7239683b9)

Now you can enter `pip install -r requirements.txt`. This will ensure all packages associated with this app will be installed to your virtual environment

## Step 4
Open a terminal and run `uvicorn server:app --host localhost --port 8000`

## Step 5
Open another terminal window and run `streamlit run app.py`. It will automatically redirect you to the app


## Important!

Make sure your files structure is like this


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

## How to Shut Down App 

Streamlit will shut down the app if you close the terminal.

To shut down the backend server, click in your terminal where the FastAPI server is running and press `Ctrl+C`


## Uninstallation 

If you were using the one click installation, run 

`pip uninstall -r requirements.txt -y` (make sure you run it in the root folder!)

If you were using the manual installation, simply delete everything in the root folder.



