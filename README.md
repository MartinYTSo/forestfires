# app
On the folder, there are two Python files: `app.py` and `server.py`. 

`server.py` hosts all the backend information, for example, reading data or and performing ML/computational operations


In order to view it on the frontend, we have `app.py`. View the contents of `server.py` on the frontend `app.py` 

one must run the command 

`uvicorn server:app --host 0.0.0.0 --port 8000`. 

You wait for the application to start, and then you go on your browser and type in localhost:8000. 

Next, run in your terminal `streamlit run app.py.`








