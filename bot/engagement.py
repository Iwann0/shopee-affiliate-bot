"""Auto-engagement: like, retweet, and reply to relevant tweets."""

import logging
import random

import tweepy

from bot.config import Config
from bot.rate_limiter import RateLimiter
from bot.trending import search_niche_tweets

logger = logging.getLogger(__name__)

REPLY_TEMPLATES = [
    "Great point! {keyword} is really evolving fast.",
    "Interesting take on {keyword}! What are your thoughts on where it's headed?",
    "This is a solid perspective on {keyword}. Thanks for sharing!",
    "Really insightful thread about {keyword}. Following for more!",
    "Couldn't agree more about {keyword}. The future looks exciting!",
    "Well said! {keyword} is one of the most interesting topics right now.",
    "Love this take on {keyword}. Would love to hear more thoughts on this.",
    "Thanks for the insights on {keyword}! Definitely food for thought.",
]


def engage_with_trending(
    client: tweepy.Client,
    limiter: RateLimiter,
) -> dict[str, int]:
    """Find trending tweets and engage with them (like, retweet, reply)."""
    stats = {"liked": 0, "retweeted": 0, "replied": 0, "skipped": 0}
    tweets = search_niche_tweets(client)

    if not tweets:
        logger.info("No tweets found to engage with")
        return stats

    for tweet in tweets:
        if not any(
            [
                limiter.can_act("like", Config.MAX_LIKES_PER_HOUR),
                limiter.can_act("retweet", Config.MAX_RETWEETS_PER_HOUR),
                limiter.can_act("reply", Config.MAX_REPLIES_PER_HOUR),
            ]
        ):
            logger.info("All rate limits reached, stopping engagement")
            break

        # Like
        if limiter.try_act("like", Config.MAX_LIKES_PER_HOUR):
            try:
                client.like(tweet.id)
                stats["liked"] += 1
                logger.info("Liked tweet %s", tweet.id)
            except tweepy.TweepyException as e:
                logger.warning("Failed to like tweet %s: %s", tweet.id, e)

        # Retweet (50% chance to avoid being too aggressive)
        if random.random() < 0.5 and limiter.try_act("retweet", Config.MAX_RETWEETS_PER_HOUR):
            try:
                client.retweet(tweet.id)
                stats["retweeted"] += 1
                logger.info("Retweeted tweet %s", tweet.id)
            except tweepy.TweepyException as e:
                logger.warning("Failed to retweet %s: %s", tweet.id, e)

        # Reply (20% chance to keep it organic)
        if random.random() < 0.2 and limiter.try_act("reply", Config.MAX_REPLIES_PER_HOUR):
            try:
                keyword = random.choice(Config.NICHE_KEYWORDS)
                reply_text = random.choice(REPLY_TEMPLATES).format(keyword=keyword)
                client.create_tweet(text=reply_text, in_reply_to_tweet_id=tweet.id)
                stats["replied"] += 1
                logger.info("Replied to tweet %s", tweet.id)
            except tweepy.TweepyException as e:
                logger.warning("Failed to reply to %s: %s", tweet.id, e)

    logger.info(
        "Engagement round complete: liked=%d, retweeted=%d, replied=%d, skipped=%d",
        stats["liked"],
        stats["retweeted"],
        stats["replied"],
        stats["skipped"],
    )
    return stats
