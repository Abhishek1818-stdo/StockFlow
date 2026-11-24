from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, Text, DateTime, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
from .database import Base

class Organization(Base):
    __tablename__ = "organizations"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(150), nullable=False)
    default_low_stock_threshold = Column(Integer, nullable=False, default=5)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    users = relationship("User", back_populates="organization")
    products = relationship("Product", back_populates="organization")

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    organization_id = Column(Integer, ForeignKey("organizations.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    organization = relationship("Organization", back_populates="users")

class Product(Base):
    __tablename__ = "products"
    __table_args__ = (UniqueConstraint("organization_id", "sku", name="uq_org_sku"),)
    id = Column(Integer, primary_key=True, index=True)
    organization_id = Column(Integer, ForeignKey("organizations.id"), nullable=False, index=True)
    name = Column(String(150), nullable=False)
    sku = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    quantity = Column(Integer, nullable=False, default=0)
    cost_price = Column(Float, nullable=True)
    selling_price = Column(Float, nullable=True)
    low_stock_threshold = Column(Integer, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    organization = relationship("Organization", back_populates="products")
