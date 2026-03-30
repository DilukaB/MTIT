from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional

app = FastAPI(
    title="Product Service",
    description="Manages products in the e-commerce platform",
    version="1.0.0"
)

products_db = [
    {"id": 1, "name": "Laptop", "price": 999.99, "stock": 10, "category": "Electronics"},
    {"id": 2, "name": "T-Shirt", "price": 19.99, "stock": 50, "category": "Clothing"},
    {"id": 3, "name": "Headphones", "price": 149.99, "stock": 25, "category": "Electronics"},
]

class Product(BaseModel):
    name: str
    price: float
    stock: int
    category: str

class ProductUpdate(BaseModel):
    name: Optional[str] = None
    price: Optional[float] = None
    stock: Optional[int] = None
    category: Optional[str] = None

@app.get("/", tags=["Health"])
def root():
    return {"service": "Product Service", "status": "running", "port": 8001}

@app.get("/products", tags=["Products"])
def get_all_products():
    """Get all products"""
    return {"products": products_db, "total": len(products_db)}

@app.get("/products/{product_id}", tags=["Products"])
def get_product(product_id: int):
    """Get a single product by ID"""
    product = next((p for p in products_db if p["id"] == product_id), None)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return product

@app.post("/products", tags=["Products"], status_code=201)
def create_product(product: Product):
    """Create a new product"""
    new_id = max(p["id"] for p in products_db) + 1
    new_product = {"id": new_id, **product.dict()}
    products_db.append(new_product)
    return {"message": "Product created successfully", "product": new_product}

@app.put("/products/{product_id}", tags=["Products"])
def update_product(product_id: int, update: ProductUpdate):
    """Update an existing product"""
    product = next((p for p in products_db if p["id"] == product_id), None)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    for key, value in update.dict(exclude_none=True).items():
        product[key] = value
    return {"message": "Product updated", "product": product}

@app.delete("/products/{product_id}", tags=["Products"])
def delete_product(product_id: int):
    """Delete a product"""
    global products_db
    product = next((p for p in products_db if p["id"] == product_id), None)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    products_db = [p for p in products_db if p["id"] != product_id]
    return {"message": "Product deleted successfully"}
