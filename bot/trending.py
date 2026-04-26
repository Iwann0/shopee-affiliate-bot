"""Discover trending topics and find engaging tweets."""

import logging
import random

import tweepy

from bot.config import Config

logger = logging.getLogger(__name__)

# Global WOEID for worldwide trends
WOEID_WORLDWIDE = 1


def search_niche_tweets(
    client: tweepy.Client,
    max_results_per_keyword: int = 10,
) -> list[tweepy.Tweet]:
    """Search for recent popular tweets matching niche keywords."""
    all_tweets: list[tweepy.Tweet] = []
    keywords = Config.NICHE_KEYWORDS

    for keyword in keywords:
        try:
            query = f"{keyword} -is:retweet -is:reply lang:en"
            resp = client.search_recent_tweets(
                query=query,
                max_results=max_results_per_keyword,
                tweet_fields=["public_metrics", "author_id", "created_at"],
                sort_order="relevancy",
            )
            if resp.data:
                tweets = [
                    t
                    for t in resp.data
                    if t.public_metrics
                    and t.public_metrics.get("like_count", 0) >= Config.ENGAGEMENT_MIN_LIKES
                ]
                all_tweets.extend(tweets)
                logger.info("Found %d tweets for keyword '%s'", len(tweets), keyword)
        except tweepy.TweepyException as e:
            logger.warning("Error searching for '%s': %s", keyword, e)

    random.shuffle(all_tweets)
    return all_tweets


def get_trending_keywords(client: tweepy.Client) -> list[str]:
    """Get currently trending keywords from Twitter.

    Falls back to niche keywords if trends endpoint is unavailable (requires
    elevated API access).
    """
    try:
        resp = client.get_trending_topics(id=WOEID_WORLDWIDE)
        if resp and hasattr(resp, "data") and resp.data:
            return [trend["name"] for trend in resp.data[:20]]
    except (tweepy.TweepyException, AttributeError) as e:
        logger.info("Trends endpoint unavailable (%s), using niche keywords", e)

    return Config.NICHE_KEYWORDS
