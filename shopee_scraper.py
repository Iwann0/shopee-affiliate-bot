"""
Component 1: Shopee Product Scraper
Fetches trending/bestselling products from Shopee Indonesia using:
  1. Shopee Affiliate API (primary)
  2. Scraping shopee.co.id/sp (fallback)
  3. Mock data (last resort)
Combines with Google Trends data (SerpAPI) to prioritize products.
"""

import os
import re
import json
import time
import sqlite3
import logging
import random
from datetime import datetime

import requests
from bs4 import BeautifulSoup
from serpapi import GoogleSearch

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

DB_NAME = "shopee_products.db"

AFFILIATE_ID = os.getenv("SHOPEE_AFFILIATE_ID", "11320831661")

SHOPEE_AFFILIATE_API = "https://affiliate.shopee.co.id/api/v2/product/get_offer_list"

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0",
]

FALLBACK_KEYWORDS = ["baju murah", "skincare", "hp murah", "earbuds", "perabot rumah"]


def init_db():
    """Initialize SQLite database with the required schema."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS shopee_products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            original_price INTEGER,
            discount_price INTEGER,
            discount_pct INTEGER,
            url TEXT NOT NULL,
            rating REAL,
            sold INTEGER,
            posted INTEGER DEFAULT 0,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    conn.close()
    logger.info("Database initialized: %s", DB_NAME)


def get_trending_keywords():
    """Get top 5 Google Trends keywords for Indonesia today using SerpAPI."""
    api_key = os.getenv("SERPAPI_KEY")

    # Debug logging for env var
    if api_key:
        logger.info("SERPAPI_KEY is set (length: %d, starts with: %s...)", len(api_key), api_key[:4])
    else:
        logger.warning("SERPAPI_KEY is NOT set in environment. Available env vars: %s",
                        [k for k in os.environ.keys() if 'SERP' in k.upper() or 'API' in k.upper()])
        return FALLBACK_KEYWORDS

    try:
        params = {
            "engine": "google_trends_trending_now",
            "frequency": "daily",
            "geo": "ID",
            "api_key": api_key,
        }
        search = GoogleSearch(params)
        results = search.get_dict()

        keywords = []
        daily_searches = results.get("daily_searches", [])
        for day in daily_searches:
            for search_item in day.get("searches", []):
                query = search_item.get("query", {}).get("text", "")
                if query:
                    keywords.append(query)
                if len(keywords) >= 5:
                    break
            if len(keywords) >= 5:
                break

        if not keywords:
            logger.warning("No trending keywords from SerpAPI response. Using fallback.")
            return FALLBACK_KEYWORDS

        logger.info("Trending keywords (SerpAPI): %s", keywords)
        return keywords
    except Exception as e:
        logger.warning("Failed to fetch Google Trends via SerpAPI: %s. Using fallback keywords.", e)
        return FALLBACK_KEYWORDS


def _build_headers():
    """Build request headers mimicking a browser."""
    return {
        "User-Agent": random.choice(USER_AGENTS),
        "Accept": "application/json",
        "Accept-Language": "id-ID,id;q=0.9,en-US;q=0.8,en;q=0.7",
        "Referer": "https://shopee.co.id/",
    }


def scrape_affiliate_api():
    """Fetch products from Shopee Affiliate API (primary method)."""
    logger.info("Trying Shopee Affiliate API...")
    products = []

    params = {
        "limit": 10,
        "scenario": "hot_sale",
        "af_siteid": AFFILIATE_ID,
    }

    try:
        resp = requests.get(SHOPEE_AFFILIATE_API, params=params, headers=_build_headers(), timeout=15)
        logger.info("Affiliate API response status: %d", resp.status_code)
        resp.raise_for_status()
        data = resp.json()

        items = data.get("data", {}).get("items", [])
        if not items:
            items = data.get("items", [])
        if not items:
            items = data.get("data", {}).get("offers", [])

        for item in items:
            try:
                name = item.get("product_name") or item.get("name", "")
                original_price = int(item.get("original_price") or item.get("price", 0))
                discount_price = int(item.get("discount_price") or item.get("sale_price", 0))

                if original_price <= 0:
                    original_price = discount_price

                discount_pct = 0
                if original_price > 0 and original_price > discount_price:
                    discount_pct = round((1 - discount_price / original_price) * 100)

                product_url = item.get("offer_link") or item.get("product_link") or item.get("url", "")
                rating = float(item.get("rating") or item.get("item_rating", 0))
                sold = int(item.get("sales") or item.get("sold", 0))

                if name and product_url:
                    products.append({
                        "name": name,
                        "original_price": original_price,
                        "discount_price": discount_price,
                        "discount_pct": discount_pct,
                        "url": product_url,
                        "rating": rating,
                        "sold": sold,
                        "category": "affiliate_hot_sale",
                    })
            except Exception as e:
                logger.debug("Error parsing affiliate item: %s", e)
                continue

        logger.info("Affiliate API returned %d products", len(products))
    except requests.RequestException as e:
        logger.warning("Shopee Affiliate API failed: %s", e)
    except (json.JSONDecodeError, KeyError) as e:
        logger.warning("Error parsing Affiliate API response: %s", e)

    return products


def scrape_shopee_sp():
    """Fallback: scrape hot products from shopee.co.id/sp using BeautifulSoup."""
    logger.info("Trying fallback: scraping shopee.co.id/sp...")
    products = []

    try:
        headers = {
            "User-Agent": random.choice(USER_AGENTS),
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "id-ID,id;q=0.9",
        }
        resp = requests.get("https://shopee.co.id/sp", headers=headers, timeout=15)
        logger.info("shopee.co.id/sp response status: %d", resp.status_code)
        resp.raise_for_status()

        soup = BeautifulSoup(resp.text, "html.parser")

        # Try to find product data in script tags (JSON embedded)
        scripts = soup.find_all("script")
        for script in scripts:
            text = script.string or ""
            if "product" in text.lower() and ("price" in text.lower() or "name" in text.lower()):
                try:
                    # Try to extract JSON data from script
                    json_match = re.search(r'\{.*"product".*\}', text)
                    if json_match:
                        data = json.loads(json_match.group())
                        logger.info("Found product data in script tag")
                except (json.JSONDecodeError, AttributeError):
                    continue

        # Try to find product cards/items in HTML
        product_elements = soup.select("[data-sqe='item'], .shopee-search-item-result__item, .flash-sale-item")
        for elem in product_elements:
            try:
                name_el = elem.select_one("[data-sqe='name'], .item-name, .name")
                price_el = elem.select_one("[data-sqe='price'], .item-price, .price")
                link_el = elem.select_one("a[href]")

                if name_el and price_el and link_el:
                    name = name_el.get_text(strip=True)
                    price_text = re.sub(r'[^\d]', '', price_el.get_text(strip=True))
                    price = int(price_text) if price_text else 0
                    url = link_el.get("href", "")
                    if not url.startswith("http"):
                        url = "https://shopee.co.id" + url

                    products.append({
                        "name": name,
                        "original_price": price,
                        "discount_price": price,
                        "discount_pct": 0,
                        "url": url,
                        "rating": 4.5,
                        "sold": 100,
                        "category": "sp_hot",
                    })
            except Exception as e:
                logger.debug("Error parsing SP element: %s", e)
                continue

        logger.info("shopee.co.id/sp returned %d products", len(products))
    except requests.RequestException as e:
        logger.warning("shopee.co.id/sp scraping failed: %s", e)
    except Exception as e:
        logger.warning("Error parsing shopee.co.id/sp: %s", e)

    return products


def _generate_mock_products():
    """Generate mock products when all APIs are unavailable (last resort fallback)."""
    logger.info("Using mock products as last resort fallback...")
    mock_data = [
        {
            "name": "Wardah Lightening Day Cream 30g",
            "original_price": 45000,
            "discount_price": 32000,
            "discount_pct": 29,
            "url": "https://shopee.co.id/product/123456/789012",
            "rating": 4.8,
            "sold": 5200,
            "category": "skincare",
        },
        {
            "name": "Gamis Wanita Syari Terbaru 2024",
            "original_price": 189000,
            "discount_price": 99000,
            "discount_pct": 48,
            "url": "https://shopee.co.id/product/234567/890123",
            "rating": 4.6,
            "sold": 3400,
            "category": "fashion_wanita",
        },
        {
            "name": "TWS Bluetooth Earbuds Pro Bass",
            "original_price": 250000,
            "discount_price": 89000,
            "discount_pct": 64,
            "url": "https://shopee.co.id/product/345678/901234",
            "rating": 4.5,
            "sold": 8900,
            "category": "elektronik",
        },
        {
            "name": "Rak Serbaguna 4 Tingkat Minimalis",
            "original_price": 175000,
            "discount_price": 95000,
            "discount_pct": 46,
            "url": "https://shopee.co.id/product/456789/012345",
            "rating": 4.7,
            "sold": 2100,
            "category": "perlengkapan_rumah",
        },
        {
            "name": "Serum Vitamin C Brightening 20ml",
            "original_price": 125000,
            "discount_price": 49000,
            "discount_pct": 61,
            "url": "https://shopee.co.id/product/567890/123456",
            "rating": 4.9,
            "sold": 12000,
            "category": "skincare",
        },
        {
            "name": "Dress Korean Style Premium",
            "original_price": 220000,
            "discount_price": 110000,
            "discount_pct": 50,
            "url": "https://shopee.co.id/product/678901/234567",
            "rating": 4.4,
            "sold": 4500,
            "category": "fashion_wanita",
        },
        {
            "name": "Charger Fast Charging 65W USB-C",
            "original_price": 150000,
            "discount_price": 65000,
            "discount_pct": 57,
            "url": "https://shopee.co.id/product/789012/345678",
            "rating": 4.6,
            "sold": 6700,
            "category": "elektronik",
        },
        {
            "name": "Organizer Makeup Box Akrilik",
            "original_price": 95000,
            "discount_price": 45000,
            "discount_pct": 53,
            "url": "https://shopee.co.id/product/890123/456789",
            "rating": 4.5,
            "sold": 3200,
            "category": "perlengkapan_rumah",
        },
        {
            "name": "Sheet Mask Korea 10pcs Moisturizing",
            "original_price": 80000,
            "discount_price": 35000,
            "discount_pct": 56,
            "url": "https://shopee.co.id/product/901234/567890",
            "rating": 4.7,
            "sold": 15000,
            "category": "skincare",
        },
        {
            "name": "Blouse Wanita Import Silk Premium",
            "original_price": 165000,
            "discount_price": 79000,
            "discount_pct": 52,
            "url": "https://shopee.co.id/product/012345/678901",
            "rating": 4.3,
            "sold": 1800,
            "category": "fashion_wanita",
        },
        {
            "name": "Power Bank 20000mAh Fast Charge",
            "original_price": 350000,
            "discount_price": 149000,
            "discount_pct": 57,
            "url": "https://shopee.co.id/product/112233/445566",
            "rating": 4.8,
            "sold": 9500,
            "category": "elektronik",
        },
        {
            "name": "Lampu LED Strip 5M Remote RGB",
            "original_price": 120000,
            "discount_price": 55000,
            "discount_pct": 54,
            "url": "https://shopee.co.id/product/223344/556677",
            "rating": 4.4,
            "sold": 7800,
            "category": "perlengkapan_rumah",
        },
    ]
    return mock_data


def filter_products(products, min_rating=4.3, min_sold=100):
    """Filter products by rating and sold count."""
    filtered = [
        p for p in products
        if p["rating"] >= min_rating and p["sold"] >= min_sold
    ]
    logger.info("Filtered to %d products (rating>=%.1f, sold>=%d)", len(filtered), min_rating, min_sold)
    return filtered


def prioritize_by_trends(products, keywords):
    """Boost products whose names match trending keywords."""
    for p in products:
        p["trend_boost"] = 0
        name_lower = p["name"].lower()
        for kw in keywords:
            if kw.lower() in name_lower:
                p["trend_boost"] += 1

    # Sort by: trend_boost desc, then discount_pct * sold desc
    products.sort(
        key=lambda x: (x["trend_boost"], x["discount_pct"] * x["sold"]),
        reverse=True,
    )
    return products


def save_to_db(products):
    """Save top 10 products to SQLite database."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    saved = 0

    for p in products[:10]:
        # Check for duplicate by URL
        cursor.execute("SELECT id FROM shopee_products WHERE url = ?", (p["url"],))
        if cursor.fetchone():
            logger.debug("Duplicate skipped: %s", p["name"])
            continue

        cursor.execute("""
            INSERT INTO shopee_products (name, original_price, discount_price, discount_pct, url, rating, sold, posted)
            VALUES (?, ?, ?, ?, ?, ?, ?, 0)
        """, (
            p["name"],
            p["original_price"],
            p["discount_price"],
            p["discount_pct"],
            p["url"],
            p["rating"],
            p["sold"],
        ))
        saved += 1

    conn.commit()
    conn.close()
    logger.info("Saved %d new products to database", saved)
    return saved


def run_scraper():
    """Main scraper function — entry point with cascading fallbacks."""
    logger.info("=" * 50)
    logger.info("Starting Shopee scraper...")
    init_db()

    # Step 1: Get trending keywords
    keywords = get_trending_keywords()

    # Step 2: Try Shopee Affiliate API first
    all_products = scrape_affiliate_api()

    # Step 3: Fallback to scraping shopee.co.id/sp
    if not all_products:
        logger.warning("Affiliate API returned no products. Trying shopee.co.id/sp fallback...")
        all_products = scrape_shopee_sp()

    # Step 4: Last resort — mock data
    if not all_products:
        logger.warning("All APIs failed. Using mock data as last resort.")
        all_products = _generate_mock_products()

    # Step 5: Filter by rating and sold count
    filtered = filter_products(all_products, min_rating=4.3, min_sold=100)

    # Step 6: Prioritize by trending keywords
    prioritized = prioritize_by_trends(filtered, keywords)

    # Step 7: Save top 10 to DB
    saved = save_to_db(prioritized)
    logger.info("Scraper complete. %d products saved.", saved)
    return saved


if __name__ == "__main__":
    run_scraper()
