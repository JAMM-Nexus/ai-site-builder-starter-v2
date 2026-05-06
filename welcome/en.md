# 👋 Hi! I'm your AI Site Builder

I'm Claude — your personal AI developer. I'm connected to your GitHub repo and ready to build websites with AI.

## 0. Pre-flight (one-time before start)

Before your first `/new-site` make sure:

✅ **Cloudflare GitHub App** is installed on this repo
   → dash.cloudflare.com → Workers & Pages → Create → Pages → **Connect to Git**

✅ Pages project created (Production branch = `main`, **Build output = `site`**)

⚠️ Cloudflare GitHub App ≠ Anthropic GitHub App. Two separate OAuth flows — both required.

## What I can do

✅ Build any website from a description or prompt
✅ Adapt design from a reference (photo, link)
✅ Publish via `git push` in 30 seconds
✅ Edit elements on the fly

## Commands

| Command | What it does |
|---------|--------------|
| `/new-site [description]` | Create a new website |
| `/edit [what to change]` | Edit the current site |
| `/deploy` | Commit and push (CF auto-rebuilds) |
| `/status` | Check setup |
| `/domain` | Optional: connect a custom domain |

## Let's go!

Check status:
```
/status
```

Or jump straight in:
```
/new-site Coffee shop landing, minimalist dark style, 3-item menu
```

**Examples:**
- `/new-site Photographer portfolio, warm palette`
- `/new-site Law firm business site, corporate blue`
- `/new-site Product launch page, dark theme, single CTA`

---
*If something breaks — just tell me, I'll figure it out.*
