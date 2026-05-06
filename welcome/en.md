# 👋 Hi! I'm your AI Site Builder

I'm Claude — your personal AI developer in Claude Code Desktop. Ready to build websites from descriptions.

## 0. Pre-flight (one-time before start)

Check that `.env` in the project folder is filled:

✅ `CLOUDFLARE_API_TOKEN` — from [dash.cloudflare.com → API Tokens](https://dash.cloudflare.com/profile/api-tokens)
✅ `CLOUDFLARE_ACCOUNT_ID` — from the Workers & Pages sidebar
✅ `CF_PAGES_PROJECT_NAME` — any kebab-case slug, like `my-first-site`

Leave Namecheap variables empty for now — they're only needed if you want a custom domain (`/domain`).

## What I can do

✅ Build any website from a description or prompt
✅ Adapt design from a reference (photo, link)
✅ Publish to Cloudflare Pages in 30 seconds
✅ Edit elements on the fly

## Commands

| Command | What it does |
|---------|--------------|
| `/status` | Verify Cloudflare credentials |
| `/new-site [description]` | Create a new site in `site/` |
| `/edit [what to change]` | Edit the current site |
| `/deploy` | Publish to Cloudflare Pages |
| `/domain` | Optional: connect a custom domain |

## Let's go

First check setup:
```
/status
```

If everything is ✅, tell me what to build:
```
/new-site Coffee shop landing, minimalist dark style, 3-item menu
```

**Examples:**
- `/new-site Photographer portfolio, warm palette`
- `/new-site Law firm business site, corporate blue`
- `/new-site Product launch page, dark theme, single CTA`

---
*If something goes wrong — just tell me, I'll figure it out.*
