from typing import Annotated

from fastapi import Depends

from app.api.dependencies import CurrentUser
from app.core.config import settings
from app.core.exceptions import (
    RateLimitExceededError,
)
from app.core.rate_limiter import (
    RateLimitRule,
    rate_limiter,
)


async def enforce_chat_rate_limit(
    current_user: CurrentUser,
) -> None:
    """
    Apply the AI request limit per authenticated user.
    """

    key = (
        f"chat:user:{current_user.id}"
    )

    allowed, retry_after = (
        await rate_limiter.check(
            key=key,
            rule=RateLimitRule(
                requests=(
                    settings
                    .rate_limit_chat_requests
                ),
                window_seconds=(
                    settings
                    .rate_limit_window_seconds
                ),
            ),
        )
    )

    if not allowed:
        raise RateLimitExceededError(
            retry_after=retry_after,
        )


ChatRateLimit = Annotated[
    None,
    Depends(enforce_chat_rate_limit),
]