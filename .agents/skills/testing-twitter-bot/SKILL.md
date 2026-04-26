# Testing the Twitter Trend Research Bot

## Setup
```bash
pip install -e .
pip install ruff
```

## Run
```bash
python -m bot.main
```
Requires all 5 Twitter env vars: `TWITTER_API_KEY`, `TWITTER_API_SECRET`, `TWITTER_ACCESS_TOKEN`, `TWITTER_ACCESS_TOKEN_SECRET`, `TWITTER_BEARER_TOKEN`.

## Credential Mapping
The working credentials may be stored under different env var names. Map them before running:
```bash
export TWITTER_API_KEY="$consumer_key"
export TWITTER_API_SECRET="$consumer_key_secret"
export TWITTER_ACCESS_TOKEN="$access_token"
export TWITTER_ACCESS_TOKEN_SECRET="$access_token_secret"
export TWITTER_BEARER_TOKEN="$bearer_token"
```

## Lint
```bash
ruff check bot/
ruff check --fix bot/  # auto-fix
```

## Testing Individual Modules
All modules can be tested independently via Python one-liners:
```bash
# Trending (free, no Twitter API needed)
python -c "from bot.trending import scrape_twitter_trends; print(len(scrape_twitter_trends()))"
python -c "from bot.trending import get_google_trends_rising; print(get_google_trends_rising(['AI']))"
python -c "from bot.trending import get_google_trends_interest; print(get_google_trends_interest(['AI', 'crypto']))"

# Content generation (no API needed)
python -c "from bot.content import generate_tweet_drafts; print(generate_tweet_drafts(['AI'], count=3))"

# Account suggestions (no API needed)
python -c "from bot.accounts import suggest_accounts_to_follow; print(suggest_accounts_to_follow(['AI']))"

# Config validation (no API needed)
python -c "from bot.config import Config; print(Config.validate())"

# Scheduler registration (no API needed, but needs tweepy client)
python -c "from bot.twitter_client import create_client; from bot.scheduler import create_scheduler; s = create_scheduler(create_client(), '123'); print([(j.id, j.name) for j in s.get_jobs()])"
```

## Key Assertions
- `scrape_twitter_trends()` returns a list of 5-30 strings (no duplicates)
- `get_google_trends_rising(['AI'])` returns a dict with `query` and `value` keys per item
- `get_google_trends_interest(['AI'])` returns floats between 0-100
- `generate_tweet_drafts()` returns dicts with `full_tweet` under 280 chars
- Config validation returns a list of error strings for missing env vars
- Scheduler creates exactly 2 jobs: `research` and `analytics`

## Known Limitations
- Twitter account @Sentimen666 has no API credits (402 Payment Required for search/post)
- Auth works on the free tier; trend research uses free sources (Google Trends + trends24.in)
- The bot outputs research to console — user posts manually
