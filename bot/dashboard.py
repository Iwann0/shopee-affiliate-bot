"""Flask web dashboard for Twitter Growth Research Bot."""

import json
import logging
import os
import threading

from flask import Flask, jsonify, render_template, request

from bot.accounts import (
    get_my_profile,
    suggest_accounts_to_follow,
    suggest_follow_strategy,
)
from bot.analytics import get_growth_summary
from bot.config import Config
from bot.content import generate_tweet_drafts
from bot.trending import get_all_trends
from bot.twitter_client import create_client

logger = logging.getLogger(__name__)

app = Flask(
    __name__,
    template_folder=os.path.join(os.path.dirname(__file__), "..", "templates"),
    static_folder=os.path.join(os.path.dirname(__file__), "..", "static"),
)

_client = None
_client_lock = threading.Lock()


def _get_client():
    global _client
    with _client_lock:
        if _client is None:
            _client = create_client()
        return _client


@app.route("/")
def index():
    return render_template("dashboard.html")


@app.route("/api/profile")
def api_profile():
    try:
        client = _get_client()
        profile = get_my_profile(client)
        if profile:
            tips = suggest_follow_strategy(profile)
            profile["tips"] = tips
            return jsonify(profile)
        return jsonify({"error": "Could not fetch profile"}), 500
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/trends")
def api_trends():
    try:
        trends = get_all_trends()
        return jsonify(trends)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/drafts")
def api_drafts():
    try:
        topics = request.args.getlist("topics")
        count = int(request.args.get("count", Config.DRAFT_COUNT))
        drafts = generate_tweet_drafts(
            topics=topics if topics else None,
            count=count,
        )
        return jsonify(drafts)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/accounts")
def api_accounts():
    try:
        suggestions = suggest_accounts_to_follow()
        return jsonify(suggestions)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/analytics")
def api_analytics():
    try:
        analytics_file = Config.ANALYTICS_FILE
        history = []
        if os.path.exists(analytics_file):
            with open(analytics_file) as f:
                history = json.load(f)

        summary = get_growth_summary()
        return jsonify({"history": history, "summary": summary})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/settings", methods=["GET"])
def api_get_settings():
    return jsonify({
        "niche_keywords": Config.NICHE_KEYWORDS,
        "draft_count": Config.DRAFT_COUNT,
        "engage_interval": Config.ENGAGE_INTERVAL_MINUTES,
        "post_interval": Config.POST_INTERVAL_MINUTES,
        "analytics_interval": Config.ANALYTICS_INTERVAL_MINUTES,
    })


@app.route("/api/settings", methods=["POST"])
def api_update_settings():
    try:
        data = request.get_json()
        if "niche_keywords" in data:
            keywords = data["niche_keywords"]
            if isinstance(keywords, str):
                keywords = [kw.strip() for kw in keywords.split(",")]
            Config.NICHE_KEYWORDS = keywords

        if "draft_count" in data:
            Config.DRAFT_COUNT = int(data["draft_count"])

        return jsonify({"status": "ok", "settings": {
            "niche_keywords": Config.NICHE_KEYWORDS,
            "draft_count": Config.DRAFT_COUNT,
        }})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


def run_dashboard(host: str = "0.0.0.0", port: int = 5000) -> None:
    """Start the Flask dashboard server."""
    errors = Config.validate()
    if errors:
        for err in errors:
            logger.error("Config error: %s", err)
        raise SystemExit(1)

    logger.info("Starting dashboard at http://localhost:%d", port)
    app.run(host=host, port=port, debug=False)
