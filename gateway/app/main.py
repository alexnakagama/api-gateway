from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware

from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

import logging

from app.services.users.users import proxy_service
from app.services.inventory.inventory import proxy_inventory

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Users
@limiter.limit("10/minute")
@app.api_route("/users/{path:path}", methods=["GET","POST","PUT","DELETE"])
async def users_proxy(path: str, request: Request):
    logging.info(f"Request to /users/{path} | Method: {request.method} | IP: {request.client.host}")
    return proxy_service("users", path, request)

# Inventory
@limiter.limit("10/minute")
@app.api_route("/inventory/{path:path}", methods=["GET","POST","PUT","DELETE"])
async def inventory_proxy(path: str, request: Request):
    logging.info(f"Request to /inventory/{path} | Method: {request.method} | IP: {request.client.host}")
    return proxy_inventory("inventory", path, request)