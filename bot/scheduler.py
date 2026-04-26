"""Schedule periodic research cycles."""

import logging

import tweepy
from apscheduler.schedulers.blocking import BlockingScheduler

from bot.analytics import record_snapshot
from bot.config import Config

logger = logging.getLogger(__name__)


def create_scheduler(
    client: tweepy.Client,
    my_user_id: str,
) -> BlockingScheduler:
    """Create and configure the bot scheduler with research jobs."""
    scheduler = BlockingScheduler()

    # Import here to avoid circular imports
    from bot.main import run_research

    scheduler.add_job(
        run_research,
        "interval",
        minutes=Config.ENGAGE_INTERVAL_MINUTES,
        id="research",
        name="Trend research cycle",
    )

    scheduler.add_job(
        record_snapshot,
        "interval",
        minutes=Config.ANALYTICS_INTERVAL_MINUTES,
        args=[client],
        id="analytics",
        name="Analytics snapshot",
    )

    logger.info(
        "Scheduler configured: research every %dm, analytics every %dm",
        Config.ENGAGE_INTERVAL_MINUTES,
        Config.ANALYTICS_INTERVAL_MINUTES,
    )
    return scheduler
