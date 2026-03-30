# API Gateway — Diluka
**Port:** 8000  
**Owner:** Diluka  
**Branch:** feature/api-gateway

## Run
```bash
pip install -r requirements.txt
uvicorn main:app --reload --port 8000
```

## Swagger UI
http://localhost:8000/docs

## How It Works
The API Gateway is the single entry point for all microservices.
Instead of calling each service on different ports, clients call port 8000 only.

| Gateway Route | Forwards To |
|---------------|-------------|
| /gateway/products | Product Service :8001 |
| /gateway/customers | Customer Service :8002 |
| /gateway/orders | Order Service :8003 |
| /gateway/payments | Payment Service :8004 |
