from fastapi import FastAPI, Request

from app.services.users.users import proxy_service

app = FastAPI()

@app.api_route("/users/{path:path}", methods=["GET","POST","PUT","DELETE"])
async def users_proxy(path: str, request: Request):
    return proxy_service("users", path, request)