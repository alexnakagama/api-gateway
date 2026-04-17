# Gateway

The API Gateway is the single entry point for all client requests in this microservices architecture. It receives incoming HTTP requests, applies cross-cutting concerns (rate limiting, CORS, logging), and transparently forwards each request to the appropriate downstream microservice.

---

## Table of Contents

- [Responsibilities](#responsibilities)
- [Tech Stack](#tech-stack)
- [Project Structure](#project-structure)
- [Configuration](#configuration)
- [Running Locally](#running-locally)
- [Routes](#routes)
- [Proxy Behavior](#proxy-behavior)
- [Rate Limiting](#rate-limiting)
- [CORS](#cors)
- [Logging](#logging)
- [Error Handling](#error-handling)
- [Running Tests](#running-tests)

---

## Responsibilities

- Route incoming requests to the correct microservice based on the URL prefix.
- Enforce rate limits per client IP address.
- Handle CORS headers for browser-based clients.
- Log all incoming requests with method, path, and client IP.
- Return standardized error responses when a downstream service is unavailable.

---

## Tech Stack

| Component      | Technology         |
|----------------|--------------------|
| Language       | Python 3.12        |
| Framework      | FastAPI            |
| HTTP Client    | httpx              |
| Rate Limiting  | slowapi            |
| Configuration  | python-dotenv      |
| ASGI Server    | Uvicorn            |
| Testing        | pytest, FastAPI TestClient |

---

## Project Structure

```
gateway/
├── Dockerfile
├── pyproject.toml
├── pytest.ini
├── env_example.py
├── app/
│   ├── main.py              # FastAPI application, middleware, and route definitions
│   ├── config.py            # Loads and exposes environment variables
│   └── services/
│       ├── users/
│       │   └── users.py     # Proxy function for the Users microservice
│       └── inventory/
│           └── inventory.py # Proxy function for the Inventory microservice
└── tests/
    ├── test_health_check.py
    └── test_users.py
```

---

## Configuration

Copy the example file and fill in your values:

```bash
cp env_example.py .env
```

| Variable         | Description                                         | Example                        |
|------------------|-----------------------------------------------------|--------------------------------|
| `USERS_URL`      | Base URL of the Users microservice                  | `http://users:8000`            |
| `INVENTORY_URL`  | Base URL of the Inventory microservice              | `http://inventory:8000`        |
| `CORS_ORIGINS`   | Comma-separated list of allowed CORS origins        | `http://localhost:3000`        |
| `RATE_LIMIT`     | Rate limit per IP (slowapi format)                  | `10/minute`                    |

When running with Docker Compose, these variables are injected from the `docker-compose.yml` environment section and do not require a `.env` file.

---

## Running Locally

```bash
# Create and activate a virtual environment
python -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install -e .

# Set environment variables
cp env_example.py .env
# Edit .env with your local service URLs

# Start the gateway
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

The gateway will be available at `http://localhost:8000`.

---

## Routes

| Method | Path                        | Description                          |
|--------|-----------------------------|--------------------------------------|
| GET    | `/health`                   | Health check — returns gateway status |
| GET    | `/users/{path}`             | Proxies to Users microservice        |
| GET    | `/inventory/{path}`         | Proxies to Inventory microservice    |

The `{path}` parameter is a catch-all that captures any subroute, including nested paths like `/users/profile/settings`.

---

## Proxy Behavior

Each proxy function (`proxy_service`, `proxy_inventory`) forwards the incoming request to the corresponding downstream service, preserving:

- HTTP method
- Request headers
- Request body

The response from the downstream service (status code, headers, body) is returned as-is to the client.

**Example flow:**

```
GET http://localhost:8000/users/users
        |
        v
Gateway receives request
        |
        v
Forwards to http://users:8000/users
        |
        v
Returns response to client
```

---

## Rate Limiting

Rate limiting is applied per client IP address using `slowapi`. The limit is configured via the `RATE_LIMIT` environment variable using slowapi's format:

| Format        | Meaning                        |
|---------------|--------------------------------|
| `10/minute`   | 10 requests per minute per IP  |
| `100/hour`    | 100 requests per hour per IP   |
| `5/second`    | 5 requests per second per IP   |

When the limit is exceeded, the gateway returns a `429 Too Many Requests` response.

---

## CORS

CORS is configured via the `CORS_ORIGINS` environment variable. Multiple origins can be specified as a comma-separated list:

```env
CORS_ORIGINS=http://localhost:3000,https://yourdomain.com
```

The gateway allows all HTTP methods and headers for the configured origins.

---

## Logging

All incoming requests are logged to stdout in the following format:

```
2026-04-17 12:00:00,000 - INFO - Request to /users/users | Method: GET | IP: 127.0.0.1
```

Log entries include:
- Timestamp
- Log level
- Request path
- HTTP method
- Client IP address

---

## Error Handling

| Scenario                             | HTTP Status | Response Body                       |
|--------------------------------------|-------------|-------------------------------------|
| Downstream service unreachable       | `502`       | `"Users service unavailable"`       |
| Rate limit exceeded                  | `429`       | slowapi default response            |
| Route not found                      | `404`       | FastAPI default response            |

---

## Running Tests

Tests use `pytest` and FastAPI's built-in `TestClient`. No external services need to be running.

```bash
# From the gateway/ directory
pytest
```

Expected output:
```
collected 2 items

tests/test_health_check.py .     [ 50%]
tests/test_users.py .            [100%]

2 passed in 0.5s
```
