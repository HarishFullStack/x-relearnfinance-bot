# X Finance Bot 🤖

Automatically posts 2x daily finance content to X using GitHub Actions.

| Time | Type | Source |
|------|------|--------|
| 8:00 AM EST | Pre-written | Rotates through `posts.json` (30 posts) |
| 6:00 PM EST | AI-generated | Claude generates fresh content daily |

---

## Setup (5 steps)

### 1. Fork or clone this repo to your GitHub

### 2. Get your X API credentials
- Go to [developer.x.com](https://developer.x.com)
- Create a Free tier account → New Project → New App
- Set permissions to **Read and Write**
- Generate: API Key, API Secret, Access Token, Access Token Secret

### 3. Get your Anthropic API key
- Go to [console.anthropic.com](https://console.anthropic.com)
- Create an API key

### 4. Add secrets to GitHub
Go to your repo → **Settings → Secrets and variables → Actions → New repository secret**

Add all 5 secrets:

| Secret Name | Where to get it |
|---|---|
| `X_API_KEY` | X Developer Portal |
| `X_API_SECRET` | X Developer Portal |
| `X_ACCESS_TOKEN` | X Developer Portal |
| `X_ACCESS_TOKEN_SECRET` | X Developer Portal |
| `ANTHROPIC_API_KEY` | console.anthropic.com |

### 5. Enable GitHub Actions
Go to **Actions tab** in your repo → Enable workflows

---

## Testing manually
Go to **Actions → X Finance Bot → Run workflow** and pick `scheduled` or `ai`.

---

## Customizing posts
Edit `posts.json` to add/change pre-written posts. The bot rotates through them by day of year, so order matters for scheduling.
