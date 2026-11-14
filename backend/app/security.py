import hashlib
import secrets
from collections import defaultdict, deque
from threading import Lock
from time import monotonic
from fastapi import Header, HTTPException, Request
from .config import settings


def token_hash(token: str):
    return hashlib.sha256(token.encode()).hexdigest()


def new_token():
    return secrets.token_urlsafe(32)


def require_admin(request: Request, authorization: str = Header(default="")):
    if settings.local_demo and request.client and request.client.host in {"127.0.0.1", "::1", "testclient"}:
        return
    expected = f"Bearer {settings.admin_token}"
    if not settings.admin_token or not secrets.compare_digest(authorization, expected):
        raise HTTPException(401, "Administrator authentication required")


class RateLimiter:
    def __init__(self):
        self.events = defaultdict(deque)
        self.lock = Lock()

    def check(self, key):
        now = monotonic()
        with self.lock:
            # Bound memory, including for invalid credentials.
            if key not in self.events and len(self.events) >= 10000:
                self.events = defaultdict(deque, {k: v for k, v in self.events.items() if v and v[-1] > now - 60})
                if len(self.events) >= 10000:
                    raise HTTPException(429, "Rate limiter capacity reached")
            events = self.events[key]
            while events and events[0] <= now - 60:
                events.popleft()
            if len(events) >= settings.ingestion_limit_per_minute:
                raise HTTPException(429, "Ingestion rate limit exceeded", headers={"Retry-After": "60"})
            events.append(now)


limiter = RateLimiter()
