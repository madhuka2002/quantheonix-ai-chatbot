import pytest

from app.core.rate_limiter import (
    InMemoryRateLimiter,
    RateLimitRule,
)


@pytest.mark.asyncio
async def test_rate_limiter_allows_requests_under_limit():
    limiter = InMemoryRateLimiter()

    rule = RateLimitRule(
        requests=3,
        window_seconds=60,
    )

    for index in range(3):
        allowed, retry_after = (
            await limiter.check(
                key="test-user",
                rule=rule,
            )
        )

        assert allowed is True
        assert retry_after == 0


@pytest.mark.asyncio
async def test_rate_limiter_blocks_request_over_limit():
    limiter = InMemoryRateLimiter()

    rule = RateLimitRule(
        requests=2,
        window_seconds=60,
    )

    await limiter.check(
        key="test-user",
        rule=rule,
    )

    await limiter.check(
        key="test-user",
        rule=rule,
    )

    allowed, retry_after = (
        await limiter.check(
            key="test-user",
            rule=rule,
        )
    )

    assert allowed is False
    assert retry_after > 0


@pytest.mark.asyncio
async def test_rate_limiter_separates_clients():
    limiter = InMemoryRateLimiter()

    rule = RateLimitRule(
        requests=1,
        window_seconds=60,
    )

    first_allowed, _ = (
        await limiter.check(
            key="user-a",
            rule=rule,
        )
    )

    second_allowed, _ = (
        await limiter.check(
            key="user-b",
            rule=rule,
        )
    )

    assert first_allowed is True
    assert second_allowed is True