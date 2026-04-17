# Users Service

A lightweight microservice responsible for user data. It exposes a REST API consumed exclusively through the API Gateway.

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

This service listens on port `8000` internally (exposed as `8001` in Docker Compose).

| Method | Path      | Description     |
|--------|-----------|-----------------|
| GET    | `/users`  | Get all users   |

**Request (direct, bypassing the gateway):**
```bash
curl http://localhost:8001/users
```

**Request (via the gateway):**
```bash
curl http://localhost:8000/users/users
```

**Response:**
```json
[
  { "id": 1, "name": "user example" }
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
uvicorn main:app --host 0.0.0.0 --port 8001
```

Service is available at `http://localhost:8001`.

---

## Running with Docker

This service is managed by Docker Compose from the root of the repository:

```bash
docker compose up --build users
```

The service will be available within the Docker network at `http://users:8000` and externally at `http://localhost:8001`.
