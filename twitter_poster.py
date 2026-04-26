"""
Component 3: Twitter Poster
Posts tweets from pending_posts.json using Tweepy (Twitter API v2).
Updates posted status in both the JSON file and SQLite database.
"""

import os
import json
import sqlite3
import logging

import tweepy

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

DB_NAME = "shopee_products.db"
PENDING_FILE = "pending_posts.json"


def _get_twitter_client():
    """Initialize and return Tweepy Client for Twitter API v2."""
    bearer_token = os.getenv("TWITTER_BEARER_TOKEN")
    api_key = os.getenv("TWITTER_API_KEY")
    api_secret = os.getenv("TWITTER_API_SECRET")
    access_token = os.getenv("TWITTER_ACCESS_TOKEN")
    access_token_secret = os.getenv("TWITTER_ACCESS_TOKEN_SECRET")

    if not all([api_key, api_secret, access_token, access_token_secret]):
        raise ValueError(
            "Twitter credentials not found. Set TWITTER_API_KEY, TWITTER_API_SECRET, "
            "TWITTER_ACCESS_TOKEN, and TWITTER_ACCESS_TOKEN_SECRET environment variables."
        )

    client = tweepy.Client(
        bearer_token=bearer_token,
        consumer_key=api_key,
        consumer_secret=api_secret,
        access_token=access_token,
        access_token_secret=access_token_secret,
    )
    logger.info("Twitter client initialized successfully")
    return client


def load_pending_posts():
    """Load pending posts from JSON file."""
    if not os.path.exists(PENDING_FILE):
        logger.warning("No pending posts file found: %s", PENDING_FILE)
        return []
    with open(PENDING_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def save_pending_posts(posts):
    """Save pending posts back to JSON file."""
    with open(PENDING_FILE, "w", encoding="utf-8") as f:
        json.dump(posts, f, ensure_ascii=False, indent=2)


def mark_posted_in_db(product_id):
    """Update posted=1 in the SQLite database for the given product."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("UPDATE shopee_products SET posted = 1 WHERE id = ?", (product_id,))
    conn.commit()
    conn.close()
    logger.info("Marked product %d as posted in database", product_id)


def post_next_tweet():
    """Post the next unposted tweet from pending_posts.json."""
    posts = load_pending_posts()

    # Find the first unposted tweet
    target = None
    target_idx = None
    for idx, post in enumerate(posts):
        if not post.get("posted", False):
            target = post
            target_idx = idx
            break

    if target is None:
        logger.info("No pending tweets to post.")
        return False

    try:
        client = _get_twitter_client()
        tweet_text = target["tweet"]

        logger.info("Posting tweet for product: %s", target["product_name"])
        response = client.create_tweet(text=tweet_text)

        tweet_id = response.data["id"]
        logger.info("Tweet posted successfully! Tweet ID: %s", tweet_id)

        # Update pending_posts.json
        posts[target_idx]["posted"] = True
        posts[target_idx]["tweet_id"] = tweet_id
        save_pending_posts(posts)

        # Update SQLite database
        mark_posted_in_db(target["product_id"])

        return True

    except tweepy.TweepyException as e:
        logger.error("Failed to post tweet: %s", e)
        return False
    except Exception as e:
        logger.error("Unexpected error posting tweet: %s", e)
        return False


def post_all_pending():
    """Post all pending tweets (for manual trigger)."""
    count = 0
    while post_next_tweet():
        count += 1
    logger.info("Posted %d tweets total", count)
    return count


if __name__ == "__main__":
    post_next_tweet()
