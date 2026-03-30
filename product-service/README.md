# Product Service — Chalaka
**Port:** 8001  
**Owner:** Chalaka  
**Branch:** feature/product-service

## Run
```bash
pip install -r requirements.txt
uvicorn main:app --reload --port 8001
```

## Swagger UI
http://localhost:8001/docs

## Endpoints
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | /products | Get all products |
| GET | /products/{id} | Get product by ID |
| POST | /products | Create product |
| PUT | /products/{id} | Update product |
| DELETE | /products/{id} | Delete product |
