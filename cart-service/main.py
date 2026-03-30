from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional, Dict
import uvicorn

app = FastAPI(
    title="Cart Service",
    description="Microservice for managing shopping carts in the E-Commerce platform",
    version="1.0.0",
    docs_url="/docs",
    openapi_url="/openapi.json"
)

# ── Models ──────────────────────────────────────────────────────────────────
class CartItem(BaseModel):
    product_id: int
    product_name: str
    quantity: int
    unit_price: float

class Cart(BaseModel):
    id: Optional[int] = None
    customer_id: int
    items: List[CartItem] = []
    total_amount: Optional[float] = 0.0

# ── In-memory database ───────────────────────────────────────────────────────
# Key: customer_id -> Cart
carts_db: Dict[int, Cart] = {
    1: Cart(id=1, customer_id=1, items=[
        CartItem(product_id=2, product_name="Wireless Mouse", quantity=1, unit_price=25.99),
    ], total_amount=25.99),
    2: Cart(id=2, customer_id=2, items=[], total_amount=0.0),
}
counter = 3

def calculate_total(items: List[CartItem]) -> float:
    return round(sum(item.quantity * item.unit_price for item in items), 2)

# ── Routes ───────────────────────────────────────────────────────────────────
@app.get("/", tags=["Health"])
def root():
    return {"service": "Cart Service", "status": "running", "port": 8005}

@app.get("/carts", response_model=List[Cart], tags=["Cart"])
def get_all_carts():
    """Retrieve all carts"""
    return list(carts_db.values())

@app.get("/carts/{customer_id}", response_model=Cart, tags=["Cart"])
def get_cart(customer_id: int):
    """Retrieve cart for a specific customer"""
    cart = carts_db.get(customer_id)
    if not cart:
        raise HTTPException(status_code=404, detail=f"Cart for customer {customer_id} not found")
    return cart

@app.post("/carts/{customer_id}", response_model=Cart, status_code=201, tags=["Cart"])
def create_cart(customer_id: int):
    """Create an empty cart for a customer"""
    global counter
    if customer_id in carts_db:
        raise HTTPException(status_code=400, detail=f"Cart for customer {customer_id} already exists")
    new_cart = Cart(id=counter, customer_id=customer_id, items=[], total_amount=0.0)
    counter += 1
    carts_db[customer_id] = new_cart
    return new_cart

@app.post("/carts/{customer_id}/items", response_model=Cart, tags=["Cart"])
def add_item_to_cart(customer_id: int, item: CartItem):
    """Add an item to the cart"""
    if customer_id not in carts_db:
        # Auto-create cart if not exists
        global counter
        carts_db[customer_id] = Cart(id=counter, customer_id=customer_id, items=[], total_amount=0.0)
        counter += 1

    cart = carts_db[customer_id]
    # Check if item already exists, update quantity
    existing = next((i for i in cart.items if i.product_id == item.product_id), None)
    if existing:
        existing.quantity += item.quantity
    else:
        cart.items.append(item)

    cart.total_amount = calculate_total(cart.items)
    return cart

@app.put("/carts/{customer_id}/items/{product_id}", response_model=Cart, tags=["Cart"])
def update_cart_item(customer_id: int, product_id: int, quantity: int):
    """Update quantity of a specific item in cart"""
    cart = carts_db.get(customer_id)
    if not cart:
        raise HTTPException(status_code=404, detail=f"Cart for customer {customer_id} not found")

    item = next((i for i in cart.items if i.product_id == product_id), None)
    if not item:
        raise HTTPException(status_code=404, detail=f"Product {product_id} not in cart")

    if quantity <= 0:
        cart.items = [i for i in cart.items if i.product_id != product_id]
    else:
        item.quantity = quantity

    cart.total_amount = calculate_total(cart.items)
    return cart

@app.delete("/carts/{customer_id}/items/{product_id}", response_model=Cart, tags=["Cart"])
def remove_item_from_cart(customer_id: int, product_id: int):
    """Remove an item from the cart"""
    cart = carts_db.get(customer_id)
    if not cart:
        raise HTTPException(status_code=404, detail=f"Cart for customer {customer_id} not found")

    original_count = len(cart.items)
    cart.items = [i for i in cart.items if i.product_id != product_id]
    if len(cart.items) == original_count:
        raise HTTPException(status_code=404, detail=f"Product {product_id} not in cart")

    cart.total_amount = calculate_total(cart.items)
    return cart

@app.delete("/carts/{customer_id}", tags=["Cart"])
def clear_cart(customer_id: int):
    """Clear all items from the cart"""
    cart = carts_db.get(customer_id)
    if not cart:
        raise HTTPException(status_code=404, detail=f"Cart for customer {customer_id} not found")
    cart.items = []
    cart.total_amount = 0.0
    return {"message": f"Cart for customer {customer_id} cleared successfully"}

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8005, reload=True)
