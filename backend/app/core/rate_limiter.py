import asyncio
import time
from collections import defaultdict, deque
from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class RateLimitRule:
    requests: int
    window_seconds: int


class InMemoryRateLimiter:
    """
    Small in-memory sliding-window rate limiter.

    Suitable for:
    - local development
    - testing
    - a single backend instance

    This should later be replaced by a shared store such
    as Redis when multiple backend instances are deployed.
    """

    def __init__(self) -> None:
        self._requests: dict[
            str,
            deque[float],
        ] = defaultdict(deque)

        self._lock = asyncio.Lock()

    async def check(
        self,
        *,
        key: str,
        rule: RateLimitRule,
    ) -> tuple[bool, int]:
        now = time.monotonic()

        window_start = (
            now - rule.window_seconds
        )

        async with self._lock:
            timestamps = self._requests[key]

            while (
                timestamps
                and timestamps[0] <= window_start
            ):
                timestamps.popleft()

            if len(timestamps) >= rule.requests:
                oldest_request = timestamps[0]

                retry_after = max(
                    1,
                    int(
                        rule.window_seconds
                        - (
                            now
                            - oldest_request
                        )
                    )
                    + 1,
                )

                return False, retry_after

            timestamps.append(now)

            return True, 0


rate_limiter = InMemoryRateLimiter()