from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from enum import Enum
import uvicorn
from datetime import datetime

app = FastAPI(
    title="Order Service",
    description="Microservice for managing orders in the E-Commerce platform",
    version="1.0.0",
    docs_url="/docs",
    openapi_url="/openapi.json"
)

# ── Models ──────────────────────────────────────────────────────────────────
class OrderStatus(str, Enum):
    PENDING = "pending"
    CONFIRMED = "confirmed"
    SHIPPED = "shipped"
    DELIVERED = "delivered"
    CANCELLED = "cancelled"

class OrderItem(BaseModel):
    product_id: int
    product_name: str
    quantity: int
    unit_price: float

class Order(BaseModel):
    id: Optional[int] = None
    customer_id: int
    items: List[OrderItem]
    total_amount: float
    status: OrderStatus = OrderStatus.PENDING
    created_at: Optional[str] = None

# ── In-memory database ───────────────────────────────────────────────────────
orders_db: List[Order] = [
    Order(
        id=1,
        customer_id=1,
        items=[OrderItem(product_id=1, product_name="Laptop Pro", quantity=1, unit_price=1200.00)],
        total_amount=1200.00,
        status=OrderStatus.CONFIRMED,
        created_at="2026-03-01T10:00:00"
    ),
    Order(
        id=2,
        customer_id=2,
        items=[
            OrderItem(product_id=2, product_name="Wireless Mouse", quantity=2, unit_price=25.99),
            OrderItem(product_id=3, product_name="USB-C Hub", quantity=1, unit_price=45.00),
        ],
        total_amount=96.98,
        status=OrderStatus.PENDING,
        created_at="2026-03-10T14:30:00"
    ),
]
counter = 3

# ── Routes ───────────────────────────────────────────────────────────────────
@app.get("/", tags=["Health"])
def root():
    return {"service": "Order Service", "status": "running", "port": 8003}

@app.get("/orders", response_model=List[Order], tags=["Orders"])
def get_all_orders():
    """Retrieve all orders"""
    return orders_db

@app.get("/orders/{order_id}", response_model=Order, tags=["Orders"])
def get_order(order_id: int):
    """Retrieve a specific order by ID"""
    order = next((o for o in orders_db if o.id == order_id), None)
    if not order:
        raise HTTPException(status_code=404, detail=f"Order with ID {order_id} not found")
    return order

@app.get("/orders/customer/{customer_id}", response_model=List[Order], tags=["Orders"])
def get_orders_by_customer(customer_id: int):
    """Retrieve all orders for a specific customer"""
    customer_orders = [o for o in orders_db if o.customer_id == customer_id]
    return customer_orders

@app.post("/orders", response_model=Order, status_code=201, tags=["Orders"])
def create_order(order: Order):
    """Place a new order"""
    global counter
    order.id = counter
    counter += 1
    order.created_at = datetime.now().isoformat()
    orders_db.append(order)
    return order

@app.put("/orders/{order_id}/status", response_model=Order, tags=["Orders"])
def update_order_status(order_id: int, status: OrderStatus):
    """Update the status of an order"""
    for i, o in enumerate(orders_db):
        if o.id == order_id:
            orders_db[i].status = status
            return orders_db[i]
    raise HTTPException(status_code=404, detail=f"Order with ID {order_id} not found")

@app.delete("/orders/{order_id}", tags=["Orders"])
def cancel_order(order_id: int):
    """Cancel/delete an order"""
    global orders_db
    order = next((o for o in orders_db if o.id == order_id), None)
    if not order:
        raise HTTPException(status_code=404, detail=f"Order with ID {order_id} not found")
    orders_db = [o for o in orders_db if o.id != order_id]
    return {"message": f"Order {order_id} cancelled successfully"}

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8003, reload=True)
