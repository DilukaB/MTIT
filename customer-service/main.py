from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional

app = FastAPI(
    title="Customer Service",
    description="Manages customers in the e-commerce platform",
    version="1.0.0"
)

customers_db = [
    {"id": 1, "name": "Alice Johnson", "email": "alice@email.com", "phone": "0771234567", "address": "Colombo 03"},
    {"id": 2, "name": "Bob Silva", "email": "bob@email.com", "phone": "0777654321", "address": "Kandy"},
    {"id": 3, "name": "Carol Fernando", "email": "carol@email.com", "phone": "0779876543", "address": "Galle"},
]

class Customer(BaseModel):
    name: str
    email: str
    phone: str
    address: str

class CustomerUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[str] = None

@app.get("/", tags=["Health"])
def root():
    return {"service": "Customer Service", "status": "running", "port": 8002}

@app.get("/customers", tags=["Customers"])
def get_all_customers():
    """Get all customers"""
    return {"customers": customers_db, "total": len(customers_db)}

@app.get("/customers/{customer_id}", tags=["Customers"])
def get_customer(customer_id: int):
    """Get a single customer by ID"""
    customer = next((c for c in customers_db if c["id"] == customer_id), None)
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")
    return customer

@app.post("/customers", tags=["Customers"], status_code=201)
def create_customer(customer: Customer):
    """Register a new customer"""
    if any(c["email"] == customer.email for c in customers_db):
        raise HTTPException(status_code=400, detail="Email already registered")
    new_id = max(c["id"] for c in customers_db) + 1
    new_customer = {"id": new_id, **customer.dict()}
    customers_db.append(new_customer)
    return {"message": "Customer registered successfully", "customer": new_customer}

@app.put("/customers/{customer_id}", tags=["Customers"])
def update_customer(customer_id: int, update: CustomerUpdate):
    """Update customer details"""
    customer = next((c for c in customers_db if c["id"] == customer_id), None)
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")
    for key, value in update.dict(exclude_none=True).items():
        customer[key] = value
    return {"message": "Customer updated", "customer": customer}

@app.delete("/customers/{customer_id}", tags=["Customers"])
def delete_customer(customer_id: int):
    """Delete a customer"""
    global customers_db
    customer = next((c for c in customers_db if c["id"] == customer_id), None)
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")
    customers_db = [c for c in customers_db if c["id"] != customer_id]
    return {"message": "Customer deleted successfully"}
