# API Gateway

A microservices-based project with a centralized API Gateway built with FastAPI. The gateway handles all incoming requests and routes them to the appropriate microservice, while providing cross-cutting concerns like rate limiting, CORS, and logging.

## Architecture

```
Client (browser, app, etc.)
           │
           ▼
    ┌─────────────┐
    │ API Gateway │  :8000
    │  (FastAPI)  │
    └──────┬──────┘
           │
    ┌──────┴──────┐
    ▼             ▼
┌────────┐  ┌───────────┐
│ Users  │  │ Inventory │
│ :8001  │  │  :8002    │
└────────┘  └───────────┘
```

## Tech Stack

| Component | Technology |
|-----------|-----------|
| Language | Python 3.12 |
| Framework | FastAPI |
| HTTP Client | httpx |
| Rate Limiting | slowapi |
| Config | python-dotenv |
| Server | Uvicorn |
| Containerization | Docker + Docker Compose |

## Project Structure

```
api-gateway/
├── docker-compose.yml
├── README.md
├── gateway/
│   ├── Dockerfile
│   ├── pyproject.toml
│   ├── .env
│   └── app/
│       ├── main.py          # FastAPI app, routes and middleware
│       ├── config.py        # Environment variable configuration
│       └── services/
│           ├── users/
│           │   └── users.py     # Users proxy logic
│           └── inventory/
│               └── inventory.py # Inventory proxy logic
└── services/
    ├── users/
    │   ├── Dockerfile
    │   ├── pyproject.toml
    │   └── main.py          # Users microservice
    └── inventory/
        ├── Dockerfile
        ├── pyproject.toml
        └── main.py          # Inventory microservice
```

## Prerequisites

- [Docker](https://www.docker.com/) and [Docker Compose](https://docs.docker.com/compose/)
- Python 3.12+ (for local development without Docker)

## Getting Started

### With Docker Compose (recommended)

1. Clone the repository:
   ```bash
   git clone <your-repo-url>
   cd api-gateway
   ```

2. Configure environment variables (optional, defaults are provided):
   ```bash
   cp gateway/.env.example gateway/.env
   ```

3. Build and start all services:
   ```bash
   docker compose up --build
   ```

4. The gateway will be available at `http://localhost:8000`.

---

### Without Docker (local development)

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

Make sure your `gateway/.env` points to the correct local URLs:
```env
USERS_URL=http://localhost:8001
INVENTORY_URL=http://localhost:8002
CORS_ORIGINS=http://localhost:3000
RATE_LIMIT=10/minute
```

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `USERS_URL` | URL of the users microservice | `http://users:8000` |
| `INVENTORY_URL` | URL of the inventory microservice | `http://inventory:8000` |
| `CORS_ORIGINS` | Comma-separated list of allowed origins | `*` |
| `RATE_LIMIT` | Rate limit per IP (slowapi format) | `10/minute` |

## API Endpoints

All requests go through the gateway on port `8000`.

### Users

| Method | Gateway URL | Description |
|--------|-------------|-------------|
| GET | `/users/users` | Get all users |

**Example:**
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

| Method | Gateway URL | Description |
|--------|-------------|-------------|
| GET | `/inventory/inventory` | Get all inventory items |

**Example:**
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

### Interactive Docs

FastAPI automatically generates interactive documentation:

- Swagger UI: [http://localhost:8000/docs](http://localhost:8000/docs)
- ReDoc: [http://localhost:8000/redoc](http://localhost:8000/redoc)

## Features

- **Reverse Proxy:** Routes requests to the correct microservice based on the URL path.
- **Rate Limiting:** Limits requests per IP using slowapi (configurable via env).
- **CORS:** Configurable allowed origins via environment variables.
- **Logging:** Logs every request with method, path, and client IP.
- **Error Handling:** Returns `502 Bad Gateway` if a microservice is unreachable.

## Adding a New Microservice

1. Create your service in `services/your-service/`.
2. Add its URL to `gateway/.env`:
   ```env
   YOUR_SERVICE_URL=http://your-service:8000
   ```
3. Add it to `gateway/app/config.py`:
   ```python
   SERVICES = {
       ...
       "your-service": os.getenv("YOUR_SERVICE_URL"),
   }
   ```
4. Add a new route in `gateway/app/main.py`:
   ```python
   @limiter.limit(RATE_LIMIT)
   @app.api_route("/your-service/{path:path}", methods=["GET","POST","PUT","DELETE"])
   async def your_service_proxy(path: str, request: Request):
       return await proxy_service("your-service", path, request)
   ```
5. Add the service to `docker-compose.yml`.
