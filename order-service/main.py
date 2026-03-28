from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional
from datetime import datetime

app = FastAPI(
    title="Order Service",
    description="Manages orders in the e-commerce platform",
    version="1.0.0"
)

orders_db = [
    {"id": 1, "customer_id": 1, "product_id": 1, "quantity": 2, "total_price": 1999.98, "status": "delivered", "created_at": "2026-03-01"},
    {"id": 2, "customer_id": 2, "product_id": 3, "quantity": 1, "total_price": 149.99, "status": "pending", "created_at": "2026-03-20"},
]

class Order(BaseModel):
    customer_id: int
    product_id: int
    quantity: int
    total_price: float

class OrderStatusUpdate(BaseModel):
    status: str  # pending, processing, shipped, delivered, cancelled

@app.get("/", tags=["Health"])
def root():
    return {"service": "Order Service", "status": "running"}

@app.get("/orders", tags=["Orders"])
def get_all_orders():
    """Get all orders"""
    return {"orders": orders_db, "total": len(orders_db)}

@app.get("/orders/{order_id}", tags=["Orders"])
def get_order(order_id: int):
    """Get a single order by ID"""
    order = next((o for o in orders_db if o["id"] == order_id), None)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    return order

@app.get("/orders/customer/{customer_id}", tags=["Orders"])
def get_orders_by_customer(customer_id: int):
    """Get all orders for a specific customer"""
    customer_orders = [o for o in orders_db if o["customer_id"] == customer_id]
    if not customer_orders:
        raise HTTPException(status_code=404, detail="No orders found for this customer")
    return {"orders": customer_orders, "total": len(customer_orders)}

@app.post("/orders", tags=["Orders"], status_code=201)
def create_order(order: Order):
    """Place a new order"""
    new_id = max(o["id"] for o in orders_db) + 1
    new_order = {
        "id": new_id,
        **order.dict(),
        "status": "pending",
        "created_at": datetime.now().strftime("%Y-%m-%d")
    }
    orders_db.append(new_order)
    return {"message": "Order placed successfully", "order": new_order}

@app.patch("/orders/{order_id}/status", tags=["Orders"])
def update_order_status(order_id: int, update: OrderStatusUpdate):
    """Update order status"""
    valid_statuses = ["pending", "processing", "shipped", "delivered", "cancelled"]
    if update.status not in valid_statuses:
        raise HTTPException(status_code=400, detail=f"Invalid status. Choose from: {valid_statuses}")
    order = next((o for o in orders_db if o["id"] == order_id), None)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    order["status"] = update.status
    return {"message": "Order status updated", "order": order}

@app.delete("/orders/{order_id}", tags=["Orders"])
def cancel_order(order_id: int):
    """Cancel/delete an order"""
    global orders_db
    order = next((o for o in orders_db if o["id"] == order_id), None)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    orders_db = [o for o in orders_db if o["id"] != order_id]
    return {"message": "Order cancelled successfully"}


 