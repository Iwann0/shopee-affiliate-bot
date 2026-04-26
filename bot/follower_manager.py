"""Smart follow/unfollow strategy for organic growth."""

import json
import logging
import os
import time

import tweepy

from bot.config import Config
from bot.rate_limiter import RateLimiter

logger = logging.getLogger(__name__)

FOLLOW_LOG_FILE = "follow_log.json"


def _load_follow_log() -> dict[str, float]:
    if os.path.exists(FOLLOW_LOG_FILE):
        with open(FOLLOW_LOG_FILE) as f:
            return json.load(f)
    return {}


def _save_follow_log(log: dict[str, float]) -> None:
    with open(FOLLOW_LOG_FILE, "w") as f:
        json.dump(log, f, indent=2)


def follow_relevant_users(
    client: tweepy.Client,
    limiter: RateLimiter,
    my_user_id: str,
) -> int:
    """Follow users who engage with niche content."""
    followed = 0
    follow_log = _load_follow_log()

    # Check following ratio
    me = client.get_me(user_fields=["public_metrics"])
    if me.data and me.data.public_metrics:
        metrics = me.data.public_metrics
        followers = metrics.get("followers_count", 0)
        following = metrics.get("following_count", 0)
        if followers > 0 and following / followers > Config.MAX_FOLLOWING_RATIO:
            logger.info(
                "Following ratio too high (%.1f), skipping follows",
                following / followers,
            )
            return 0

    for keyword in Config.NICHE_KEYWORDS[:3]:
        if not limiter.can_act("follow", Config.MAX_FOLLOWS_PER_HOUR):
            break

        try:
            query = f"{keyword} -is:retweet lang:en"
            resp = client.search_recent_tweets(
                query=query,
                max_results=10,
                tweet_fields=["author_id"],
                expansions=["author_id"],
                user_fields=["public_metrics"],
            )
            if not resp.includes or "users" not in resp.includes:
                continue

            for user in resp.includes["users"]:
                user_id_str = str(user.id)
                if user_id_str == my_user_id or user_id_str in follow_log:
                    continue

                if not user.public_metrics:
                    continue
                if user.public_metrics.get("followers_count", 0) < Config.ENGAGEMENT_MIN_FOLLOWERS:
                    continue

                if limiter.try_act("follow", Config.MAX_FOLLOWS_PER_HOUR):
                    try:
                        client.follow_user(user.id)
                        follow_log[user_id_str] = time.time()
                        followed += 1
                        logger.info("Followed @%s (%s)", user.username, user.id)
                    except tweepy.TweepyException as e:
                        logger.warning("Failed to follow %s: %s", user.id, e)

        except tweepy.TweepyException as e:
            logger.warning("Error searching for users: %s", e)

    _save_follow_log(follow_log)
    logger.info("Followed %d new users", followed)
    return followed


def unfollow_non_followers(
    client: tweepy.Client,
    limiter: RateLimiter,
    my_user_id: str,
) -> int:
    """Unfollow users who haven't followed back after UNFOLLOW_AFTER_DAYS."""
    unfollowed = 0
    follow_log = _load_follow_log()
    now = time.time()
    cutoff = Config.UNFOLLOW_AFTER_DAYS * 86400

    users_to_check = {
        uid: ts
        for uid, ts in follow_log.items()
        if now - ts > cutoff
    }

    if not users_to_check:
        logger.info("No users eligible for unfollow check")
        return 0

    # Get current followers
    try:
        followers_resp = client.get_users_followers(
            id=my_user_id,
            max_results=1000,
            user_fields=["id"],
        )
        follower_ids = set()
        if followers_resp.data:
            follower_ids = {str(u.id) for u in followers_resp.data}
    except tweepy.TweepyException as e:
        logger.warning("Failed to get followers: %s", e)
        return 0

    for user_id, _ts in users_to_check.items():
        if user_id in follower_ids:
            continue

        if not limiter.can_act("follow", Config.MAX_FOLLOWS_PER_HOUR):
            break

        try:
            client.unfollow_user(int(user_id))
            limiter.record("follow")
            del follow_log[user_id]
            unfollowed += 1
            logger.info("Unfollowed user %s (didn't follow back)", user_id)
        except tweepy.TweepyException as e:
            logger.warning("Failed to unfollow %s: %s", user_id, e)

    _save_follow_log(follow_log)
    logger.info("Unfollowed %d non-followers", unfollowed)
    return unfollowed
