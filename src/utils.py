import time
from fastapi import HTTPException, Request, status

class IPRateLimiter:
    def __init__(self, request_limit: int = 30, window_seconds: int = 60):
        self.request_limit = request_limit
        self.window_seconds = window_seconds
        self.history: dict[str, list[float]] = {}

    def check_limit(self, request: Request):
        ip = request.headers.get("X-Forwarded-for") or (request.client.host if request.client else "unknown")

        current_time = time.time()

        if ip not in self.history:
            self.history[ip] = []

        self.history[ip] = [
                timestamp for timestamp in self.history[ip]
                if current_time - timestamp < self.window_seconds
                ]

        if len(self.history[ip]) >= self.request_limit:
            raise HTTPException(status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                                detail="Your IP has suspicious activite, try again in 1 minute.")

        self.history[ip].append(current_time)

limiter = IPRateLimiter(request_limit=30, window_seconds=60)


