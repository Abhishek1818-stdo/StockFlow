from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from sqlalchemy import or_, func
from .database import Base, engine, get_db
from .models import User, Organization, Product
from .schemas import SignupIn, LoginIn, TokenOut, ProductIn, SettingsIn
from .security import hash_password, verify_password, create_token, current_user

Base.metadata.create_all(bind=engine)
app = FastAPI(title="StockFlow API", version="1.0.0", description="Multi-tenant SaaS inventory management")

allow_origins=[
    "http://localhost:5173",
    "https://YOUR-FRONTEND.vercel.app"
]
@app.get("/")
def root():
    return {"message": "Welcome to StockFlow API", "status": "running"}

@app.get("/api/health")
def health():
    return {"status": "healthy"}

@app.post("/api/auth/signup", status_code=201)
def signup(data: SignupIn, db: Session = Depends(get_db)):
    if db.query(User).filter(func.lower(User.email) == data.email.lower()).first():
        raise HTTPException(409, "Email is already registered")
    org = Organization(name=data.organization_name.strip())
    db.add(org)
    db.flush()
    user = User(email=data.email.lower(), hashed_password=hash_password(data.password), organization_id=org.id)
    db.add(user)
    db.commit()
    return {"message": "Account created successfully"}

@app.post("/api/auth/login", response_model=TokenOut)
def login(data: LoginIn, db: Session = Depends(get_db)):
    user = db.query(User).filter(func.lower(User.email) == data.email.lower()).first()
    if not user or not verify_password(data.password, user.hashed_password):
        raise HTTPException(401, "Incorrect email or password")
    return {"access_token": create_token(user), "token_type": "bearer"}

@app.get("/api/auth/me")
def me(user: User = Depends(current_user), db: Session = Depends(get_db)):
    org = db.query(Organization).filter(Organization.id == user.organization_id).first()
    return {"id": user.id, "email": user.email, "organization_id": user.organization_id,
            "organization_name": org.name if org else "", "default_low_stock_threshold": org.default_low_stock_threshold if org else 5}

def product_dict(p: Product):
    return {"id": p.id, "organization_id": p.organization_id, "name": p.name, "sku": p.sku,
            "description": p.description, "quantity": p.quantity, "cost_price": p.cost_price,
            "selling_price": p.selling_price, "low_stock_threshold": p.low_stock_threshold,
            "created_at": p.created_at.isoformat(), "updated_at": p.updated_at.isoformat()}

@app.get("/api/products")
def list_products(search: str = "", stock: str = "all", db: Session = Depends(get_db), user: User = Depends(current_user)):
    q = db.query(Product).filter(Product.organization_id == user.organization_id)
    if search.strip():
        term = f"%{search.strip()}%"
        q = q.filter(or_(Product.name.ilike(term), Product.sku.ilike(term)))
    org = db.query(Organization).filter(Organization.id == user.organization_id).first()
    default_threshold = org.default_low_stock_threshold if org else 5
    if stock == "low":
        q = q.filter(Product.quantity <= func.coalesce(Product.low_stock_threshold, default_threshold))
    elif stock == "healthy":
        q = q.filter(Product.quantity > func.coalesce(Product.low_stock_threshold, default_threshold))
    return [product_dict(p) for p in q.order_by(Product.updated_at.desc()).all()]

@app.post("/api/products", status_code=201)
def create_product(data: ProductIn, db: Session = Depends(get_db), user: User = Depends(current_user)):
    duplicate = db.query(Product).filter(Product.organization_id == user.organization_id, func.lower(Product.sku) == data.sku.lower()).first()
    if duplicate:
        raise HTTPException(409, "A product with this SKU already exists in your organization")
    p = Product(**data.model_dump(), organization_id=user.organization_id)
    db.add(p)
    db.commit()
    db.refresh(p)
    return product_dict(p)

@app.get("/api/products/{product_id}")
def get_product(product_id: int, db: Session = Depends(get_db), user: User = Depends(current_user)):
    p = db.query(Product).filter(Product.id == product_id, Product.organization_id == user.organization_id).first()
    if not p: raise HTTPException(404, "Product not found")
    return product_dict(p)

@app.put("/api/products/{product_id}")
def update_product(product_id: int, data: ProductIn, db: Session = Depends(get_db), user: User = Depends(current_user)):
    p = db.query(Product).filter(Product.id == product_id, Product.organization_id == user.organization_id).first()
    if not p: raise HTTPException(404, "Product not found")
    duplicate = db.query(Product).filter(Product.organization_id == user.organization_id, func.lower(Product.sku) == data.sku.lower(), Product.id != product_id).first()
    if duplicate: raise HTTPException(409, "Another product already uses this SKU")
    for key, value in data.model_dump().items(): setattr(p, key, value)
    db.commit()
    db.refresh(p)
    return product_dict(p)

@app.delete("/api/products/{product_id}")
def delete_product(product_id: int, db: Session = Depends(get_db), user: User = Depends(current_user)):
    p = db.query(Product).filter(Product.id == product_id, Product.organization_id == user.organization_id).first()
    if not p: raise HTTPException(404, "Product not found")
    db.delete(p)
    db.commit()
    return {"message": "Product deleted"}

@app.post("/api/products/{product_id}/adjust")
def adjust_stock(product_id: int, change: int, db: Session = Depends(get_db), user: User = Depends(current_user)):
    p = db.query(Product).filter(Product.id == product_id, Product.organization_id == user.organization_id).first()
    if not p: raise HTTPException(404, "Product not found")
    if p.quantity + change < 0: raise HTTPException(400, "Stock quantity cannot become negative")
    p.quantity += change
    db.commit()
    db.refresh(p)
    return product_dict(p)

@app.get("/api/dashboard")
def dashboard(db: Session = Depends(get_db), user: User = Depends(current_user)):
    org = db.query(Organization).filter(Organization.id == user.organization_id).first()
    products = db.query(Product).filter(Product.organization_id == user.organization_id).all()
    threshold = org.default_low_stock_threshold if org else 5
    low = [p for p in products if p.quantity <= (p.low_stock_threshold if p.low_stock_threshold is not None else threshold)]
    return {
        "total_products": len(products),
        "total_units": sum(p.quantity for p in products),
        "low_stock_count": len(low),
        "inventory_cost_value": round(sum((p.cost_price or 0) * p.quantity for p in products), 2),
        "inventory_retail_value": round(sum((p.selling_price or 0) * p.quantity for p in products), 2),
        "low_stock_items": [product_dict(p) for p in sorted(low, key=lambda x: x.quantity)]
    }

@app.get("/api/settings")
def get_settings(db: Session = Depends(get_db), user: User = Depends(current_user)):
    org = db.query(Organization).filter(Organization.id == user.organization_id).first()
    return {"organization_name": org.name, "default_low_stock_threshold": org.default_low_stock_threshold}

@app.put("/api/settings")
def update_settings(data: SettingsIn, db: Session = Depends(get_db), user: User = Depends(current_user)):
    org = db.query(Organization).filter(Organization.id == user.organization_id).first()
    org.default_low_stock_threshold = data.default_low_stock_threshold
    db.commit()
    return {"message": "Settings updated", "default_low_stock_threshold": org.default_low_stock_threshold}
