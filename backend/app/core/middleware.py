import logging
import re
import time
from uuid import uuid4

from fastapi import Request
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.base import (
    BaseHTTPMiddleware,
    RequestResponseEndpoint,
)
from starlette.responses import (
    JSONResponse,
    Response,
)
from starlette.types import (
    ASGIApp,
    Receive,
    Scope,
    Send,
)
from app.core.config import settings
from app.core.exception_handlers import create_error_content
from app.core.rate_limiter import (
    RateLimitRule,
    rate_limiter,
)

logger = logging.getLogger(__name__)


class RouteAwareCORSMiddleware:
    """Apply a separate, credential-free policy to public widget routes."""

    _public_config_path = re.compile(
        r"^/api/v1/public/assistants/[^/]+/config$"
    )
    _public_chat_path = "/api/v1/public/chat/stream"

    def __init__(
        self,
        app: ASGIApp,
        *,
        dashboard_origins: list[str],
    ) -> None:
        common_options = {
            "allow_origins": ["*"],
            "allow_credentials": False,
            "allow_headers": [
                "Accept",
                "Content-Type",
            ],
            "expose_headers": [
                "X-Request-ID",
            ],
        }

        self._public_config_cors = CORSMiddleware(
            app,
            allow_methods=["GET"],
            **common_options,
        )
        self._public_chat_cors = CORSMiddleware(
            app,
            allow_methods=["POST"],
            **common_options,
        )
        self._dashboard_cors = CORSMiddleware(
            app,
            allow_origins=dashboard_origins,
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
            expose_headers=["X-Request-ID"],
        )

    async def __call__(
        self,
        scope: Scope,
        receive: Receive,
        send: Send,
    ) -> None:
        if scope["type"] != "http":
            await self._dashboard_cors(
                scope,
                receive,
                send,
            )
            return

        path = scope.get("path", "")

        if self._public_config_path.fullmatch(path):
            cors_app = self._public_config_cors
        elif path == self._public_chat_path:
            cors_app = self._public_chat_cors
        else:
            cors_app = self._dashboard_cors

        await cors_app(
            scope,
            receive,
            send,
        )


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
