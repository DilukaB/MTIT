from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional
from datetime import datetime

app = FastAPI(
    title="Payment Service",
    description="Manages payments in the e-commerce platform",
    version="1.0.0"
)

payments_db = [
    {"id": 1, "order_id": 1, "customer_id": 1, "amount": 1999.98, "method": "credit_card", "status": "completed", "created_at": "2026-03-01"},
    {"id": 2, "order_id": 2, "customer_id": 2, "amount": 149.99, "method": "paypal", "status": "pending", "created_at": "2026-03-20"},
]

class Payment(BaseModel):
    order_id: int
    customer_id: int
    amount: float
    method: str  # credit_card, debit_card, paypal, bank_transfer

class PaymentStatusUpdate(BaseModel):
    status: str  # pending, completed, failed, refunded

@app.get("/", tags=["Health"])
def root():
    return {"service": "Payment Service", "status": "running", "port": 8004}

@app.get("/payments", tags=["Payments"])
def get_all_payments():
    """Get all payments"""
    return {"payments": payments_db, "total": len(payments_db)}

@app.get("/payments/{payment_id}", tags=["Payments"])
def get_payment(payment_id: int):
    """Get a single payment by ID"""
    payment = next((p for p in payments_db if p["id"] == payment_id), None)
    if not payment:
        raise HTTPException(status_code=404, detail="Payment not found")
    return payment

@app.get("/payments/order/{order_id}", tags=["Payments"])
def get_payment_by_order(order_id: int):
    """Get payment details for a specific order"""
    payment = next((p for p in payments_db if p["order_id"] == order_id), None)
    if not payment:
        raise HTTPException(status_code=404, detail="No payment found for this order")
    return payment

@app.get("/payments/customer/{customer_id}", tags=["Payments"])
def get_payments_by_customer(customer_id: int):
    """Get all payments by a specific customer"""
    customer_payments = [p for p in payments_db if p["customer_id"] == customer_id]
    if not customer_payments:
        raise HTTPException(status_code=404, detail="No payments found for this customer")
    return {"payments": customer_payments, "total": len(customer_payments)}

@app.post("/payments", tags=["Payments"], status_code=201)
def create_payment(payment: Payment):
    """Process a new payment"""
    valid_methods = ["credit_card", "debit_card", "paypal", "bank_transfer"]
    if payment.method not in valid_methods:
        raise HTTPException(status_code=400, detail=f"Invalid method. Choose from: {valid_methods}")
    new_id = max(p["id"] for p in payments_db) + 1
    new_payment = {
        "id": new_id,
        **payment.dict(),
        "status": "pending",
        "created_at": datetime.now().strftime("%Y-%m-%d")
    }
    payments_db.append(new_payment)
    return {"message": "Payment processed successfully", "payment": new_payment}

@app.patch("/payments/{payment_id}/status", tags=["Payments"])
def update_payment_status(payment_id: int, update: PaymentStatusUpdate):
    """Update payment status"""
    valid_statuses = ["pending", "completed", "failed", "refunded"]
    if update.status not in valid_statuses:
        raise HTTPException(status_code=400, detail=f"Invalid status. Choose from: {valid_statuses}")
    payment = next((p for p in payments_db if p["id"] == payment_id), None)
    if not payment:
        raise HTTPException(status_code=404, detail="Payment not found")
    payment["status"] = update.status
    return {"message": "Payment status updated", "payment": payment}

@app.delete("/payments/{payment_id}", tags=["Payments"])
def delete_payment(payment_id: int):
    """Delete a payment record"""
    global payments_db
    payment = next((p for p in payments_db if p["id"] == payment_id), None)
    if not payment:
        raise HTTPException(status_code=404, detail="Payment not found")
    payments_db = [p for p in payments_db if p["id"] != payment_id]
    return {"message": "Payment deleted successfully"}
