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
        model="llama3-8b-8192",
        max_tokens=200,
        messages=[{"role": "user", "content": prompt}],
    )
    return response.choices[0].message.content.strip()


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
        f"Write a single X (Twitter) post about: {topic}.\n\n"
        "Rules:\n"
        "- Under 270 characters\n"
        "- Insightful, punchy, or thought-provoking\n"
        "- Use Indian context: ₹, SIP, FD, EMI, Nifty, CIBIL where relevant\n"
        "- No hashtags\n"
        "- Conversational but authoritative tone\n"
        "- No filler phrases like 'Remember:' or 'Pro tip:'\n"
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

    return ask_groq(
        f"Write an X (Twitter) post promoting a free Financial Fitness Calculator.\n\n"
        f"Today's angle: {angle}\n\n"
        "The calculator helps people measure their financial health across key metrics "
        "like savings rate, debt-to-income ratio, emergency fund, and net worth.\n\n"
        "Rules:\n"
        "- End with this exact CTA on a new line: Check your financial fitness →\n"
        "- Then the URL on its own line: https://financialfitnesscalculator.com/\n"
        "- The text before the CTA must be under 200 characters\n"
        "- Hook-driven opening — make people feel the gap or the curiosity\n"
        "- Use Indian context where relevant\n"
        "- No hashtags. Conversational, not salesy.\n"
        "- Return ONLY the post text, nothing else"
    )


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
