"""Twitter Growth Bot — Trend Research & Content Intelligence Tool.

Finds rising trends, generates tweet drafts, and suggests accounts to follow.
Run with ``--dashboard`` to start the web UI, or without flags for CLI mode.
"""

import logging
import sys

from bot.accounts import (
    get_my_profile,
    suggest_accounts_to_follow,
    suggest_follow_strategy,
)
from bot.analytics import record_snapshot
from bot.config import Config
from bot.content import generate_tweet_drafts
from bot.scheduler import create_scheduler
from bot.trending import get_all_trends
from bot.twitter_client import create_client, get_me

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)
logger = logging.getLogger(__name__)

SEPARATOR = "=" * 70


def _print_section(title: str) -> None:
    print(f"\n{SEPARATOR}")
    print(f"  {title}")
    print(SEPARATOR)


def run_research() -> None:
    """Run a single research cycle: trends → drafts → account tips."""

    # 1. Gather trends
    _print_section("TRENDING TOPICS")
    trends = get_all_trends()

    # Twitter trends
    twitter_trends = trends.get("twitter_trends", [])
    if twitter_trends:
        print("\n📈 Twitter/X Trending Right Now:")
        for i, trend in enumerate(twitter_trends[:15], 1):
            print(f"  {i:2d}. {trend}")
    else:
        print("\n  (Could not fetch Twitter trends)")

    # Interest scores
    interest = trends.get("interest_scores", {})
    if interest:
        print("\n📊 Google Trends Interest Scores (0-100):")
        sorted_interest = sorted(interest.items(), key=lambda x: x[1], reverse=True)
        for kw, score in sorted_interest:
            bar = "█" * int(score / 5)
            print(f"  {kw:15s} {score:5.0f}  {bar}")

    # Rising queries
    rising = trends.get("rising_queries", {})
    if rising:
        print("\n🚀 Rising Search Queries:")
        for kw, queries in rising.items():
            if queries:
                print(f"\n  [{kw}]")
                for q in queries[:5]:
                    print(f"    • {q['query']} (+{q['value']}%)")

    # 2. Generate tweet drafts
    _print_section("TWEET DRAFTS (ready to copy-paste)")

    # Use trending topics as inspiration if available
    draft_topics = twitter_trends[:5] if twitter_trends else None
    drafts = generate_tweet_drafts(topics=draft_topics, count=5)

    for i, draft in enumerate(drafts, 1):
        print(f"\n--- Draft {i} ({draft['char_count']} chars) ---")
        print(draft["full_tweet"])

    # 3. Account follow suggestions
    _print_section("ACCOUNTS TO FOLLOW")
    suggestions = suggest_accounts_to_follow()
    for s in suggestions[:3]:
        print(f"\n🔍 Search: {s['search_query']}")
        print(f"   Strategy: {s['strategy']}")
        print("   Look for:")
        for acct_type in s["account_types"]:
            print(f"     • {acct_type}")


def main() -> None:
    logger.info("Starting Twitter Growth Research Bot...")

    # Validate config
    errors = Config.validate()
    if errors:
        for err in errors:
            logger.error("Config error: %s", err)
        sys.exit(1)

    # Authenticate
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

    # Show profile summary
    profile = get_my_profile(client)
    if profile:
        _print_section("YOUR PROFILE")
        print(f"  @{profile['username']}")
        print(f"  Followers: {profile['followers']}")
        print(f"  Following: {profile['following']}")
        print(f"  Tweets: {profile['tweets']}")

        tips = suggest_follow_strategy(profile)
        print("\n💡 Growth Tips:")
        for tip in tips:
            print(f"  • {tip}")

    # Run research
    run_research()

    # Record analytics snapshot
    record_snapshot(client)

    # Start scheduler for periodic research
    _print_section("SCHEDULER STARTED")
    print(f"  Research runs every {Config.ENGAGE_INTERVAL_MINUTES} minutes")
    print(f"  New drafts every {Config.POST_INTERVAL_MINUTES} minutes")
    print(f"  Analytics snapshot every {Config.ANALYTICS_INTERVAL_MINUTES} minutes")
    print("  Press Ctrl+C to stop\n")

    scheduler = create_scheduler(client, my_user_id)
    try:
        scheduler.start()
    except (KeyboardInterrupt, SystemExit):
        logger.info("Shutting down...")
        scheduler.shutdown()


if __name__ == "__main__":
    if "--dashboard" in sys.argv:
        from bot.dashboard import run_dashboard

        port = 5000
        for i, arg in enumerate(sys.argv):
            if arg == "--port" and i + 1 < len(sys.argv):
                port = int(sys.argv[i + 1])
        run_dashboard(port=port)
    else:
        main()
