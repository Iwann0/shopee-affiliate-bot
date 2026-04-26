"""Discover trending topics using free data sources (Google Trends + web scraping)."""

import logging
import re

import requests
from pytrends.request import TrendReq

from bot.config import Config

logger = logging.getLogger(__name__)

_TRENDS24_URL = "https://trends24.in/"
_USER_AGENT = (
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
)


def get_google_trends_rising(keywords: list[str] | None = None) -> dict[str, list[dict]]:
    """Get rising related queries from Google Trends for each keyword.

    Returns a dict mapping each keyword to a list of
    ``{"query": str, "value": int}`` dicts sorted by rising value.
    """
    keywords = keywords or Config.NICHE_KEYWORDS
    results: dict[str, list[dict]] = {}

    for kw in keywords:
        try:
            pytrends = TrendReq(hl="en-US", tz=360)
            pytrends.build_payload([kw], timeframe="now 7-d")
            related = pytrends.related_queries()

            rising = related.get(kw, {}).get("rising")
            if rising is not None and not rising.empty:
                items = rising.to_dict("records")
                results[kw] = items
                logger.info(
                    "Google Trends: %d rising queries for '%s'", len(items), kw
                )
            else:
                results[kw] = []
                logger.info("Google Trends: no rising queries for '%s'", kw)

        except Exception as e:
            logger.warning("Google Trends error for '%s': %s", kw, e)
            results[kw] = []

    return results


def get_google_trends_interest(keywords: list[str] | None = None) -> dict[str, float]:
    """Get current relative interest scores for keywords (0-100).

    Higher score means the keyword is trending more right now.
    """
    keywords = keywords or Config.NICHE_KEYWORDS
    try:
        pytrends = TrendReq(hl="en-US", tz=360)
        pytrends.build_payload(keywords[:5], timeframe="now 1-d")
        interest = pytrends.interest_over_time()

        if interest.empty:
            return {}

        latest = interest.iloc[-1]
        scores = {kw: float(latest.get(kw, 0)) for kw in keywords[:5]}
        logger.info("Interest scores: %s", scores)
        return scores

    except Exception as e:
        logger.warning("Google Trends interest error: %s", e)
        return {}


def scrape_twitter_trends() -> list[str]:
    """Scrape current Twitter/X trending topics from trends24.in (free)."""
    try:
        resp = requests.get(
            _TRENDS24_URL,
            headers={"User-Agent": _USER_AGENT},
            timeout=15,
        )
        resp.raise_for_status()

        # Extract trend names from the HTML
        pattern = r'<a[^>]*class="[^"]*trend-link[^"]*"[^>]*>([^<]+)</a>'
        matches = re.findall(pattern, resp.text)

        if matches:
            # Deduplicate while preserving order
            seen: set[str] = set()
            unique: list[str] = []
            for m in matches:
                cleaned = m.strip()
                if cleaned and cleaned not in seen:
                    seen.add(cleaned)
                    unique.append(cleaned)
            logger.info("Scraped %d Twitter trends from trends24.in", len(unique))
            return unique[:30]

        logger.info("No trends found from trends24.in scraping")
        return []

    except Exception as e:
        logger.warning("Failed to scrape trends24.in: %s", e)
        return []


def get_all_trends() -> dict:
    """Aggregate trends from all free sources into a single report.

    Returns a dict with:
    - twitter_trends: list of currently trending Twitter topics
    - rising_queries: dict of keyword -> rising related queries
    - interest_scores: dict of keyword -> interest score (0-100)
    """
    logger.info("Gathering trends from all sources...")

    twitter_trends = scrape_twitter_trends()
    rising_queries = get_google_trends_rising()
    interest_scores = get_google_trends_interest()

    return {
        "twitter_trends": twitter_trends,
        "rising_queries": rising_queries,
        "interest_scores": interest_scores,
    }
