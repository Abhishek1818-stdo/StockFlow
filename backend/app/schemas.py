from pydantic import BaseModel, EmailStr, Field, ConfigDict
from typing import Optional

class SignupIn(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)
    organization_name: str = Field(min_length=2, max_length=150)

class LoginIn(BaseModel):
    email: EmailStr
    password: str

class TokenOut(BaseModel):
    access_token: str
    token_type: str = "bearer"

class ProductIn(BaseModel):
    name: str = Field(min_length=1, max_length=150)
    sku: str = Field(min_length=1, max_length=100)
    description: Optional[str] = None
    quantity: int = Field(ge=0)
    cost_price: Optional[float] = Field(default=None, ge=0)
    selling_price: Optional[float] = Field(default=None, ge=0)
    low_stock_threshold: Optional[int] = Field(default=None, ge=0)

class ProductOut(ProductIn):
    model_config = ConfigDict(from_attributes=True)
    id: int
    organization_id: int
    created_at: str
    updated_at: str

class SettingsIn(BaseModel):
    default_low_stock_threshold: int = Field(ge=0, le=100000)
