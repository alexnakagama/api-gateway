from fastapi import Response, Request

import httpx
from httpx import RequestError

from app.config import SERVICES

async def proxy_inventory(service_name: str, path: str, request: Request):
    service_url = f"{SERVICES[service_name]}/{path}"
    try:
        async with httpx.AsyncClient() as client:
            response = await client.request(
                method=request.method,
                url=service_url,
                headers=dict(request.headers),
                content=await request.body()
            )
        return Response(
            content=response.content,
            status_code=response.status_code,
            headers=dict(response.headers)
        )
    except RequestError:
        return Response(
            content=f"{service_name.capitalize()} service unavailable",
            status_code=502
        )