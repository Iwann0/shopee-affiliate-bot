# Shopee Affiliate Bot 🤖

Bot otomatis untuk promosi produk Shopee Indonesia di Twitter menggunakan link afiliasi.

## Fitur

- **Scraper** (`shopee_scraper.py`): Scrape produk trending/bestselling dari Shopee Indonesia (fashion wanita, skincare, elektronik, perlengkapan rumah). Filter rating >= 4.3, terjual > 100. Integrasi Google Trends Indonesia.
- **Content Generator** (`content_generator.py`): Generate tweet dalam Bahasa Indonesia dengan 4 variasi style. Otomatis tambahkan affiliate link.
- **Twitter Poster** (`twitter_poster.py`): Post tweet otomatis via Twitter API v2 (Tweepy).
- **Scheduler** (`main.py`): Jadwal otomatis menggunakan APScheduler.

## Jadwal Posting

| Waktu WIB | Aktivitas |
|---|---|
| 06:00 | Scrape produk baru + generate konten |
| 07:00 | Post tweet |
| 12:00 | Post tweet |
| 18:00 | Post tweet |
| 21:00 | Post tweet |

## Deployment di Railway.app

### 1. Fork / Clone Repository

```bash
git clone https://github.com/Iwann0/shopee-affiliate-bot.git
```

### 2. Buat Project di Railway

1. Buka [railway.app](https://railway.app) dan login
2. Klik **"New Project"** → **"Deploy from GitHub repo"**
3. Pilih repository `shopee-affiliate-bot`

### 3. Set Environment Variables

Di Railway dashboard, buka **Settings** → **Variables**, tambahkan:

| Variable | Keterangan |
|---|---|
| `TWITTER_BEARER_TOKEN` | Bearer token dari Twitter Developer Portal |
| `TWITTER_API_KEY` | Consumer API Key |
| `TWITTER_API_SECRET` | Consumer API Secret |
| `TWITTER_ACCESS_TOKEN` | Access Token |
| `TWITTER_ACCESS_TOKEN_SECRET` | Access Token Secret |
| `SHOPEE_AFFILIATE_ID` | ID afiliasi Shopee (default: 11320831661) |

### 4. Deploy

Railway akan otomatis detect `Procfile` dan menjalankan bot sebagai worker process.

## Monitoring Logs

Di Railway dashboard:
1. Buka project → klik service
2. Tab **"Logs"** untuk melihat log real-time
3. Bot akan log setiap aktivitas: scraping, generate konten, posting tweet

## Manual Trigger

### Jalankan semua (scrape + generate + post)

```bash
python main.py --run-now
```

### Jalankan komponen terpisah

```bash
# Scrape produk saja
python shopee_scraper.py

# Generate konten saja
python content_generator.py

# Post tweet berikutnya
python twitter_poster.py
```

## Development Lokal

### 1. Install dependencies

```bash
pip install -r requirements.txt
```

### 2. Setup environment variables

```bash
cp .env.example .env
# Edit .env dengan kredensial kamu
```

### 3. Jalankan bot

```bash
# Mode scheduler (production)
python main.py

# Mode manual (test)
python main.py --run-now
```

## Struktur Project

```
shopee-affiliate-bot/
├── main.py              # Entry point + scheduler
├── shopee_scraper.py    # Component 1: Shopee scraper
├── content_generator.py # Component 2: Tweet generator
├── twitter_poster.py    # Component 3: Twitter poster
├── requirements.txt     # Python dependencies
├── Procfile            # Railway worker process
├── railway.json        # Railway deployment config
├── .env.example        # Template environment variables
├── .gitignore          # Git ignore rules
└── README.md           # Dokumentasi
```

## Tech Stack

- **Python 3.11+**
- **Tweepy** - Twitter API v2
- **APScheduler** - Job scheduling
- **Requests** + **BeautifulSoup4** - Web scraping
- **pytrends** - Google Trends API
- **SQLite** - Local database

## Catatan

- Shopee API bisa berubah sewaktu-waktu. Bot menyediakan mock data sebagai fallback untuk development.
- Rate limit Twitter: max 50 tweets/24 jam (free tier). Jadwal 4x/hari aman dari rate limit.
- Pastikan akun Twitter Developer sudah memiliki akses "Read and Write".
