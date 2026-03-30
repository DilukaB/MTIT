from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import httpx
import uvicorn

app = FastAPI(
    title="API Gateway",
    description="""
## E-Commerce Microservices API Gateway

The API Gateway is the **single entry point** for all client requests.  
Instead of calling each microservice on different ports, clients call the Gateway on **port 8000**.

### Routing Table

| Route Prefix             | Forwards To              | Port |
|--------------------------|--------------------------|------|
| `/api/products/**`       | Product Service          | 8001 |
| `/api/customers/**`      | Customer Service         | 8002 |
| `/api/orders/**`         | Order Service            | 8003 |
| `/api/payments/**`       | Payment Service          | 8004 |
| `/api/cart/**`           | Cart Service             | 8005 |
    """,
    version="1.0.0",
)

# ── CORS ─────────────────────────────────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Service Registry ──────────────────────────────────────────────────────────
SERVICE_REGISTRY = {
    "products":  "http://localhost:8001",
    "customers": "http://localhost:8002",
    "orders":    "http://localhost:8003",
    "payments":  "http://localhost:8004",
    "cart":      "http://localhost:8005",
}

# ── Health Check ──────────────────────────────────────────────────────────────
@app.get("/", tags=["Gateway"])
def root():
    return {
        "service": "API Gateway",
        "status": "running",
        "port": 8000,
        "registered_services": list(SERVICE_REGISTRY.keys()),
    }

@app.get("/health", tags=["Gateway"])
async def health_check():
    """Check health status of all microservices"""
    statuses = {}
    async with httpx.AsyncClient(timeout=3.0) as client:
        for name, base_url in SERVICE_REGISTRY.items():
            try:
                resp = await client.get(f"{base_url}/")
                statuses[name] = "UP" if resp.status_code == 200 else "DEGRADED"
            except Exception:
                statuses[name] = "DOWN"
    return {"gateway": "UP", "services": statuses}

# ── Dynamic Proxy Route ───────────────────────────────────────────────────────
@app.api_route(
    "/api/{service}/{path:path}",
    methods=["GET", "POST", "PUT", "DELETE", "PATCH"],
    tags=["Proxy"],
    summary="Dynamic proxy to microservices",
    description="Routes any request to the correct microservice based on the service name in the URL."
)
async def gateway_proxy(service: str, path: str, request: Request):
    """
    **Dynamic proxy** — forwards requests to the correct microservice.

    - `service` = one of: `products`, `customers`, `orders`, `payments`, `cart`
    - `path` = the rest of the original service URL

    **Example:**  
    `GET /api/products/products/1` → forwards to `http://localhost:8001/products/1`
    """
    if service not in SERVICE_REGISTRY:
        raise HTTPException(
            status_code=404,
            detail=f"Service '{service}' not found. Available: {list(SERVICE_REGISTRY.keys())}"
        )

    base_url = SERVICE_REGISTRY[service]
    target_url = f"{base_url}/{path}"

    # Forward query params
    query_string = str(request.url.query)
    if query_string:
        target_url = f"{target_url}?{query_string}"

    body = await request.body()

    # Strip hop-by-hop headers
    forward_headers = {
        k: v for k, v in request.headers.items()
        if k.lower() not in ("host", "content-length", "transfer-encoding")
    }

    async with httpx.AsyncClient(timeout=10.0) as client:
        try:
            response = await client.request(
                method=request.method,
                url=target_url,
                headers=forward_headers,
                content=body,
            )
            try:
                return JSONResponse(
                    content=response.json(),
                    status_code=response.status_code
                )
            except Exception:
                return JSONResponse(
                    content={"raw": response.text},
                    status_code=response.status_code
                )
        except httpx.ConnectError:
            raise HTTPException(
                status_code=503,
                detail=f"Service '{service}' is unavailable. Is it running on {base_url}?"
            )
        except httpx.TimeoutException:
            raise HTTPException(
                status_code=504,
                detail=f"Service '{service}' timed out."
            )


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
