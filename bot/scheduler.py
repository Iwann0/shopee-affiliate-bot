"""Job scheduler for periodic bot tasks."""

import logging

import tweepy
from apscheduler.schedulers.blocking import BlockingScheduler

from bot.analytics import get_growth_summary, record_snapshot
from bot.config import Config
from bot.content import post_trending_tweet
from bot.engagement import engage_with_trending
from bot.follower_manager import follow_relevant_users, unfollow_non_followers
from bot.rate_limiter import RateLimiter

logger = logging.getLogger(__name__)


def create_scheduler(
    client: tweepy.Client,
    my_user_id: str,
    limiter: RateLimiter,
) -> BlockingScheduler:
    """Create and configure the bot scheduler with all jobs."""
    scheduler = BlockingScheduler()

    # Engagement job - like, retweet, reply to trending tweets
    scheduler.add_job(
        engage_with_trending,
        "interval",
        minutes=Config.ENGAGE_INTERVAL_MINUTES,
        args=[client, limiter],
        id="engage",
        name="Engage with trending tweets",
        next_run_time=None,  # don't run immediately, main.py handles startup
    )

    # Content posting job - post original tweets
    scheduler.add_job(
        post_trending_tweet,
        "interval",
        minutes=Config.POST_INTERVAL_MINUTES,
        args=[client, limiter],
        id="post",
        name="Post trending content",
        next_run_time=None,
    )

    # Follow job - follow relevant users
    scheduler.add_job(
        follow_relevant_users,
        "interval",
        minutes=Config.FOLLOW_INTERVAL_MINUTES,
        args=[client, limiter, my_user_id],
        id="follow",
        name="Follow relevant users",
        next_run_time=None,
    )

    # Unfollow job - remove non-followers
    scheduler.add_job(
        unfollow_non_followers,
        "interval",
        minutes=Config.UNFOLLOW_INTERVAL_MINUTES,
        args=[client, limiter, my_user_id],
        id="unfollow",
        name="Unfollow non-followers",
        next_run_time=None,
    )

    # Analytics snapshot
    scheduler.add_job(
        record_snapshot,
        "interval",
        minutes=Config.ANALYTICS_INTERVAL_MINUTES,
        args=[client],
        id="analytics",
        name="Record analytics snapshot",
        next_run_time=None,
    )

    # Growth report (daily)
    def log_growth_report() -> None:
        summary = get_growth_summary()
        logger.info("Growth summary: %s", summary)

    scheduler.add_job(
        log_growth_report,
        "interval",
        hours=24,
        id="growth_report",
        name="Log growth report",
    )

    return scheduler
