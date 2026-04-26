"""
Component 2: Content Generator
Reads unposted products from SQLite and generates tweet content
with Shopee affiliate links in Bahasa Indonesia.
"""

import os
import json
import random
import sqlite3
import logging
from datetime import datetime

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

DB_NAME = "shopee_products.db"
PENDING_FILE = "pending_posts.json"

AFFILIATE_ID = os.getenv("SHOPEE_AFFILIATE_ID", "11320831661")

MAX_TWEET_LENGTH = 280


def _format_price(price):
    """Format price with dots as thousand separator (Indonesian style)."""
    return f"{price:,}".replace(",", ".")


def _build_affiliate_link(product_url):
    """Build Shopee affiliate link."""
    separator = "&" if "?" in product_url else "?"
    return f"{product_url}{separator}af_siteid={AFFILIATE_ID}&af_sub1=twitter"


def _generate_tweet(product, style):
    """Generate a tweet based on the given style template."""
    name = product["name"]
    ori = _format_price(product["original_price"])
    disc = _format_price(product["discount_price"])
    pct = product["discount_pct"]
    rating = product["rating"]
    sold = product["sold"]
    selisih = _format_price(product["original_price"] - product["discount_price"])
    link = _build_affiliate_link(product["url"])

    templates = {
        "A": (
            f"\U0001f525 PROMO HARI INI!\n"
            f"{{name}}\n"
            f"\U0001f4b0 ~~Rp{ori}~~ \u2192 Rp{disc} (hemat {pct}%)\n"
            f"\u2b50 Rating {rating} | {sold}+ terjual\n"
            f"\U0001f449 {link}\n\n"
            f"#ShopeeAffiliate #PromoShopee #Belanja"
        ),
        "B": (
            f"\u2705 Worth it banget!\n"
            f"{{name}} diskon {pct}%\n"
            f"Dari Rp{ori} jadi Rp{disc}\n"
            f"\U0001f6d2 {link}\n\n"
            f"#Shopee #Sale #Rekomendasi"
        ),
        "C": (
            f"Kalian udah tau belum?\n"
            f"{{name}} lagi diskon!\n"
            f"\U0001f4b8 Hemat Rp{selisih} hari ini\n"
            f"\U0001f517 {link}\n\n"
            f"#ShopeeID #FlashSale #Deal"
        ),
        "D": (
            f"Jangan kelewatan! \u23f0\n"
            f"{{name}}\n"
            f"Harga coret Rp{ori} \u2192 Sekarang Rp{disc}\n"
            f"\u2728 {link}\n\n"
            f"#BelanjaPintar #Shopee #Promo"
        ),
    }

    tweet_template = templates[style]

    # Try with full name first
    tweet = tweet_template.replace("{name}", name)

    # Truncate product name if tweet exceeds 280 characters
    if len(tweet) > MAX_TWEET_LENGTH:
        overhead = len(tweet_template.replace("{name}", ""))
        max_name_len = MAX_TWEET_LENGTH - overhead - 3  # 3 for "..."
        if max_name_len > 0:
            name = name[:max_name_len] + "..."
        tweet = tweet_template.replace("{name}", name)

    return tweet


def get_unposted_products():
    """Fetch unposted products from the database."""
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("""
        SELECT id, name, original_price, discount_price, discount_pct, url, rating, sold
        FROM shopee_products
        WHERE posted = 0
        ORDER BY (discount_pct * sold) DESC
    """)
    products = [dict(row) for row in cursor.fetchall()]
    conn.close()
    logger.info("Found %d unposted products", len(products))
    return products


def load_pending_posts():
    """Load existing pending posts from JSON file."""
    if os.path.exists(PENDING_FILE):
        with open(PENDING_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return []


def save_pending_posts(posts):
    """Save pending posts to JSON file."""
    with open(PENDING_FILE, "w", encoding="utf-8") as f:
        json.dump(posts, f, ensure_ascii=False, indent=2)
    logger.info("Saved %d pending posts to %s", len(posts), PENDING_FILE)


def run_generator():
    """Main generator function — entry point."""
    logger.info("=" * 50)
    logger.info("Starting content generator...")

    products = get_unposted_products()
    if not products:
        logger.info("No unposted products found. Run scraper first.")
        return 0

    styles = ["A", "B", "C", "D"]
    pending = load_pending_posts()

    # Track existing product IDs in pending to avoid duplicates
    existing_ids = {p["product_id"] for p in pending if not p.get("posted", False)}

    generated = 0
    for product in products:
        if product["id"] in existing_ids:
            logger.debug("Product %d already in pending posts", product["id"])
            continue

        style = random.choice(styles)
        tweet = _generate_tweet(product, style)

        pending.append({
            "product_id": product["id"],
            "product_name": product["name"],
            "tweet": tweet,
            "affiliate_link": _build_affiliate_link(product["url"]),
            "style": style,
            "posted": False,
            "created_at": datetime.now().isoformat(),
        })
        generated += 1

    save_pending_posts(pending)
    logger.info("Generated %d new tweets", generated)
    return generated


if __name__ == "__main__":
    run_generator()
