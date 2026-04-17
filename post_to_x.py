"""
X Finance Bot
Posts 3x daily: 8 AM IST (pre-written), 12 PM IST (calculator promo), 6 PM IST (AI-generated)
"""

import os
import json
import sys
import tweepy
from groq import Groq
from datetime import datetime

# ── Credentials (set as GitHub Secrets) ──────────────────────────────────────
x_client = tweepy.Client(
    consumer_key=os.environ["X_API_KEY"],
    consumer_secret=os.environ["X_API_SECRET"],
    access_token=os.environ["X_ACCESS_TOKEN"],
    access_token_secret=os.environ["X_ACCESS_TOKEN_SECRET"],
)

groq_client = Groq(api_key=os.environ["GROQ_API_KEY"])

# ── Post Generators ───────────────────────────────────────────────────────────

def get_scheduled_post() -> str:
    """Pick a pre-written post by rotating through posts.json using the day of year."""
    with open("posts.json", "r") as f:
        posts = json.load(f)
    day_index = datetime.utcnow().timetuple().tm_yday
    post = posts[day_index % len(posts)]
    print(f"📋 Using pre-written post #{day_index % len(posts) + 1}")
    return post["text"]


def ask_groq(prompt: str) -> str:
    """Send a prompt to Groq and return the response text."""
    response = groq_client.chat.completions.create(
        model="llama-3.1-8b-instant",
        max_tokens=200,
        messages=[{"role": "user", "content": prompt}],
    )
    text = response.choices[0].message.content.strip()
    text = text.strip('"').strip("'")
    return text


def get_ai_post() -> str:
    """Generate a fresh finance post using Groq."""
    topics = [
        "budgeting and saving habits for salaried Indians",
        "stock market and mutual fund investing principles",
        "wealth-building mindset for Indian millennials",
        "passive income strategies relevant to India",
        "personal finance mistakes Indians commonly make",
        "compound interest and long-term SIP thinking",
        "financial independence and early retirement in India",
    ]
    topic = topics[datetime.utcnow().weekday()]

    return ask_groq(
        f"Write a short X (Twitter) post about: {topic}.\n\n"
        "Format:\n"
        "- Line 1: A short relatable observation or hook (max 80 chars)\n"
        "- Line 2: blank\n"
        "- Line 3-4: The insight or advice in 1-2 short lines\n\n"
        "Rules:\n"
        "- Total post must be under 260 characters including line breaks\n"
        "- Sound like a real person sharing genuine advice, not a corporate account\n"
        "- Use Indian context: ₹, SIP, FD, EMI, Nifty, CIBIL where relevant\n"
        "- No hashtags, no emojis, no filler like 'Remember:' or 'Pro tip:'\n"
        "- Return ONLY the post text, nothing else"
    )


def get_calculator_promo_post() -> str:
    """Generate a daily promo post for the Financial Fitness Calculator."""
    angles = [
        "most Indians don't know their actual financial health score",
        "the gap between feeling financially okay and being financially fit",
        "the specific metrics that determine financial fitness: savings rate, debt ratio, net worth",
        "how quickly your financial situation can change when you start measuring it",
        "why tracking financial fitness is like tracking physical fitness",
        "the blind spots Indians have about their own finances",
        "how knowing your numbers is the first step to changing them",
    ]
    angle = angles[datetime.utcnow().weekday()]

    raw = ask_groq(
        f"Write an X (Twitter) post promoting a free Financial Fitness Calculator.\n\n"
        f"Today's angle: {angle}\n\n"
        "The calculator helps Indians measure financial health: savings rate, debt ratio, emergency fund, net worth.\n\n"
        "Format:\n"
        "- Line 1: A short relatable hook (max 80 chars)\n"
        "- Line 2: blank\n"
        "- Line 3: One line expanding on the hook (max 100 chars)\n"
        "- Line 4: blank\n"
        "- Line 5: Check your financial fitness →\n"
        "- Line 6: https://financialfitnesscalculator.com/\n\n"
        "Rules:\n"
        "- Total post must be under 280 characters including line breaks\n"
        "- Sound like a real person, not an ad\n"
        "- No hashtags, no emojis\n"
        "- Return ONLY the post text, nothing else"
    )

    # Safety net: ensure CTA is always present even if AI drops it
    CTA = "\nCheck your financial fitness →\nhttps://financialfitnesscalculator.com/"
    if "financialfitnesscalculator.com" not in raw:
        lines = [l for l in raw.strip().split("\n") if l.strip()]
        hook = lines[0][:80].strip()
        body = lines[1][:100].strip() if len(lines) > 1 else ""
        return hook + ("\n\n" + body if body else "") + CTA

    # Trim if still too long
    if len(raw) > 280:
        lines = raw.strip().split("\n")
        hook = lines[0][:80].strip()
        return hook + CTA

    return raw


# ── Post to X ─────────────────────────────────────────────────────────────────

def post_to_x(text: str) -> None:
    if len(text) > 280:
        print(f"⚠️  Post too long ({len(text)} chars), trimming hook...")
        CTA = "\nCheck your financial fitness →\nhttps://financialfitnesscalculator.com/"
        if CTA in text:
            hook = text.replace(CTA, "")
            allowed = 280 - len(CTA)
            text = hook[:allowed].strip() + CTA
        else:
            text = text[:277] + "..."

    response = x_client.create_tweet(text=text)
    tweet_id = response.data["id"]
    print(f"✅ Posted! Tweet ID: {tweet_id}")
    print(f"📝 Content ({len(text)} chars):\n{text}")


# ── Entry Point ───────────────────────────────────────────────────────────────

if __name__ == "__main__":
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
