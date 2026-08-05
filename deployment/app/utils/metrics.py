from time import perf_counter
from typing import Callable
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware


class MetricsCollectorMiddleware(BaseHTTPMiddleware):
    """Middleware collecting HTTP request latencies and response counts."""

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        start_time = perf_counter()
        response = await call_next(request)
        process_time = (perf_counter() - start_time) * 1000.0
        response.headers["X-Process-Time-Ms"] = f"{process_time:.2f}"
        return response
