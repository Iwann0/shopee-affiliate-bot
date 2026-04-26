"""Track and report growth analytics."""

import json
import logging
import os
from datetime import datetime, timezone

import tweepy

from bot.config import Config

logger = logging.getLogger(__name__)


def _load_analytics() -> list[dict]:
    if os.path.exists(Config.ANALYTICS_FILE):
        with open(Config.ANALYTICS_FILE) as f:
            return json.load(f)
    return []


def _save_analytics(data: list[dict]) -> None:
    with open(Config.ANALYTICS_FILE, "w") as f:
        json.dump(data, f, indent=2)


def record_snapshot(client: tweepy.Client) -> dict:
    """Take a snapshot of the current account metrics."""
    resp = client.get_me(user_fields=["public_metrics"])
    if not resp.data or not resp.data.public_metrics:
        logger.warning("Could not fetch account metrics")
        return {}

    metrics = resp.data.public_metrics
    snapshot = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "followers": metrics.get("followers_count", 0),
        "following": metrics.get("following_count", 0),
        "tweets": metrics.get("tweet_count", 0),
        "listed": metrics.get("listed_count", 0),
    }

    history = _load_analytics()
    history.append(snapshot)

    # Keep last 30 days of data (~720 snapshots at 1/hr)
    if len(history) > 720:
        history = history[-720:]

    _save_analytics(history)
    logger.info(
        "Analytics snapshot: followers=%d, following=%d, tweets=%d",
        snapshot["followers"],
        snapshot["following"],
        snapshot["tweets"],
    )
    return snapshot


def get_growth_summary() -> dict:
    """Calculate growth metrics from stored snapshots."""
    history = _load_analytics()
    if len(history) < 2:
        return {"message": "Not enough data yet. Check back after a few snapshots."}

    latest = history[-1]
    oldest = history[0]

    follower_growth = latest["followers"] - oldest["followers"]
    tweet_growth = latest["tweets"] - oldest["tweets"]
    days = max(
        1,
        (
            datetime.fromisoformat(latest["timestamp"])
            - datetime.fromisoformat(oldest["timestamp"])
        ).days,
    )

    return {
        "period_days": days,
        "total_snapshots": len(history),
        "current_followers": latest["followers"],
        "follower_growth": follower_growth,
        "avg_followers_per_day": round(follower_growth / days, 1),
        "current_following": latest["following"],
        "tweets_posted": tweet_growth,
        "following_ratio": (
            round(latest["following"] / latest["followers"], 2)
            if latest["followers"] > 0
            else 0
        ),
    }
