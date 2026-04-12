# X Finance Bot 🤖

Automatically posts 3x daily finance content to X using GitHub Actions. 100% free — no paid APIs required.

| Time | Type | Source |
|------|------|--------|
| 8:00 AM EST | Pre-written insight | Rotates through `posts.json` (30 posts) |
| 12:00 PM EST | Calculator promo | Gemini rewrites a fresh CTA post daily |
| 6:00 PM EST | AI-generated insight | Gemini generates fresh finance content daily |

---

## Setup (5 steps)

### 1. Create a new GitHub repo and push these files
- Go to [github.com](https://github.com) → **New repository** → name it `x-finance-bot`
- Upload all files maintaining this structure:
```
x-finance-bot/
├── post_to_x.py
├── posts.json
├── requirements.txt
└── .github/
    └── workflows/
        └── tweet.yml
```

### 2. Get your X API credentials
- Go to [developer.x.com](https://developer.x.com)
- Create a **Free tier** account → New Project → New App
- Set app permissions to **Read and Write**
- Generate: API Key, API Secret, Access Token, Access Token Secret

### 3. Get your free Gemini API key
- Go to [aistudio.google.com](https://aistudio.google.com)
- Click **Get API Key → Create API Key**
- No credit card or payment required

### 4. Add secrets to GitHub
Go to your repo → **Settings → Secrets and variables → Actions → New repository secret**

Add all 5 secrets:

| Secret Name | Where to get it |
|---|---|
| `X_API_KEY` | X Developer Portal |
| `X_API_SECRET` | X Developer Portal |
| `X_ACCESS_TOKEN` | X Developer Portal |
| `X_ACCESS_TOKEN_SECRET` | X Developer Portal |
| `GEMINI_API_KEY` | aistudio.google.com |

### 5. Enable GitHub Actions
Go to the **Actions tab** in your repo → click **Enable workflows**

---

## Testing manually
Go to **Actions → X Finance Bot → Run workflow**, pick a post type (`scheduled`, `calculator`, or `ai`), and click **Run workflow**.

---

## Customizing posts
Edit `posts.json` to add or change pre-written posts. The bot selects posts by day of year (loops back after 30 days), so you can add as many as you like.
