from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional
import uvicorn

app = FastAPI(
    title="Customer Service",
    description="Microservice for managing customers in the E-Commerce platform",
    version="1.0.0",
    docs_url="/docs",
    openapi_url="/openapi.json"
)

# ── Models ──────────────────────────────────────────────────────────────────
class Customer(BaseModel):
    id: Optional[int] = None
    first_name: str
    last_name: str
    email: str
    phone: str
    address: str
    city: str

# ── In-memory database ───────────────────────────────────────────────────────
customers_db: List[Customer] = [
    Customer(id=1, first_name="Amal", last_name="Perera", email="amal@email.com", phone="0771234567", address="123 Galle Rd", city="Colombo"),
    Customer(id=2, first_name="Nimal", last_name="Silva", email="nimal@email.com", phone="0777654321", address="45 Kandy Rd", city="Kandy"),
]
counter = 3

# ── Routes ───────────────────────────────────────────────────────────────────
@app.get("/", tags=["Health"])
def root():
    return {"service": "Customer Service", "status": "running", "port": 8002}

@app.get("/customers", response_model=List[Customer], tags=["Customers"])
def get_all_customers():
    """Retrieve all customers"""
    return customers_db

@app.get("/customers/{customer_id}", response_model=Customer, tags=["Customers"])
def get_customer(customer_id: int):
    """Retrieve a specific customer by ID"""
    customer = next((c for c in customers_db if c.id == customer_id), None)
    if not customer:
        raise HTTPException(status_code=404, detail=f"Customer with ID {customer_id} not found")
    return customer

@app.post("/customers", response_model=Customer, status_code=201, tags=["Customers"])
def create_customer(customer: Customer):
    """Register a new customer"""
    global counter
    # Check for duplicate email
    existing = next((c for c in customers_db if c.email == customer.email), None)
    if existing:
        raise HTTPException(status_code=400, detail="Customer with this email already exists")
    customer.id = counter
    counter += 1
    customers_db.append(customer)
    return customer

@app.put("/customers/{customer_id}", response_model=Customer, tags=["Customers"])
def update_customer(customer_id: int, updated_customer: Customer):
    """Update customer details"""
    for i, c in enumerate(customers_db):
        if c.id == customer_id:
            updated_customer.id = customer_id
            customers_db[i] = updated_customer
            return updated_customer
    raise HTTPException(status_code=404, detail=f"Customer with ID {customer_id} not found")

@app.delete("/customers/{customer_id}", tags=["Customers"])
def delete_customer(customer_id: int):
    """Delete a customer by ID"""
    global customers_db
    customer = next((c for c in customers_db if c.id == customer_id), None)
    if not customer:
        raise HTTPException(status_code=404, detail=f"Customer with ID {customer_id} not found")
    customers_db = [c for c in customers_db if c.id != customer_id]
    return {"message": f"Customer {customer_id} deleted successfully"}

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8002, reload=True)
