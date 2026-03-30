# Customer Service — Randeni
**Port:** 8002  
**Owner:** Randeni  
**Branch:** feature/customer-service

## Run
```bash
pip install -r requirements.txt
uvicorn main:app --reload --port 8002
```

## Swagger UI
http://localhost:8002/docs

## Endpoints
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | /customers | Get all customers |
| GET | /customers/{id} | Get customer by ID |
| POST | /customers | Register customer |
| PUT | /customers/{id} | Update customer |
| DELETE | /customers/{id} | Delete customer |
