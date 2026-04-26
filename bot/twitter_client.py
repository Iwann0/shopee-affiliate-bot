"""Twitter API client wrapper using Tweepy v2."""

import logging

import tweepy

from bot.config import Config

logger = logging.getLogger(__name__)


def create_client() -> tweepy.Client:
    """Create an authenticated Twitter API v2 client."""
    return tweepy.Client(
        bearer_token=Config.TWITTER_BEARER_TOKEN,
        consumer_key=Config.TWITTER_API_KEY,
        consumer_secret=Config.TWITTER_API_SECRET,
        access_token=Config.TWITTER_ACCESS_TOKEN,
        access_token_secret=Config.TWITTER_ACCESS_TOKEN_SECRET,
        wait_on_rate_limit=True,
    )


def get_me(client: tweepy.Client) -> tweepy.User:
    """Get the authenticated user's profile."""
    resp = client.get_me(user_fields=["public_metrics", "description"])
    if resp.data is None:
        raise RuntimeError("Failed to fetch authenticated user profile")
    return resp.data
