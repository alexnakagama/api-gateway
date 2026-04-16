from fastapi import FastAPI, Request

from app.services.users.users import proxy_service
from app.services.inventory.inventory import proxy_inventory

app = FastAPI()

# Users
@app.api_route("/users/{path:path}", methods=["GET","POST","PUT","DELETE"])
async def users_proxy(path: str, request: Request):
    return proxy_service("users", path, request)

# Inventory
@app.api_route("/inventory/{path:path}", methods=["GET","POST","PUT","DELETE"])
async def inventory_proxy(path: str, request: Request):
    return proxy_inventory("inventory", path, request)