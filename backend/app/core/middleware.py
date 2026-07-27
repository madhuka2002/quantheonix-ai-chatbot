import logging
import time
from uuid import uuid4

from fastapi import Request
from starlette.middleware.base import (
    BaseHTTPMiddleware,
    RequestResponseEndpoint,
)
from starlette.responses import Response


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