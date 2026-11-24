# StockFlow Backend

## Setup (Windows CMD)
```cmd
cd backend
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
python -m uvicorn app.main:app --reload
```
Open http://127.0.0.1:8000/docs

The SQLite database `stockflow.db` is created automatically in the backend folder.
For local development the API uses a development SECRET_KEY. Set a strong `SECRET_KEY`
environment variable before any deployment.
