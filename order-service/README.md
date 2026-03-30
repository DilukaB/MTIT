# Order Service — Diluka
**Port:** 8003  
**Owner:** Diluka  
**Branch:** feature/order-service

## Run
```bash
pip install -r requirements.txt
uvicorn main:app --reload --port 8003
```

## Swagger UI
http://localhost:8003/docs

## Endpoints
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | /orders | Get all orders |
| GET | /orders/{id} | Get order by ID |
| GET | /orders/customer/{id} | Get orders by customer |
| POST | /orders | Place new order |
| PATCH | /orders/{id}/status | Update order status |
| DELETE | /orders/{id} | Cancel order |
