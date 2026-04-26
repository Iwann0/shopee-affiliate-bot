"""Simple in-memory rate limiter to stay within Twitter API limits."""

import logging
import time
from collections import defaultdict

logger = logging.getLogger(__name__)


class RateLimiter:
    def __init__(self) -> None:
        self._actions: dict[str, list[float]] = defaultdict(list)

    def _clean_old(self, action: str, window_seconds: int = 3600) -> None:
        now = time.time()
        self._actions[action] = [
            ts for ts in self._actions[action] if now - ts < window_seconds
        ]

    def can_act(self, action: str, max_per_hour: int) -> bool:
        self._clean_old(action)
        return len(self._actions[action]) < max_per_hour

    def record(self, action: str) -> None:
        self._actions[action].append(time.time())

    def remaining(self, action: str, max_per_hour: int) -> int:
        self._clean_old(action)
        return max(0, max_per_hour - len(self._actions[action]))

    def try_act(self, action: str, max_per_hour: int) -> bool:
        if self.can_act(action, max_per_hour):
            self.record(action)
            return True
        logger.debug("Rate limit reached for %s (%d/hr)", action, max_per_hour)
        return False
