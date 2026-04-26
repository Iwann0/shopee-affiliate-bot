"""
Main entry point for Shopee Affiliate Bot.
Combines all 3 components with APScheduler for automated scheduling.

Schedule (WIB = UTC+7):
  - 06:00 WIB (23:00 UTC prev day): Run scraper + content generator
  - 07:00 WIB (00:00 UTC): Post tweet
  - 12:00 WIB (05:00 UTC): Post tweet
  - 18:00 WIB (11:00 UTC): Post tweet
  - 21:00 WIB (14:00 UTC): Post tweet
"""

import os
import sys
import signal
import logging
from datetime import datetime, timezone

from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.cron import CronTrigger

from shopee_scraper import run_scraper
from content_generator import run_generator
from twitter_poster import post_next_tweet

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)


def daily_scrape_and_generate():
    """Run scraper and content generator (daily at 06:00 WIB / 23:00 UTC)."""
    logger.info("=" * 60)
    logger.info("DAILY JOB: Scraping products and generating content...")
    try:
        saved = run_scraper()
        logger.info("Scraper finished. %d products saved.", saved)
    except Exception as e:
        logger.error("Scraper failed: %s", e)

    try:
        generated = run_generator()
        logger.info("Generator finished. %d tweets generated.", generated)
    except Exception as e:
        logger.error("Generator failed: %s", e)


def scheduled_post():
    """Post next tweet (runs at 07:00, 12:00, 18:00, 21:00 WIB)."""
    logger.info("=" * 60)
    logger.info("SCHEDULED POST: Posting next tweet...")
    try:
        result = post_next_tweet()
        if result:
            logger.info("Tweet posted successfully!")
        else:
            logger.info("No tweet to post or posting failed.")
    except Exception as e:
        logger.error("Posting failed: %s", e)


def manual_run():
    """Run all components manually (for testing / manual trigger)."""
    logger.info("Manual run triggered")
    daily_scrape_and_generate()
    scheduled_post()


def main():
    """Main function — start the scheduler."""
    logger.info("=" * 60)
    logger.info("Shopee Affiliate Bot starting...")
    logger.info("Current UTC time: %s", datetime.now(timezone.utc).isoformat())

    # Handle manual run mode
    if len(sys.argv) > 1 and sys.argv[1] == "--run-now":
        manual_run()
        return

    # Run scraper + generator immediately on startup
    daily_scrape_and_generate()

    scheduler = BlockingScheduler()

    # Daily scrape + generate at 06:00 WIB = 23:00 UTC (previous day)
    scheduler.add_job(
        daily_scrape_and_generate,
        CronTrigger(hour=23, minute=0, timezone="UTC"),
        id="daily_scrape",
        name="Daily Scrape & Generate (06:00 WIB)",
        misfire_grace_time=3600,
    )

    # Tweet posting schedule (WIB → UTC)
    post_hours_utc = [0, 5, 11, 14]  # 07:00, 12:00, 18:00, 21:00 WIB
    for hour in post_hours_utc:
        scheduler.add_job(
            scheduled_post,
            CronTrigger(hour=hour, minute=0, timezone="UTC"),
            id=f"post_{hour}utc",
            name=f"Post Tweet ({hour}:00 UTC)",
            misfire_grace_time=3600,
        )

    # Graceful shutdown
    def shutdown(signum, frame):
        logger.info("Shutting down scheduler...")
        scheduler.shutdown(wait=False)
        sys.exit(0)

    signal.signal(signal.SIGTERM, shutdown)
    signal.signal(signal.SIGINT, shutdown)

    logger.info("Scheduler started. Jobs scheduled:")
    try:
        for job in scheduler.get_jobs():
            logger.info("  - %s", job.name)
    except Exception as e:
        logger.warning("Could not list jobs: %s", e)

    try:
        scheduler.start()
    except (KeyboardInterrupt, SystemExit):
        logger.info("Bot stopped.")


if __name__ == "__main__":
    main()
