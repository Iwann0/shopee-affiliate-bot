"""Generate and post original tweets about trending topics."""

import logging
import random

import tweepy

from bot.rate_limiter import RateLimiter
from bot.trending import get_trending_keywords

logger = logging.getLogger(__name__)

TWEET_TEMPLATES = [
    (
        "Hot take: {topic} is going to change everything"
        " in the next 5 years. Here's why...\n\nThread incoming"
    ),
    (
        "Everyone's talking about {topic} today. My thoughts:\n\n"
        "It's still early. If you're not paying attention, you're missing out."
    ),
    (
        "The future of {topic} is brighter than most people think.\n\n"
        "Here's what I'm watching closely..."
    ),
    (
        "{topic} update:\n\nThe momentum is building."
        " This is the kind of shift that creates massive opportunities."
    ),
    (
        "Why {topic} matters right now:\n\n"
        "1. Innovation is accelerating\n"
        "2. Adoption is growing\n"
        "3. The market is shifting\n\n"
        "Don't sleep on this."
    ),
    (
        "Quick thought on {topic}:\n\n"
        "We're at an inflection point. The next 12 months will be pivotal."
    ),
    (
        "If you're interested in {topic}, now is the time to go deep.\n\n"
        "The opportunity window won't stay open forever."
    ),
    (
        "3 things about {topic} that nobody is talking about:\n\n"
        "1. The infrastructure is maturing\n"
        "2. New players are entering\n"
        "3. The rules are changing"
    ),
    (
        "My prediction for {topic}:\n\n"
        "We'll see a major breakthrough within the next year. Bookmark this."
    ),
    (
        "{topic} is trending and for good reason.\n\n"
        "This is one of those rare moments where paying attention actually pays off."
    ),
]

HASHTAG_MAP: dict[str, list[str]] = {
    "tech": ["#Tech", "#Innovation", "#FutureTech"],
    "programming": ["#Coding", "#Developer", "#Programming"],
    "AI": ["#AI", "#ArtificialIntelligence", "#MachineLearning"],
    "startup": ["#Startup", "#Entrepreneurship", "#Business"],
    "crypto": ["#Crypto", "#Bitcoin", "#Web3"],
}


def _get_hashtags(topic: str) -> str:
    for key, tags in HASHTAG_MAP.items():
        if key.lower() in topic.lower():
            return " ".join(random.sample(tags, min(2, len(tags))))
    return "#Trending"


def post_trending_tweet(
    client: tweepy.Client,
    limiter: RateLimiter,
) -> bool:
    """Generate and post a tweet about a trending topic."""
    if not limiter.can_act("post", 3):  # max 3 original posts per hour
        logger.info("Post rate limit reached")
        return False

    trending = get_trending_keywords(client)
    topic = random.choice(trending)

    tweet_text = random.choice(TWEET_TEMPLATES).format(topic=topic)
    hashtags = _get_hashtags(topic)
    full_tweet = f"{tweet_text}\n\n{hashtags}"

    # Ensure tweet is within 280 chars
    if len(full_tweet) > 280:
        full_tweet = full_tweet[:277] + "..."

    try:
        client.create_tweet(text=full_tweet)
        limiter.record("post")
        logger.info("Posted tweet about '%s'", topic)
        return True
    except tweepy.TweepyException as e:
        logger.error("Failed to post tweet: %s", e)
        return False
