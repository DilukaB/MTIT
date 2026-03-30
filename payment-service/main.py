from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from enum import Enum
import uvicorn
from datetime import datetime

app = FastAPI(
    title="Payment Service",
    description="Microservice for managing payments in the E-Commerce platform",
    version="1.0.0",
    docs_url="/docs",
    openapi_url="/openapi.json"
)

# ── Models ──────────────────────────────────────────────────────────────────
class PaymentMethod(str, Enum):
    CREDIT_CARD = "credit_card"
    DEBIT_CARD = "debit_card"
    PAYPAL = "paypal"
    BANK_TRANSFER = "bank_transfer"
    CASH_ON_DELIVERY = "cash_on_delivery"

class PaymentStatus(str, Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    REFUNDED = "refunded"

class Payment(BaseModel):
    id: Optional[int] = None
    order_id: int
    customer_id: int
    amount: float
    method: PaymentMethod
    status: PaymentStatus = PaymentStatus.PENDING
    transaction_id: Optional[str] = None
    created_at: Optional[str] = None

# ── In-memory database ───────────────────────────────────────────────────────
payments_db: List[Payment] = [
    Payment(
        id=1, order_id=1, customer_id=1, amount=1200.00,
        method=PaymentMethod.CREDIT_CARD, status=PaymentStatus.COMPLETED,
        transaction_id="TXN-20260301-001", created_at="2026-03-01T10:05:00"
    ),
    Payment(
        id=2, order_id=2, customer_id=2, amount=96.98,
        method=PaymentMethod.PAYPAL, status=PaymentStatus.PENDING,
        transaction_id=None, created_at="2026-03-10T14:35:00"
    ),
]
counter = 3

# ── Routes ───────────────────────────────────────────────────────────────────
@app.get("/", tags=["Health"])
def root():
    return {"service": "Payment Service", "status": "running", "port": 8004}

@app.get("/payments", response_model=List[Payment], tags=["Payments"])
def get_all_payments():
    """Retrieve all payments"""
    return payments_db

@app.get("/payments/{payment_id}", response_model=Payment, tags=["Payments"])
def get_payment(payment_id: int):
    """Retrieve a specific payment by ID"""
    payment = next((p for p in payments_db if p.id == payment_id), None)
    if not payment:
        raise HTTPException(status_code=404, detail=f"Payment with ID {payment_id} not found")
    return payment

@app.get("/payments/order/{order_id}", response_model=List[Payment], tags=["Payments"])
def get_payments_by_order(order_id: int):
    """Retrieve all payments for a specific order"""
    return [p for p in payments_db if p.order_id == order_id]

@app.post("/payments", response_model=Payment, status_code=201, tags=["Payments"])
def process_payment(payment: Payment):
    """Initiate a new payment"""
    global counter
    payment.id = counter
    counter += 1
    payment.created_at = datetime.now().isoformat()
    # Simulate auto-generating transaction ID for non-COD payments
    if payment.method != PaymentMethod.CASH_ON_DELIVERY:
        payment.transaction_id = f"TXN-{datetime.now().strftime('%Y%m%d')}-{counter:03d}"
        payment.status = PaymentStatus.PROCESSING
    payments_db.append(payment)
    return payment

@app.put("/payments/{payment_id}/status", response_model=Payment, tags=["Payments"])
def update_payment_status(payment_id: int, status: PaymentStatus):
    """Update payment status (e.g., mark as completed or failed)"""
    for i, p in enumerate(payments_db):
        if p.id == payment_id:
            payments_db[i].status = status
            return payments_db[i]
    raise HTTPException(status_code=404, detail=f"Payment with ID {payment_id} not found")

@app.delete("/payments/{payment_id}", tags=["Payments"])
def delete_payment(payment_id: int):
    """Delete a payment record"""
    global payments_db
    payment = next((p for p in payments_db if p.id == payment_id), None)
    if not payment:
        raise HTTPException(status_code=404, detail=f"Payment with ID {payment_id} not found")
    payments_db = [p for p in payments_db if p.id != payment_id]
    return {"message": f"Payment {payment_id} deleted successfully"}

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8004, reload=True)
