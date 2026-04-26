"""Bot configuration loaded from environment variables."""

import os

from dotenv import load_dotenv

load_dotenv()


class Config:
    # Twitter API v2 credentials (needed for auth + analytics only)
    TWITTER_API_KEY: str = os.environ.get("TWITTER_API_KEY", "")
    TWITTER_API_SECRET: str = os.environ.get("TWITTER_API_SECRET", "")
    TWITTER_ACCESS_TOKEN: str = os.environ.get("TWITTER_ACCESS_TOKEN", "")
    TWITTER_ACCESS_TOKEN_SECRET: str = os.environ.get(
        "TWITTER_ACCESS_TOKEN_SECRET", ""
    )
    TWITTER_BEARER_TOKEN: str = os.environ.get("TWITTER_BEARER_TOKEN", "")

    # Niche keywords for trend research
    NICHE_KEYWORDS: list[str] = [
        kw.strip()
        for kw in os.environ.get(
            "NICHE_KEYWORDS", "tech,programming,AI,startup,crypto"
        ).split(",")
    ]

    # Scheduling intervals (minutes)
    ENGAGE_INTERVAL_MINUTES: int = int(
        os.environ.get("ENGAGE_INTERVAL_MINUTES", "30")
    )
    POST_INTERVAL_MINUTES: int = int(
        os.environ.get("POST_INTERVAL_MINUTES", "120")
    )
    ANALYTICS_INTERVAL_MINUTES: int = int(
        os.environ.get("ANALYTICS_INTERVAL_MINUTES", "720")
    )

    # Analytics
    ANALYTICS_FILE: str = os.environ.get("ANALYTICS_FILE", "analytics.json")

    # Tweet draft count per research cycle
    DRAFT_COUNT: int = int(os.environ.get("DRAFT_COUNT", "5"))

    @classmethod
    def validate(cls) -> list[str]:
        errors = []
        if not cls.TWITTER_API_KEY:
            errors.append("TWITTER_API_KEY is required")
        if not cls.TWITTER_API_SECRET:
            errors.append("TWITTER_API_SECRET is required")
        if not cls.TWITTER_ACCESS_TOKEN:
            errors.append("TWITTER_ACCESS_TOKEN is required")
        if not cls.TWITTER_ACCESS_TOKEN_SECRET:
            errors.append("TWITTER_ACCESS_TOKEN_SECRET is required")
        if not cls.TWITTER_BEARER_TOKEN:
            errors.append("TWITTER_BEARER_TOKEN is required")
        return errors
