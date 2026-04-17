# API Gateway

A production-ready API Gateway built with FastAPI that acts as a single entry point for a microservices architecture. It handles routing, rate limiting, CORS, and centralized logging across all downstream services.

---

## Table of Contents

- [Architecture](#architecture)
- [Tech Stack](#tech-stack)
- [Project Structure](#project-structure)
- [Prerequisites](#prerequisites)
- [Getting Started](#getting-started)
- [Environment Variables](#environment-variables)
- [API Endpoints](#api-endpoints)
- [Features](#features)
- [Running Tests](#running-tests)
- [Adding a New Microservice](#adding-a-new-microservice)

---

## Architecture

```
Client (browser, mobile app, third-party)
                  |
                  v
         +------------------+
         |   API Gateway    |   localhost:8000
         |    (FastAPI)     |
         +--------+---------+
                  |
       +----------+----------+
       |                     |
       v                     v
 +-----------+        +-------------+
 |   Users   |        |  Inventory  |
 | :8001     |        |  :8002      |
 +-----------+        +-------------+
```

All services communicate internally via Docker's bridge network (`microservices-net`) using their service names as hostnames.

---

## Tech Stack

| Component        | Technology          |
|------------------|---------------------|
| Language         | Python 3.12         |
| Framework        | FastAPI             |
| HTTP Client      | httpx               |
| Rate Limiting    | slowapi             |
| Configuration    | python-dotenv       |
| ASGI Server      | Uvicorn             |
| Testing          | pytest, FastAPI TestClient |
| Containerization | Docker + Docker Compose |

---

## Project Structure

```
api-gateway/
├── docker-compose.yml           # Orchestrates all services
├── README.md
├── gateway/
│   ├── Dockerfile
│   ├── pyproject.toml
│   ├── pytest.ini               # Pytest configuration
│   ├── env_example.py           # Environment variable reference
│   ├── README.md
│   ├── app/
│   │   ├── main.py              # FastAPI app: routes and middleware
│   │   ├── config.py            # Environment variable loading
│   │   └── services/
│   │       ├── users/
│   │       │   └── users.py     # HTTP proxy logic for Users service
│   │       └── inventory/
│   │           └── inventory.py # HTTP proxy logic for Inventory service
│   └── tests/
│       ├── test_health_check.py
│       └── test_users.py
└── services/
    ├── users/
    │   ├── Dockerfile
    │   ├── pyproject.toml
    │   ├── README.md
    │   └── main.py              # Users microservice
    └── inventory/
        ├── Dockerfile
        ├── pyproject.toml
        ├── README.md
        └── main.py              # Inventory microservice
```

---

## Prerequisites

- [Docker](https://www.docker.com/) and [Docker Compose](https://docs.docker.com/compose/) v2+
- Python 3.12+ (only required for local development without Docker)

---

## Getting Started

### Docker Compose (recommended)

1. Clone the repository:
   ```bash
   git clone <your-repo-url>
   cd api-gateway
   ```

2. Copy and configure the environment file:
   ```bash
   cp gateway/env_example.py gateway/.env
   ```
   Edit `gateway/.env` with your values (see [Environment Variables](#environment-variables)).

3. Build and start all services:
   ```bash
   docker compose up --build
   ```

4. The gateway is available at `http://localhost:8000`.

To stop all services:
```bash
docker compose down
```

---

### Local Development (without Docker)

You will need three separate terminals.

**Terminal 1 — Users service:**
```bash
cd services/users
source .venv/bin/activate
uvicorn main:app --host 0.0.0.0 --port 8001
```

**Terminal 2 — Inventory service:**
```bash
cd services/inventory
source .venv/bin/activate
uvicorn main:app --host 0.0.0.0 --port 8002
```

**Terminal 3 — Gateway:**
```bash
cd gateway
source .venv/bin/activate
uvicorn app.main:app --reload
```

Point your `gateway/.env` to the correct local URLs:
```env
USERS_URL=http://localhost:8001
INVENTORY_URL=http://localhost:8002
CORS_ORIGINS=http://localhost:3000
RATE_LIMIT=10/minute
```

---

## Environment Variables

All environment variables are configured in `gateway/.env`. The gateway reads them at startup via `python-dotenv`.

| Variable          | Description                                        | Default        |
|-------------------|----------------------------------------------------|----------------|
| `USERS_URL`       | Base URL of the Users microservice                 | —              |
| `INVENTORY_URL`   | Base URL of the Inventory microservice             | —              |
| `CORS_ORIGINS`    | Comma-separated list of allowed CORS origins       | `*`            |
| `RATE_LIMIT`      | Rate limit per IP address (slowapi format)         | `10/minute`    |

**Example `.env` for Docker:**
```env
USERS_URL=http://users:8000
INVENTORY_URL=http://inventory:8000
CORS_ORIGINS=http://localhost:3000,https://yourdomain.com
RATE_LIMIT=20/minute
```

**Example `.env` for local development:**
```env
USERS_URL=http://localhost:8001
INVENTORY_URL=http://localhost:8002
CORS_ORIGINS=http://localhost:3000
RATE_LIMIT=100/minute
```

---

## API Endpoints

All requests are sent to the gateway at `http://localhost:8000`. The gateway forwards them to the appropriate microservice based on the URL prefix.

### Health Check

| Method | URL       | Description                  |
|--------|-----------|------------------------------|
| GET    | `/health` | Returns gateway health status |

**Request:**
```bash
curl http://localhost:8000/health
```

**Response:**
```json
{
  "status": "ok"
}
```

---

### Users

All requests to `/users/{path}` are proxied to the Users microservice.

| Method | Gateway URL     | Proxied To              | Description     |
|--------|-----------------|-------------------------|-----------------|
| GET    | `/users/users`  | `USERS_URL/users`       | Get all users   |

**Request:**
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

### Inventory

All requests to `/inventory/{path}` are proxied to the Inventory microservice.

| Method | Gateway URL             | Proxied To                    | Description          |
|--------|-------------------------|-------------------------------|----------------------|
| GET    | `/inventory/inventory`  | `INVENTORY_URL/inventory`     | Get all inventory    |

**Request:**
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

### Interactive Documentation

FastAPI automatically generates interactive API documentation:

| Interface   | URL                                      |
|-------------|------------------------------------------|
| Swagger UI  | http://localhost:8000/docs               |
| ReDoc       | http://localhost:8000/redoc              |

---

## Features

- **Reverse Proxy** — Routes requests to the correct microservice based on the URL prefix. Forwards method, headers, and body transparently.
- **Rate Limiting** — Limits requests per client IP using `slowapi`. Configurable via the `RATE_LIMIT` environment variable (e.g., `10/minute`, `100/hour`).
- **CORS** — Configurable allowed origins, credentials, methods, and headers via environment variables.
- **Centralized Logging** — Logs every incoming request with timestamp, log level, path, HTTP method, and client IP.
- **Error Handling** — Returns `502 Bad Gateway` if a downstream microservice is unreachable, with a descriptive error message.
- **Health Check** — Dedicated `/health` endpoint for monitoring and load balancer probes.

---

## Running Tests

Tests are located in `gateway/tests/` and use `pytest` with FastAPI's `TestClient`.

Install development dependencies (inside the gateway virtual environment):
```bash
cd gateway
source .venv/bin/activate
pip install pytest
```

Run all tests:
```bash
cd gateway
pytest
```

Expected output:
```
collected 2 items

tests/test_health_check.py .     [ 50%]
tests/test_users.py .            [100%]

2 passed in 0.5s
```

---

## Adding a New Microservice

Follow these steps to register a new service in the gateway:

1. **Create the service** in `services/your-service/` with its own `Dockerfile` and `main.py`.

2. **Register the URL** in `gateway/.env`:
   ```env
   YOUR_SERVICE_URL=http://your-service:8000
   ```

3. **Add it to the service registry** in `gateway/app/config.py`:
   ```python
   SERVICES = {
       "users": os.getenv("USERS_URL"),
       "inventory": os.getenv("INVENTORY_URL"),
       "your-service": os.getenv("YOUR_SERVICE_URL"),
   }
   ```

4. **Add the proxy route** in `gateway/app/main.py`:
   ```python
   @limiter.limit(RATE_LIMIT)
   @app.api_route("/your-service/{path:path}", methods=["GET", "POST", "PUT", "DELETE"])
   async def your_service_proxy(path: str, request: Request):
       logging.info(f"Request to /your-service/{path} | Method: {request.method} | IP: {request.client.host}")
       return await proxy_service("your-service", path, request)
   ```

5. **Add the service to `docker-compose.yml`**:
   ```yaml
   your-service:
     build: ./services/your-service
     ports:
       - "8003:8000"
     networks:
       - microservices-net
   ```

   And add the environment variable to the `gateway` service:
   ```yaml
   environment:
     - YOUR_SERVICE_URL=http://your-service:8000
   ```
