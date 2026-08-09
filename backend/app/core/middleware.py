import logging
import time
from uuid import uuid4

from fastapi import Request
from starlette.middleware.base import (
    BaseHTTPMiddleware,
    RequestResponseEndpoint,
)
from starlette.responses import (
    JSONResponse,
    Response,
)
from app.core.config import settings
from app.core.exception_handlers import create_error_content
from app.core.rate_limiter import (
    RateLimitRule,
    rate_limiter,
)

logger = logging.getLogger(__name__)


class RequestContextMiddleware(
    BaseHTTPMiddleware
):
    async def dispatch(
        self,
        request: Request,
        call_next: RequestResponseEndpoint,
    ) -> Response:
        incoming_request_id = request.headers.get(
            "X-Request-ID"
        )

        request_id = (
            incoming_request_id.strip()
            if incoming_request_id
            else str(uuid4())
        )

        request.state.request_id = request_id

        started_at = time.perf_counter()

        logger.info(
            "Request started | "
            "request_id=%s | method=%s | path=%s",
            request_id,
            request.method,
            request.url.path,
        )

        response = await call_next(request)

        duration_ms = (
            time.perf_counter() - started_at
        ) * 1000

        response.headers["X-Request-ID"] = (
            request_id
        )

        logger.info(
            "Request completed | "
            "request_id=%s | status=%s | "
            "duration_ms=%.2f",
            request_id,
            response.status_code,
            duration_ms,
        )

        return response


class RateLimitMiddleware(
    BaseHTTPMiddleware
):
    """
    Apply lightweight application-level rate limits
    to sensitive and expensive endpoints.
    """

    async def dispatch(
        self,
        request: Request,
        call_next: RequestResponseEndpoint,
    ) -> Response:
        if not settings.rate_limit_enabled:
            return await call_next(request)

        rule = self._get_rule(request)

        if rule is None:
            return await call_next(request)

        client_key = self._get_client_key(
            request
        )

        limiter_key = (
            f"{rule['name']}:{client_key}"
        )

        allowed, retry_after = (
            await rate_limiter.check(
                key=limiter_key,
                rule=RateLimitRule(
                    requests=rule["requests"],
                    window_seconds=(
                        settings.rate_limit_window_seconds
                    ),
                ),
            )
        )

        if allowed:
            return await call_next(request)

        request_id = getattr(
            request.state,
            "request_id",
            "unknown",
        )

        return JSONResponse(
            status_code=429,
            content=create_error_content(
                code="rate_limit_exceeded",
                message=(
                    "Too many requests. "
                    "Please try again shortly."
                ),
                request_id=request_id,
                details={
                    "retry_after": retry_after,
                },
            ),
            headers={
                "Retry-After": str(
                    retry_after
                ),
                "X-Request-ID": request_id,
            },
        )

    @staticmethod
    def _get_client_key(
        request: Request,
    ) -> str:
        """
        Use the remote address as the initial limiter
        identity.

        Authenticated user-based limiting can replace
        this for AI endpoints later.
        """

        if request.client:
            return request.client.host

        return "unknown"

    @staticmethod
    def _get_rule(
        request: Request,
    ) -> dict | None:
        if request.method != "POST":
            return None

        path = request.url.path

        rules = {
            "/api/v1/auth/login": {
                "name": "login",
                "requests": (
                    settings.rate_limit_login_requests
                ),
            },
            "/api/v1/auth/register": {
                "name": "register",
                "requests": (
                    settings.rate_limit_register_requests
                ),
            },
            "/api/v1/auth/refresh": {
                "name": "refresh",
                "requests": (
                    settings.rate_limit_refresh_requests
                ),
            },
            # "/api/v1/chat": {
            #     "name": "chat",
            #     "requests": (
            #         settings.rate_limit_chat_requests
            #     ),
            # },
            # "/api/v1/chat/stream": {
            #     "name": "chat",
            #     "requests": (
            #         settings.rate_limit_chat_requests
            #     ),
            # },
        }

        return rules.get(path)