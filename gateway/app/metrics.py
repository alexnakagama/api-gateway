from prometheus_client import Counter, generate_latest

REQUEST_COUNT = Counter("request_count", "Total HTTP requests", ["method", "endpoint"])

def setup_metrics(app):
    from fastapi import Request, Response

    @app.middleware("http")
    async def count_requests(request: Request, call_next):
        response = await call_next(request)
        REQUEST_COUNT.labels(request.method, request.url.path).inc()
        return response

    @app.get("/metrics")
    def metrics():
        return Response(generate_latest(), media_type="text/plain")