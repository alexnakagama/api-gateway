# Inventory Service

A lightweight microservice responsible for inventory data. It exposes a REST API consumed exclusively through the API Gateway.

---

## Table of Contents

- [Tech Stack](#tech-stack)
- [Endpoints](#endpoints)
- [Running Locally](#running-locally)
- [Running with Docker](#running-with-docker)

---

## Tech Stack

| Component    | Technology  |
|--------------|-------------|
| Language     | Python 3.12 |
| Framework    | FastAPI     |
| ASGI Server  | Uvicorn     |

---

## Endpoints

This service listens on port `8000` internally (exposed as `8002` in Docker Compose).

| Method | Path          | Description             |
|--------|---------------|-------------------------|
| GET    | `/inventory`  | Get all inventory items |

**Request (direct, bypassing the gateway):**
```bash
curl http://localhost:8002/inventory
```

**Request (via the gateway):**
```bash
curl http://localhost:8000/inventory/inventory
```

**Response:**
```json
[
  { "id": 1, "item": "product A", "stock": 10 },
  { "id": 2, "item": "product B", "stock": 5 }
]
```

---

## Running Locally

```bash
# Create and activate a virtual environment
python -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install -e .

# Start the service
uvicorn main:app --host 0.0.0.0 --port 8002
```

Service is available at `http://localhost:8002`.

---

## Running with Docker

This service is managed by Docker Compose from the root of the repository:

```bash
docker compose up --build inventory
```

The service will be available within the Docker network at `http://inventory:8000` and externally at `http://localhost:8002`.
