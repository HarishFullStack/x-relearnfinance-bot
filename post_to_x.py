"""
X Finance Bot
Posts 2x daily: 8 AM EST (pre-written) and 6 PM EST (AI-generated)
"""

import os
import json
import sys
import tweepy
import google.generativeai as genai
from datetime import datetime

# ── Credentials (set as GitHub Secrets) ──────────────────────────────────────
x_client = tweepy.Client(
    consumer_key=os.environ["X_API_KEY"],
    consumer_secret=os.environ["X_API_SECRET"],
    access_token=os.environ["X_ACCESS_TOKEN"],
    access_token_secret=os.environ["X_ACCESS_TOKEN_SECRET"],
)

genai.configure(api_key=os.environ["GEMINI_API_KEY"])
gemini = genai.GenerativeModel("gemini-1.5-pro")

# ── Post Generators ───────────────────────────────────────────────────────────

def get_scheduled_post() -> str:
    """Pick a pre-written post by rotating through posts.json using the day of year."""
    with open("posts.json", "r") as f:
        posts = json.load(f)
    day_index = datetime.utcnow().timetuple().tm_yday
    post = posts[day_index % len(posts)]
    print(f"📋 Using pre-written post #{day_index % len(posts) + 1}")
    return post["text"]


def get_ai_post() -> str:
    """Generate a fresh finance post using Gemini."""
    topics = [
        "budgeting and saving habits",
        "stock market investing principles",
        "wealth-building mindset",
        "passive income strategies",
        "personal finance mistakes to avoid",
        "compound interest and long-term thinking",
        "financial independence / FIRE movement",
    ]
    topic = topics[datetime.utcnow().weekday()]

    prompt = (
        f"Write a single X (Twitter) post about: {topic}.\n\n"
        "Rules:\n"
        "- Under 270 characters\n"
        "- Insightful, punchy, or thought-provoking\n"
        "- No hashtags\n"
        "- Conversational but authoritative tone\n"
        "- No filler phrases like 'Remember:' or 'Pro tip:'\n"
        "- Return ONLY the post text, nothing else"
    )
    response = gemini.generate_content(prompt)
    return response.text.strip()


def get_calculator_promo_post() -> str:
    """Generate a daily promo post for the Financial Fitness Calculator."""
    angles = [
        "most people don't know their actual financial health score",
        "the gap between feeling financially okay and being financially fit",
        "the specific metrics that determine financial fitness (savings rate, debt ratio, net worth)",
        "how quickly your financial situation can change when you measure it",
        "why tracking financial fitness is like tracking physical fitness",
        "the blind spots people have about their own finances",
        "how knowing your numbers is the first step to changing them",
    ]
    angle = angles[datetime.utcnow().weekday()]

    CTA_URL = "https://financialfitnesscalculator.com/"
    CTA_TEXT = "Check your financial fitness →"

    prompt = (
        f"Write an X (Twitter) post promoting a free Financial Fitness Calculator.\n\n"
        f"Today's angle: {angle}\n\n"
        "The calculator helps people measure their financial health across key metrics "
        "like savings rate, debt-to-income ratio, emergency fund, and net worth.\n\n"
        "Rules:\n"
        f"- End with this exact CTA on a new line: {CTA_TEXT}\n"
        f"- Then the URL on its own line: {CTA_URL}\n"
        "- The text before the CTA must be under 200 characters\n"
        "- Hook-driven opening — make people feel the gap or the curiosity\n"
        "- No hashtags, no emojis unless one fits naturally\n"
        "- Conversational, not salesy\n"
        "- Return ONLY the post text, nothing else"
    )
    response = gemini.generate_content(prompt)
    return response.text.strip()


# ── Post to X ─────────────────────────────────────────────────────────────────

def post_to_x(text: str) -> None:
    if len(text) > 280:
        print(f"⚠️  Post too long ({len(text)} chars), truncating...")
        text = text[:277] + "..."

    response = x_client.create_tweet(text=text)
    tweet_id = response.data["id"]
    print(f"✅ Posted! Tweet ID: {tweet_id}")
    print(f"📝 Content: {text}")


# ── Entry Point ───────────────────────────────────────────────────────────────

if __name__ == "__main__":
    # POST_TYPE options: "scheduled" | "ai" | "calculator"
    post_type = os.environ.get("POST_TYPE", "scheduled")

    print(f"🚀 Running X Finance Bot — mode: {post_type}")

    if post_type == "scheduled":
        content = get_scheduled_post()
    elif post_type == "ai":
        content = get_ai_post()
    elif post_type == "calculator":
        content = get_calculator_promo_post()
    else:
        print(f"❌ Unknown POST_TYPE: {post_type}")
        sys.exit(1)

    post_to_x(content)
