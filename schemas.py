"""
Database Schemas

Define your MongoDB collection schemas here using Pydantic models.
These schemas are used for data validation in your application.

Each Pydantic model represents a collection in your database.
Model name is converted to lowercase for the collection name:
- User -> "user" collection
- Product -> "product" collection
- BlogPost -> "blogs" collection
"""

from pydantic import BaseModel, Field
from typing import Optional, List, Dict

class User(BaseModel):
    """
    Users collection schema
    Collection name: "user" (lowercase of class name)
    """
    name: str = Field(..., description="Full name")
    email: str = Field(..., description="Email address")
    address: str = Field(..., description="Address")
    age: Optional[int] = Field(None, ge=0, le=120, description="Age in years")
    is_active: bool = Field(True, description="Whether user is active")

class Product(BaseModel):
    """
    Products collection schema
    Collection name: "product" (lowercase of class name)
    """
    title: str = Field(..., description="Product name")
    description: Optional[str] = Field(None, description="Marketing description")
    category: str = Field(..., description="Category e.g. chair, mat")
    images: List[str] = Field(default_factory=list, description="Image URLs")
    specs: Dict[str, str] = Field(default_factory=dict, description="Key-value specs")
    tags: List[str] = Field(default_factory=list, description="Searchable tags")
    price_from: Optional[float] = Field(None, ge=0, description="Optional starting price for reference")
    in_stock: bool = Field(True, description="Whether product is in stock")

class QuoteRequest(BaseModel):
    """
    Quote requests from prospects
    Collection name: "quoterequest"
    """
    product_id: Optional[str] = Field(None, description="ID of product of interest")
    product_title: Optional[str] = Field(None, description="Fallback product title if ID not provided")
    name: str = Field(..., description="Contact name")
    company: Optional[str] = Field(None, description="Company name")
    email: str = Field(..., description="Contact email")
    phone: Optional[str] = Field(None, description="Phone number")
    quantity: Optional[int] = Field(1, ge=1, description="Estimated quantity")
    message: Optional[str] = Field(None, description="Additional notes or requirements")
