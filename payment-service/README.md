# Payment Service — Basnayake
**Port:** 8004  
**Owner:** Basnayake  
**Branch:** feature/payment-service

## Run
```bash
pip install -r requirements.txt
uvicorn main:app --reload --port 8004
```

## Swagger UI
http://localhost:8004/docs

## Endpoints
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | /payments | Get all payments |
| GET | /payments/{id} | Get payment by ID |
| GET | /payments/order/{id} | Get payment by order |
| GET | /payments/customer/{id} | Get payments by customer |
| POST | /payments | Process payment |
| PATCH | /payments/{id}/status | Update status |
| DELETE | /payments/{id} | Delete payment |
