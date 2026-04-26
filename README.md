# Twitter/X Growth Bot

Automated Twitter/X bot that engages with trending topics, grows your followers organically, and helps monetize through sponsorships.

## Features

- **Auto-Engagement** — Likes, retweets, and replies to trending tweets in your niche
- **Content Posting** — Generates and posts original tweets about trending topics
- **Smart Follow/Unfollow** — Follows relevant users, unfollows non-followers after a grace period
- **Rate Limiting** — Built-in rate limiter to stay within Twitter API limits and avoid bans
- **Analytics Tracking** — Records follower growth, engagement metrics, and generates reports
- **Configurable Scheduling** — All intervals and thresholds are configurable via environment variables

## Quick Start

### 1. Clone and install

```bash
git clone https://github.com/Iwann0/twitter-growth-bot.git
cd twitter-growth-bot
pip install -e .
```

### 2. Configure environment

Copy the example env file and fill in your Twitter API credentials:

```bash
cp .env.example .env
# Edit .env with your Twitter API credentials
```

You need a Twitter Developer account with **Elevated** access for full functionality.
Get your API keys at: https://developer.twitter.com/en/portal/dashboard

### 3. Run the bot

```bash
python -m bot.main
```

## Configuration

All settings are configurable via environment variables (see `.env.example`):

| Variable | Default | Description |
|----------|---------|-------------|
| `TWITTER_API_KEY` | — | Twitter API key (required) |
| `TWITTER_API_SECRET` | — | Twitter API secret (required) |
| `TWITTER_ACCESS_TOKEN` | — | OAuth access token (required) |
| `TWITTER_ACCESS_TOKEN_SECRET` | — | OAuth access token secret (required) |
| `TWITTER_BEARER_TOKEN` | — | Bearer token (required) |
| `NICHE_KEYWORDS` | `tech,programming,AI,startup,crypto` | Comma-separated topics to engage with |
| `MAX_LIKES_PER_HOUR` | `15` | Max likes per hour |
| `MAX_RETWEETS_PER_HOUR` | `10` | Max retweets per hour |
| `MAX_REPLIES_PER_HOUR` | `5` | Max replies per hour |
| `MAX_FOLLOWS_PER_HOUR` | `10` | Max follows/unfollows per hour |
| `ENGAGE_INTERVAL_MINUTES` | `30` | How often to engage with tweets |
| `POST_INTERVAL_MINUTES` | `120` | How often to post original content |
| `FOLLOW_INTERVAL_MINUTES` | `60` | How often to run follow strategy |
| `UNFOLLOW_INTERVAL_MINUTES` | `360` | How often to unfollow non-followers |
| `UNFOLLOW_AFTER_DAYS` | `3` | Days to wait before unfollowing non-followers |
| `MAX_FOLLOWING_RATIO` | `1.5` | Max following/followers ratio |

## Deploy on Railway

1. Connect this repo to [Railway](https://railway.app)
2. Add your Twitter API credentials as environment variables
3. Railway will detect the `Procfile` and start the bot as a worker

## How It Works

1. **Startup** — Authenticates with Twitter, runs an initial engagement round and posts a tweet
2. **Engagement Loop** — Every 30 minutes, searches for trending tweets in your niche, likes/retweets/replies
3. **Content Loop** — Every 2 hours, generates and posts an original tweet about a trending topic
4. **Follow Loop** — Every hour, follows users who engage with niche content
5. **Unfollow Loop** — Every 6 hours, unfollows users who haven't followed back
6. **Analytics** — Every 12 hours, records a snapshot of your account metrics

## Monetization Strategy

Once you grow to 1,000+ engaged followers:

1. **Sponsored tweets** — Brands pay for tweets/threads about their products
2. **Affiliate marketing** — Share affiliate links in your niche
3. **Twitter/X Premium** — Earn from ad revenue sharing
4. **Consulting leads** — Use your profile to attract clients
5. **Product promotion** — Promote your own digital products

## License

MIT
