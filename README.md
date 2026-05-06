# AI Site Builder — Starter Kit

> Build any website in minutes using Claude Code Desktop + Cloudflare Pages.
> Course: [create-your-ai.site](https://create-your-ai.site)

---

## Quick Start

### 1. Get Claude Pro
[claude.ai](https://claude.ai) → Sign up → Subscribe to Claude Pro ($20/mo).
Required for Claude Code Desktop access.

### 2. Download this Starter Kit
On this GitHub page click **Code** (green button) → **Download ZIP**.
Extract to a convenient folder, e.g. `~/Documents/ai-site-builder/`.

### 3. Install Claude Code Desktop
Download from [claude.ai/download](https://claude.ai/download) → install for your OS (macOS / Windows / Linux).
Open Claude Code Desktop → "Open folder" → select your extracted Starter Kit folder.

### 4. Get Cloudflare credentials
- Sign up at [cloudflare.com](https://cloudflare.com) (free).
- [API Token](https://dash.cloudflare.com/profile/api-tokens): Create Token → "Edit Cloudflare Workers" template → Continue → Create Token. Copy the value.
- Account ID: [dash.cloudflare.com](https://dash.cloudflare.com) → Workers & Pages → right sidebar → Account ID. Copy.

### 5. Fill `.env`
Open `.env` in the Starter Kit folder. Fill 3 values:
```
CLOUDFLARE_API_TOKEN=<your token>
CLOUDFLARE_ACCOUNT_ID=<your account id>
CF_PAGES_PROJECT_NAME=my-first-site
```

(Leave Namecheap fields empty — they're only needed for `/domain` command.)

### 6. Build a site
In Claude Code Desktop chat:
```
/new-site Coffee shop landing, dark style, 3-item menu
```

### 7. Publish
```
/deploy
```

Wrangler runs locally, deploys `site/` folder to Cloudflare Pages.
~30 seconds → live on `https://my-first-site.pages.dev`.

---

## Commands

| Command | Description |
|---------|-------------|
| `/new-site [description]` | Build a new website |
| `/edit [what to change]` | Modify the current site |
| `/deploy` | Publish to Cloudflare Pages via wrangler |
| `/status` | Verify Cloudflare credentials work |
| `/domain` | Optional: connect a custom domain (requires Namecheap creds) |

---

## Custom domain (optional)

If you want `mysite.com` instead of `mysite.pages.dev`:
1. Buy a domain at [namecheap.com](https://namecheap.com).
2. Get Namecheap API key: Profile → Tools → API Access → enable + whitelist your IP.
3. Fill `NAMECHEAP_*` and `DOMAIN` in `.env`.
4. Run `/domain` in Claude Code Desktop.

Without this — your site lives on the free `*.pages.dev` URL forever, with HTTPS.

---

## Files

- `site/` — your generated website (deploys to Cloudflare)
- `site-template/` — reference template Claude uses for `/new-site`
- `welcome/` — Claude's multilingual greeting (uk/ru/en/es)
- `scripts/` — Python helpers (auto-install dependencies on first run)
- `CLAUDE.md` — instructions for the Claude agent
- `.env` — your credentials (never commit)

---

## Support

- Telegram bot: [@your_ai_site_bot](https://t.me/your_ai_site_bot)
- Course: [create-your-ai.site](https://create-your-ai.site)
