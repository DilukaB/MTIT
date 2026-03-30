from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional
import uvicorn

app = FastAPI(
    title="Product Service",
    description="Microservice for managing products in the E-Commerce platform",
    version="1.0.0",
    docs_url="/docs",
    openapi_url="/openapi.json"
)

# ── Models ──────────────────────────────────────────────────────────────────
class Product(BaseModel):
    id: Optional[int] = None
    name: str
    description: str
    price: float
    stock: int
    category: str

# ── In-memory database ───────────────────────────────────────────────────────
products_db: List[Product] = [
    Product(id=1, name="Laptop Pro", description="High-performance laptop", price=1200.00, stock=50, category="Electronics"),
    Product(id=2, name="Wireless Mouse", description="Ergonomic wireless mouse", price=25.99, stock=200, category="Accessories"),
    Product(id=3, name="USB-C Hub", description="7-in-1 USB-C hub", price=45.00, stock=150, category="Accessories"),
]
counter = 4

# ── Routes ───────────────────────────────────────────────────────────────────
@app.get("/", tags=["Health"])
def root():
    return {"service": "Product Service", "status": "running", "port": 8001}

@app.get("/products", response_model=List[Product], tags=["Products"])
def get_all_products():
    """Retrieve all products"""
    return products_db

@app.get("/products/{product_id}", response_model=Product, tags=["Products"])
def get_product(product_id: int):
    """Retrieve a specific product by ID"""
    product = next((p for p in products_db if p.id == product_id), None)
    if not product:
        raise HTTPException(status_code=404, detail=f"Product with ID {product_id} not found")
    return product

@app.post("/products", response_model=Product, status_code=201, tags=["Products"])
def create_product(product: Product):
    """Create a new product"""
    global counter
    product.id = counter
    counter += 1
    products_db.append(product)
    return product

@app.put("/products/{product_id}", response_model=Product, tags=["Products"])
def update_product(product_id: int, updated_product: Product):
    """Update an existing product"""
    for i, p in enumerate(products_db):
        if p.id == product_id:
            updated_product.id = product_id
            products_db[i] = updated_product
            return updated_product
    raise HTTPException(status_code=404, detail=f"Product with ID {product_id} not found")

@app.delete("/products/{product_id}", tags=["Products"])
def delete_product(product_id: int):
    """Delete a product by ID"""
    global products_db
    product = next((p for p in products_db if p.id == product_id), None)
    if not product:
        raise HTTPException(status_code=404, detail=f"Product with ID {product_id} not found")
    products_db = [p for p in products_db if p.id != product_id]
    return {"message": f"Product {product_id} deleted successfully"}

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8001, reload=True)
