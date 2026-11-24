# StockFlow — SaaS Inventory Management MVP

A full-stack inventory management app built with FastAPI, SQLite, SQLAlchemy, React and Vite.

## Features
- Organization signup and email/password login
- Argon2 password hashing and JWT authentication
- Organization-scoped product data (tenant isolation)
- Product create, list, detail, update and delete
- SKU uniqueness within each organization
- Search by product name or SKU
- Stock increase/decrease controls
- Dashboard metrics: products, units, low-stock count, stock cost value
- Low-stock detection with per-product override and organization default
- Workspace settings for default low-stock threshold
- Responsive SaaS-style interface

## Requirements
- Python 3.10+
- Node.js 18+

## Run on Windows (two terminals)

### Terminal 1 — Backend
```cmd
cd STOCKFLOW\backend
python -m venv venv
venv\Scripts\activate
python -m pip install --upgrade pip
pip install -r requirements.txt
python -m uvicorn app.main:app --reload
```
API: http://127.0.0.1:8000  
Swagger docs: http://127.0.0.1:8000/docs

### Terminal 2 — Frontend
```cmd
cd STOCKFLOW\frontend
npm install
npm run dev
```
Frontend: http://localhost:5173

## Demo
1. Open the frontend and create an account with an organization name.
2. Add products with SKU, quantity and prices.
3. Try setting a low quantity or threshold to trigger a low-stock alert.
4. Use the + / − controls to adjust stock.
5. Change the default threshold in Settings.

## Notes
- SQLite file `backend/stockflow.db` is created automatically.
- Local development uses a fallback JWT secret. Set a strong `SECRET_KEY` environment variable for deployment.
- This is an MVP, not a production-hardened service. For production, add migrations, rate limiting, HTTPS, secure secret management, backups, audit history and stronger operational monitoring.
