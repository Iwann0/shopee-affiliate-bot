"""Bot configuration loaded from environment variables."""

import os

from dotenv import load_dotenv

load_dotenv()


class Config:
    # Twitter API v2 credentials
    TWITTER_API_KEY: str = os.environ.get("TWITTER_API_KEY", "")
    TWITTER_API_SECRET: str = os.environ.get("TWITTER_API_SECRET", "")
    TWITTER_ACCESS_TOKEN: str = os.environ.get("TWITTER_ACCESS_TOKEN", "")
    TWITTER_ACCESS_TOKEN_SECRET: str = os.environ.get("TWITTER_ACCESS_TOKEN_SECRET", "")
    TWITTER_BEARER_TOKEN: str = os.environ.get("TWITTER_BEARER_TOKEN", "")

    # Engagement settings
    MAX_LIKES_PER_HOUR: int = int(os.environ.get("MAX_LIKES_PER_HOUR", "15"))
    MAX_RETWEETS_PER_HOUR: int = int(os.environ.get("MAX_RETWEETS_PER_HOUR", "10"))
    MAX_REPLIES_PER_HOUR: int = int(os.environ.get("MAX_REPLIES_PER_HOUR", "5"))
    MAX_FOLLOWS_PER_HOUR: int = int(os.environ.get("MAX_FOLLOWS_PER_HOUR", "10"))

    # Content settings
    NICHE_KEYWORDS: list[str] = [
        kw.strip()
        for kw in os.environ.get(
            "NICHE_KEYWORDS", "tech,programming,AI,startup,crypto"
        ).split(",")
    ]
    ENGAGEMENT_MIN_FOLLOWERS: int = int(os.environ.get("ENGAGEMENT_MIN_FOLLOWERS", "100"))
    ENGAGEMENT_MIN_LIKES: int = int(os.environ.get("ENGAGEMENT_MIN_LIKES", "5"))

    # Follow/unfollow settings
    UNFOLLOW_AFTER_DAYS: int = int(os.environ.get("UNFOLLOW_AFTER_DAYS", "3"))
    MAX_FOLLOWING_RATIO: float = float(os.environ.get("MAX_FOLLOWING_RATIO", "1.5"))

    # Scheduling intervals (minutes)
    ENGAGE_INTERVAL_MINUTES: int = int(os.environ.get("ENGAGE_INTERVAL_MINUTES", "30"))
    POST_INTERVAL_MINUTES: int = int(os.environ.get("POST_INTERVAL_MINUTES", "120"))
    FOLLOW_INTERVAL_MINUTES: int = int(os.environ.get("FOLLOW_INTERVAL_MINUTES", "60"))
    UNFOLLOW_INTERVAL_MINUTES: int = int(os.environ.get("UNFOLLOW_INTERVAL_MINUTES", "360"))
    ANALYTICS_INTERVAL_MINUTES: int = int(os.environ.get("ANALYTICS_INTERVAL_MINUTES", "720"))

    # Analytics
    ANALYTICS_FILE: str = os.environ.get("ANALYTICS_FILE", "analytics.json")

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
