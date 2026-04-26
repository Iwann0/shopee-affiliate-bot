# Twitter/X Trend Research & Growth Bot

A **free** trend research and content intelligence tool that helps you grow your Twitter/X account. It finds rising trends, generates ready-to-post tweet drafts, and suggests accounts to follow — all without needing paid Twitter API access for its core features.

## What It Does

- **Finds trending topics** — scrapes Twitter trends from trends24.in + Google Trends rising queries
- **Generates tweet drafts** — creates copy-paste-ready tweets based on what's trending in your niche
- **Suggests accounts to follow** — provides search strategies and account categories for growth
- **Tracks your growth** — records follower/following/tweet snapshots over time
- **Runs on autopilot** — periodic research cycles via scheduler (every 30 min by default)
- **Web dashboard** — local web UI to browse trends, copy drafts, and track growth

## How It Works

The bot uses **free data sources** for trend discovery:
1. **trends24.in** — scraped for real-time Twitter/X trending topics
2. **Google Trends** — interest scores and rising search queries for your niche keywords

Twitter API is only used for:
- Authenticating your account
- Fetching your profile stats (followers, following, tweets)
- Recording analytics snapshots

**You post manually** — the bot generates drafts and research, you decide what to post.

## Quick Start

```bash
# Clone and install
git clone https://github.com/Iwann0/shopee-affiliate-bot.git
cd shopee-affiliate-bot
pip install -e .

# Configure
cp .env.example .env
# Edit .env with your Twitter API credentials

# Run (CLI mode)
python -m bot.main

# Run (Web Dashboard)
python -m bot.main --dashboard
# Open http://localhost:5000 in your browser
```

## Configuration

| Variable | Default | Description |
|---|---|---|
| `TWITTER_API_KEY` | (required) | Twitter API consumer key |
| `TWITTER_API_SECRET` | (required) | Twitter API consumer secret |
| `TWITTER_ACCESS_TOKEN` | (required) | OAuth access token |
| `TWITTER_ACCESS_TOKEN_SECRET` | (required) | OAuth access token secret |
| `TWITTER_BEARER_TOKEN` | (required) | Bearer token |
| `NICHE_KEYWORDS` | `tech,programming,AI,startup,crypto` | Comma-separated topics to research |
| `ENGAGE_INTERVAL_MINUTES` | `30` | How often to run trend research |
| `POST_INTERVAL_MINUTES` | `120` | How often to generate new tweet drafts |
| `ANALYTICS_INTERVAL_MINUTES` | `720` | How often to record analytics |
| `DRAFT_COUNT` | `5` | Number of tweet drafts per cycle |
| `ANALYTICS_FILE` | `analytics.json` | Where to store analytics data |

## Sample Output

```
======================================================================
  TRENDING TOPICS
======================================================================

📈 Twitter/X Trending Right Now:
   1. #AI
   2. #Bitcoin
   3. Claude AI
   ...

📊 Google Trends Interest Scores (0-100):
  AI                 100  ████████████████████
  crypto              45  █████████
  tech                38  ███████

🚀 Rising Search Queries:

  [AI]
    • cursor ai (+50%)
    • kimi ai (+70%)
    • claude ai (+2150%)

======================================================================
  TWEET DRAFTS (ready to copy-paste)
======================================================================

--- Draft 1 (142 chars) ---
Hot take: AI is going to change everything in the next 5 years...

======================================================================
  ACCOUNTS TO FOLLOW
======================================================================

🔍 Search: "AI" filter:verified
   Strategy: Search 'AI' on Twitter, sort by 'People'...
```

## Deploy on Railway

1. Fork this repo
2. Create a new project on [Railway](https://railway.app)
3. Set environment variables in Railway dashboard
4. Deploy — Railway auto-detects the `Procfile`

## Monetization Strategy

Once you grow your account using the research insights:

1. **Sponsored tweets** — brands pay for shout-outs ($50-$500+ per tweet)
2. **Affiliate links** — promote products with your unique link
3. **Twitter Premium** — earn ad revenue from your content
4. **Consulting leads** — use your account to attract clients
5. **Product promotion** — launch your own products to your audience

## Project Structure

```
bot/
├── main.py          # Entry point — CLI + dashboard modes
├── dashboard.py     # Flask web dashboard
├── trending.py      # Trend discovery (Google Trends + web scraping)
├── content.py       # Tweet draft generator
├── accounts.py      # Account follow suggestions
├── analytics.py     # Growth tracking
├── scheduler.py     # Periodic research scheduling
├── config.py        # Environment variable config
└── twitter_client.py # Twitter API client setup
templates/
└── dashboard.html   # Dashboard HTML template
static/
├── style.css        # Dashboard styles
└── app.js           # Dashboard JavaScript
```
