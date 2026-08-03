from fastapi import Request, HTTPException
from starlette.middleware.base import BaseHTTPMiddleware
import time

class RateLimitMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, max_requests: int = 100, window: int = 60):
        super().__init__(app)
        self.max_requests = max_requests
        self.window = window
        self.requests = {}
    async def dispatch(self, request: Request, call_next):
        client_ip = request.client.host
        now = time.time()
        self.requests = {ip: [t for t in times if now - t < self.window] for ip, times in self.requests.items()}
        client_requests = self.requests.get(client_ip, [])
        if len(client_requests) >= self.max_requests:
            raise HTTPException(status_code=429, detail="Rate limit exceeded")
        client_requests.append(now)
        self.requests[client_ip] = client_requests
        return await call_next(request)
