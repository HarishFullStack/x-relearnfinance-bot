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


def ask_groq(prompt: str, max_tokens: int = 300) -> str:
    response = groq_client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=max_tokens,   # ← make sure this is wired up
        temperature=0.8,
    )
    return response.choices[0].message.content.strip()

def get_ai_post() -> str:
    """Generate a trend-aware finance post using Groq."""
    return ask_groq(
        "You are a personal finance content creator for salaried Indians aged 22–40.\n\n"
        "Step 1 — Think about what is trending or being widely discussed in India RIGHT NOW:\n"
        "Consider recent news, market events, RBI/SEBI decisions, Budget updates, IPO activity,\n"
        "viral social media topics, cricket, Bollywood, jobs/layoffs, or any cultural moment\n"
        "that Indians are actively talking about on X (Twitter) today.\n\n"
        "Step 2 — Pick the ONE trending topic that can be most naturally connected\n"
        "to a personal finance lesson. If nothing connects cleanly, use a strong\n"
        "evergreen Indian finance angle instead.\n\n"
        "Step 3 — Write the X (Twitter) post.\n\n"
        "Format:\n"
        "- Line 1: Hook that ties the trend to a money truth (max 85 chars)\n"
        "- Line 2: blank\n"
        "- Lines 3–4: The finance insight in 1–2 punchy lines\n"
        "- Line 5: blank\n"
        "- Line 6: One punchy closing line that reinforces the lesson (max 60 chars)\n\n"
        "Rules:\n"
        "- Total post must be BETWEEN 220 and 260 characters including line breaks\n"
        "- You MUST write all 6 lines — do not stop early\n"
        "- Sound like a real person, not a brand account\n"
        "- Use Indian context: ₹, SIP, EMI, FD, Nifty, CIBIL where relevant\n"
        "- No hashtags, no emojis, no filler like 'Remember:' or 'Pro tip:'\n"
        "- Do NOT mention the trend awkwardly — weave it in naturally\n"
        "- Return ONLY the final post text, nothing else",
        max_tokens=300
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
        "Format (follow exactly, nothing more):\n"
        "Line 1: Hook — one sentence, max 60 characters\n"
        "Line 2: blank\n"
        "Line 3: One sentence expanding the hook, max 80 characters\n\n"
        "Rules:\n"
        "- Write ONLY lines 1 and 3 — do not add CTA or URL, that is added automatically\n"
        "- Total of your response must be under 150 characters\n"
        "- ONE sentence per line only, no lists, no paragraphs\n"
        "- Sound like a real person noticing something, not an ad\n"
        "- No hashtags, no emojis\n"
        "- Return ONLY the two lines, nothing else"
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
