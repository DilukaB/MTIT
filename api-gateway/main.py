from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
import httpx

app = FastAPI(
    title="E-Commerce API Gateway",
    description="Single entry point for all microservices — routes to Product(8001), Customer(8002), Order(8003), Payment(8004)",
    version="1.0.0"
)

SERVICES = {
    "product":  "http://localhost:8001",
    "customer": "http://localhost:8002",
    "order":    "http://localhost:8003",
    "payment":  "http://localhost:8004",
}

async def forward_request(service_url: str, path: str, method: str, body: dict = None):
    url = f"{service_url}{path}"
    async with httpx.AsyncClient() as client:
        try:
            if method == "GET":
                response = await client.get(url)
            elif method == "POST":
                response = await client.post(url, json=body)
            elif method == "PUT":
                response = await client.put(url, json=body)
            elif method == "PATCH":
                response = await client.patch(url, json=body)
            elif method == "DELETE":
                response = await client.delete(url)
            return response.json(), response.status_code
        except httpx.ConnectError:
            raise HTTPException(status_code=503, detail=f"Service unavailable: {service_url}")

# ── GATEWAY ROOT ─────────────────────────────────
@app.get("/", tags=["Gateway"])
def gateway_root():
    return {
        "service": "API Gateway",
        "status": "running",
        "port": 8000,
        "routes": {
            "products":  "/gateway/products",
            "customers": "/gateway/customers",
            "orders":    "/gateway/orders",
            "payments":  "/gateway/payments"
        }
    }

# ── PRODUCT ROUTES (→ Port 8001) ─────────────────
@app.get("/gateway/products", tags=["Product Gateway"])
async def get_products():
    """[Gateway → 8001] Get all products"""
    data, status = await forward_request(SERVICES["product"], "/products", "GET")
    return JSONResponse(content=data, status_code=status)

@app.get("/gateway/products/{product_id}", tags=["Product Gateway"])
async def get_product(product_id: int):
    """[Gateway → 8001] Get product by ID"""
    data, status = await forward_request(SERVICES["product"], f"/products/{product_id}", "GET")
    return JSONResponse(content=data, status_code=status)

@app.post("/gateway/products", tags=["Product Gateway"])
async def create_product(request: Request):
    """[Gateway → 8001] Create a product"""
    body = await request.json()
    data, status = await forward_request(SERVICES["product"], "/products", "POST", body)
    return JSONResponse(content=data, status_code=status)

@app.put("/gateway/products/{product_id}", tags=["Product Gateway"])
async def update_product(product_id: int, request: Request):
    """[Gateway → 8001] Update a product"""
    body = await request.json()
    data, status = await forward_request(SERVICES["product"], f"/products/{product_id}", "PUT", body)
    return JSONResponse(content=data, status_code=status)

@app.delete("/gateway/products/{product_id}", tags=["Product Gateway"])
async def delete_product(product_id: int):
    """[Gateway → 8001] Delete a product"""
    data, status = await forward_request(SERVICES["product"], f"/products/{product_id}", "DELETE")
    return JSONResponse(content=data, status_code=status)

# ── CUSTOMER ROUTES (→ Port 8002) ────────────────
@app.get("/gateway/customers", tags=["Customer Gateway"])
async def get_customers():
    """[Gateway → 8002] Get all customers"""
    data, status = await forward_request(SERVICES["customer"], "/customers", "GET")
    return JSONResponse(content=data, status_code=status)

@app.get("/gateway/customers/{customer_id}", tags=["Customer Gateway"])
async def get_customer(customer_id: int):
    """[Gateway → 8002] Get customer by ID"""
    data, status = await forward_request(SERVICES["customer"], f"/customers/{customer_id}", "GET")
    return JSONResponse(content=data, status_code=status)

@app.post("/gateway/customers", tags=["Customer Gateway"])
async def create_customer(request: Request):
    """[Gateway → 8002] Register a customer"""
    body = await request.json()
    data, status = await forward_request(SERVICES["customer"], "/customers", "POST", body)
    return JSONResponse(content=data, status_code=status)

@app.put("/gateway/customers/{customer_id}", tags=["Customer Gateway"])
async def update_customer(customer_id: int, request: Request):
    """[Gateway → 8002] Update customer"""
    body = await request.json()
    data, status = await forward_request(SERVICES["customer"], f"/customers/{customer_id}", "PUT", body)
    return JSONResponse(content=data, status_code=status)

@app.delete("/gateway/customers/{customer_id}", tags=["Customer Gateway"])
async def delete_customer(customer_id: int):
    """[Gateway → 8002] Delete customer"""
    data, status = await forward_request(SERVICES["customer"], f"/customers/{customer_id}", "DELETE")
    return JSONResponse(content=data, status_code=status)

# ── ORDER ROUTES (→ Port 8003) ───────────────────
@app.get("/gateway/orders", tags=["Order Gateway"])
async def get_orders():
    """[Gateway → 8003] Get all orders"""
    data, status = await forward_request(SERVICES["order"], "/orders", "GET")
    return JSONResponse(content=data, status_code=status)

@app.get("/gateway/orders/{order_id}", tags=["Order Gateway"])
async def get_order(order_id: int):
    """[Gateway → 8003] Get order by ID"""
    data, status = await forward_request(SERVICES["order"], f"/orders/{order_id}", "GET")
    return JSONResponse(content=data, status_code=status)

@app.post("/gateway/orders", tags=["Order Gateway"])
async def create_order(request: Request):
    """[Gateway → 8003] Place an order"""
    body = await request.json()
    data, status = await forward_request(SERVICES["order"], "/orders", "POST", body)
    return JSONResponse(content=data, status_code=status)

@app.patch("/gateway/orders/{order_id}/status", tags=["Order Gateway"])
async def update_order_status(order_id: int, request: Request):
    """[Gateway → 8003] Update order status"""
    body = await request.json()
    data, status = await forward_request(SERVICES["order"], f"/orders/{order_id}/status", "PATCH", body)
    return JSONResponse(content=data, status_code=status)

@app.delete("/gateway/orders/{order_id}", tags=["Order Gateway"])
async def cancel_order(order_id: int):
    """[Gateway → 8003] Cancel an order"""
    data, status = await forward_request(SERVICES["order"], f"/orders/{order_id}", "DELETE")
    return JSONResponse(content=data, status_code=status)

# ── PAYMENT ROUTES (→ Port 8004) ─────────────────
@app.get("/gateway/payments", tags=["Payment Gateway"])
async def get_payments():
    """[Gateway → 8004] Get all payments"""
    data, status = await forward_request(SERVICES["payment"], "/payments", "GET")
    return JSONResponse(content=data, status_code=status)

@app.get("/gateway/payments/{payment_id}", tags=["Payment Gateway"])
async def get_payment(payment_id: int):
    """[Gateway → 8004] Get payment by ID"""
    data, status = await forward_request(SERVICES["payment"], f"/payments/{payment_id}", "GET")
    return JSONResponse(content=data, status_code=status)

@app.get("/gateway/payments/order/{order_id}", tags=["Payment Gateway"])
async def get_payment_by_order(order_id: int):
    """[Gateway → 8004] Get payment by order ID"""
    data, status = await forward_request(SERVICES["payment"], f"/payments/order/{order_id}", "GET")
    return JSONResponse(content=data, status_code=status)

@app.post("/gateway/payments", tags=["Payment Gateway"])
async def create_payment(request: Request):
    """[Gateway → 8004] Process a payment"""
    body = await request.json()
    data, status = await forward_request(SERVICES["payment"], "/payments", "POST", body)
    return JSONResponse(content=data, status_code=status)

@app.patch("/gateway/payments/{payment_id}/status", tags=["Payment Gateway"])
async def update_payment_status(payment_id: int, request: Request):
    """[Gateway → 8004] Update payment status"""
    body = await request.json()
    data, status = await forward_request(SERVICES["payment"], f"/payments/{payment_id}/status", "PATCH", body)
    return JSONResponse(content=data, status_code=status)

@app.delete("/gateway/payments/{payment_id}", tags=["Payment Gateway"])
async def delete_payment(payment_id: int):
    """[Gateway → 8004] Delete a payment"""
    data, status = await forward_request(SERVICES["payment"], f"/payments/{payment_id}", "DELETE")
    return JSONResponse(content=data, status_code=status)
