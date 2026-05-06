# AI Site Builder — Starter Kit v2

> Build any website in minutes using Claude Code Web + GitHub + Cloudflare Pages.
> Course: [create-your-ai.site](https://create-your-ai.site)

---

## Quick Start (5 minutes)

### 1. Import this repository
- [github.com/new/import](https://github.com/new/import)
- Clone URL: `https://github.com/JAMM-Automation/ai-site-builder-starter-v2`
- Repository name: `my-first-ai-site` (or any other)
- Visibility: **Private** (recommended)
- Click **Begin import**

### 2. Connect Cloudflare Pages
- [dash.cloudflare.com](https://dash.cloudflare.com) → Workers & Pages → Create → Pages → **Connect to Git**
- Install **Cloudflare GitHub App** → grant access to your imported repo
- Production branch: `main`, **Build output directory: `site`**, Build command: (empty)
- Save and Deploy → first build runs automatically

### 3. Connect Claude Code Web
- [claude.ai/code](https://claude.ai/code) → New project → Connect GitHub
- Select your imported repo → Authorize Anthropic
- Open the project — Claude greets you in your language

### 4. Build a site
In Claude Code Web chat:
```
/new-site Лендинг для кав'ярні, темний стиль, меню з 3 позиціями
```

### 5. Publish
```
/deploy
```

`git push` → Cloudflare auto-rebuilds → ~30 seconds → live on `<your-project>.pages.dev`.

---

## Commands

| Command | Description |
|---------|-------------|
| `/new-site [description]` | Build a new website |
| `/edit [what to change]` | Modify the current site |
| `/deploy` | Push `site/` to GitHub (CF rebuilds automatically) |
| `/status` | Check connections |
| `/domain` | Optional: connect a custom domain via Namecheap + CF |

---

## Optional: Custom Domain

For `/domain` you need:
1. Copy `.env.example` to `.env`
2. Fill in `CLOUDFLARE_API_TOKEN`, `CLOUDFLARE_ACCOUNT_ID`, `NAMECHEAP_*`, `DOMAIN`
3. Run `/domain` in Claude Code Web

Without `.env`, the basic flow (build + publish on `*.pages.dev`) works fine — no API tokens needed.

---

## How it works

```
Claude Code Web
   │
   ├─ writes site/ → git push origin main
   │
   ▼
GitHub repo (your private copy of starter v2)
   │
   ├─ webhook fires
   │
   ▼
Cloudflare Pages
   │
   └─ rebuild → publish to <project>.pages.dev (HTTPS auto)
```

No local Python, no wrangler, no local API tokens. Everything in browser.

---

## Files

- `site/` — deployable HTML/CSS/JS (this is what Cloudflare publishes)
- `site-template/` — reference template (NOT deployed)
- `welcome/` — multilingual greetings (uk/ru/en/es)
- `scripts/` — optional Python helpers (auto-install deps when run)
- `CLAUDE.md` — instructions for Claude Code agent
- `.env.example` — secrets template (only needed for `/domain`)

---

## Support

- Telegram bot: [@your_ai_site_bot](https://t.me/your_ai_site_bot)
- Course: [create-your-ai.site](https://create-your-ai.site)
