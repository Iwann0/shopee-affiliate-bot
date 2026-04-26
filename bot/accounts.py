"""Discover relevant accounts to follow for growth.

Uses the authenticated Twitter API (get_me) for basic profile lookup,
and suggests accounts based on trending topics and niche keywords.
Since the free Twitter API tier does not support user search, this module
provides curated suggestions and strategies.
"""

import logging

import tweepy

from bot.config import Config

logger = logging.getLogger(__name__)


def get_my_profile(client: tweepy.Client) -> dict:
    """Get the authenticated user's profile summary."""
    try:
        resp = client.get_me(user_fields=["public_metrics", "description"])
        if resp.data:
            metrics = resp.data.public_metrics or {}
            return {
                "username": resp.data.username,
                "id": str(resp.data.id),
                "followers": metrics.get("followers_count", 0),
                "following": metrics.get("following_count", 0),
                "tweets": metrics.get("tweet_count", 0),
                "description": resp.data.description or "",
            }
    except tweepy.TweepyException as e:
        logger.warning("Failed to get profile: %s", e)
    return {}


def suggest_follow_strategy(profile: dict) -> list[str]:
    """Generate actionable follow strategy tips based on current profile state."""
    tips: list[str] = []
    followers = profile.get("followers", 0)
    following = profile.get("following", 0)
    tweets = profile.get("tweets", 0)

    if tweets < 10:
        tips.append(
            "Post at least 10 quality tweets before aggressive following. "
            "Accounts with no content get ignored."
        )

    if followers == 0:
        tips.append(
            "Start by following 20-30 accounts in your niche. "
            "Engage with their content (like + reply) to get noticed."
        )

    if following > 0 and followers > 0 and following / followers > 2.0:
        tips.append(
            f"Your following/follower ratio is {following / followers:.1f}. "
            "Slow down on following and focus on creating engaging content."
        )

    tips.append(
        "Search Twitter for your niche keywords and follow accounts that: "
        "have 500-50K followers, tweet regularly, and get good engagement."
    )
    tips.append(
        "Reply to trending tweets in your niche with genuine insights. "
        "This is the fastest free way to get noticed."
    )
    tips.append(
        "Use these hashtags in your posts to increase discoverability: "
        + ", ".join(f"#{kw}" for kw in Config.NICHE_KEYWORDS[:5])
    )

    return tips


def suggest_accounts_to_follow(niche_keywords: list[str] | None = None) -> list[dict]:
    """Suggest types of accounts to follow based on niche keywords.

    Since free-tier Twitter API doesn't support user search, this provides
    search strategies and account categories to find manually.
    """
    keywords = niche_keywords or Config.NICHE_KEYWORDS
    suggestions: list[dict] = []

    for kw in keywords:
        suggestions.append({
            "keyword": kw,
            "search_query": f'"{kw}" filter:verified',
            "strategy": (
                f"Search '{kw}' on Twitter, sort by 'People'. "
                f"Follow accounts with 1K-50K followers that tweet about {kw} regularly."
            ),
            "account_types": [
                f"{kw} influencers and thought leaders",
                f"{kw} news and media accounts",
                f"{kw} community accounts and newsletters",
                f"Active commentators discussing {kw}",
            ],
        })

    logger.info("Generated follow suggestions for %d keywords", len(suggestions))
    return suggestions
