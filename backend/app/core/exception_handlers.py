import logging
from typing import Any

from fastapi import (
    HTTPException,
    Request,
    status,
)
from fastapi.exceptions import (
    RequestValidationError,
)
from fastapi.responses import JSONResponse

from app.core.exceptions import (
    ApplicationError,
)


logger = logging.getLogger(__name__)


def get_request_id(request: Request) -> str:
    return getattr(
        request.state,
        "request_id",
        "unknown",
    )


def create_error_content(
    *,
    code: str,
    message: str,
    request_id: str,
    details: Any | None = None,
) -> dict[str, Any]:
    return {
        "error": {
            "code": code,
            "message": message,
            "request_id": request_id,
            "details": details,
        }
    }


async def application_error_handler(
    request: Request,
    exception: ApplicationError,
) -> JSONResponse:
    request_id = get_request_id(request)

    logger.warning(
        "Application error | "
        "request_id=%s | code=%s | message=%s",
        request_id,
        exception.code,
        exception.message,
    )

    return JSONResponse(
        status_code=exception.status_code,
        content=create_error_content(
            code=exception.code,
            message=exception.message,
            request_id=request_id,
            details=exception.details,
        ),
        headers={
            "X-Request-ID": request_id,
        },
    )


async def validation_error_handler(
    request: Request,
    exception: RequestValidationError,
) -> JSONResponse:
    request_id = get_request_id(request)

    validation_details = []

    for error in exception.errors():
        validation_details.append(
            {
                "location": list(
                    error.get("loc", [])
                ),
                "message": error.get(
                    "msg",
                    "Invalid value.",
                ),
                "type": error.get(
                    "type",
                    "validation_error",
                ),
            }
        )

    logger.info(
        "Request validation failed | "
        "request_id=%s | errors=%s",
        request_id,
        validation_details,
    )

    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content=create_error_content(
            code="VALIDATION_ERROR",
            message=(
                "The submitted request is invalid."
            ),
            request_id=request_id,
            details=validation_details,
        ),
        headers={
            "X-Request-ID": request_id,
        },
    )


async def http_exception_handler(
    request: Request,
    exception: HTTPException,
) -> JSONResponse:
    request_id = get_request_id(request)

    message = (
        exception.detail
        if isinstance(exception.detail, str)
        else "The request could not be completed."
    )

    return JSONResponse(
        status_code=exception.status_code,
        content=create_error_content(
            code="HTTP_ERROR",
            message=message,
            request_id=request_id,
            details=(
                None
                if isinstance(
                    exception.detail,
                    str,
                )
                else exception.detail
            ),
        ),
        headers={
            "X-Request-ID": request_id,
        },
    )


async def unhandled_exception_handler(
    request: Request,
    exception: Exception,
) -> JSONResponse:
    request_id = get_request_id(request)

    logger.exception(
        "Unhandled server error | "
        "request_id=%s | path=%s",
        request_id,
        request.url.path,
    )

    return JSONResponse(
        status_code=(
            status.HTTP_500_INTERNAL_SERVER_ERROR
        ),
        content=create_error_content(
            code="INTERNAL_SERVER_ERROR",
            message=(
                "An unexpected server error occurred."
            ),
            request_id=request_id,
        ),
        headers={
            "X-Request-ID": request_id,
        },
    )