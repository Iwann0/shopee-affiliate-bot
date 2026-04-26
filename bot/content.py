"""Generate tweet drafts for manual posting based on trending topics."""

import logging
import random
import urllib.parse

from bot.config import Config

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


def _get_image_url(topic: str, width: int = 800, height: int = 418) -> str:
    """Build a Lorem Picsum URL seeded by topic for a consistent image.

    Returns a direct image URL sized for Twitter cards (roughly 1.91:1).
    Each topic always maps to the same image via the seed parameter.
    """
    seed = urllib.parse.quote(topic.lower().strip(), safe="")
    return f"https://picsum.photos/seed/{seed}/{width}/{height}"


def _get_hashtags(topic: str) -> str:
    for key, tags in HASHTAG_MAP.items():
        if key.lower() in topic.lower():
            return " ".join(random.sample(tags, min(2, len(tags))))
    return "#Trending"


def generate_tweet_drafts(
    topics: list[str] | None = None,
    count: int = 5,
) -> list[dict[str, str]]:
    """Generate tweet drafts for given topics (or niche keywords).

    Returns a list of dicts with ``topic``, ``tweet``, ``hashtags``,
    ``full_tweet``, and ``char_count`` fields.
    """
    topics = topics or Config.NICHE_KEYWORDS
    drafts: list[dict[str, str]] = []

    for _ in range(count):
        topic = random.choice(topics)
        template = random.choice(TWEET_TEMPLATES)
        tweet_text = template.format(topic=topic)
        hashtags = _get_hashtags(topic)
        full_tweet = f"{tweet_text}\n\n{hashtags}"

        if len(full_tweet) > 280:
            full_tweet = full_tweet[:277] + "..."

        drafts.append({
            "topic": topic,
            "tweet": tweet_text,
            "hashtags": hashtags,
            "full_tweet": full_tweet,
            "char_count": str(len(full_tweet)),
            "image_url": _get_image_url(topic),
        })

    logger.info("Generated %d tweet drafts", len(drafts))
    return drafts
