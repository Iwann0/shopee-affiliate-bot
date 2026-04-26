"""Twitter Growth Bot - main entry point."""

import logging
import sys

from bot.analytics import record_snapshot
from bot.config import Config
from bot.content import post_trending_tweet
from bot.engagement import engage_with_trending
from bot.rate_limiter import RateLimiter
from bot.scheduler import create_scheduler
from bot.twitter_client import create_client, get_me

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)
logger = logging.getLogger(__name__)


def main() -> None:
    logger.info("Starting Twitter Growth Bot...")

    # Validate config
    errors = Config.validate()
    if errors:
        for err in errors:
            logger.error("Config error: %s", err)
        sys.exit(1)

    # Create client and verify credentials
    client = create_client()
    try:
        me = get_me(client)
        logger.info(
            "Authenticated as @%s (followers: %d, following: %d)",
            me.username,
            me.public_metrics.get("followers_count", 0) if me.public_metrics else 0,
            me.public_metrics.get("following_count", 0) if me.public_metrics else 0,
        )
    except Exception as e:
        logger.error("Failed to authenticate: %s", e)
        sys.exit(1)

    my_user_id = str(me.id)
    limiter = RateLimiter()

    # Run initial tasks
    logger.info("Running initial engagement round...")
    engage_with_trending(client, limiter)

    logger.info("Posting initial trending tweet...")
    post_trending_tweet(client, limiter)

    logger.info("Recording initial analytics snapshot...")
    record_snapshot(client)

    # Start scheduler for recurring tasks
    logger.info("Starting scheduler...")
    logger.info(
        "Schedule: engage every %dm, post every %dm, follow every %dm, "
        "unfollow every %dm, analytics every %dm",
        Config.ENGAGE_INTERVAL_MINUTES,
        Config.POST_INTERVAL_MINUTES,
        Config.FOLLOW_INTERVAL_MINUTES,
        Config.UNFOLLOW_INTERVAL_MINUTES,
        Config.ANALYTICS_INTERVAL_MINUTES,
    )

    scheduler = create_scheduler(client, my_user_id)
    try:
        scheduler.start()
    except (KeyboardInterrupt, SystemExit):
        logger.info("Shutting down...")
        scheduler.shutdown()


if __name__ == "__main__":
    main()
