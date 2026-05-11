# AI Site Builder — Starter Kit (Multi-Project)

> Build **many** websites and projects in minutes using Claude Code Desktop + Cloudflare Pages.
> Each project lives in its own folder. Switch between them with one command.
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
Open `.env` in the Starter Kit folder. Fill 2 values (these are **global** — used for every project you create):
```
CLOUDFLARE_API_TOKEN=<your token>
CLOUDFLARE_ACCOUNT_ID=<your account id>
```

(Leave Namecheap fields empty — they're only needed for `/domain` command.)

### 6. Build your first site
In Claude Code Desktop chat:
```
/new-site coffee-shop Coffee shop landing, dark style, 3-item menu
```

Files appear at `projects/coffee-shop/`.

### 7. Publish
```
/deploy
```

Wrangler runs locally, deploys `projects/coffee-shop/` to Cloudflare Pages.
~30 seconds → live on `https://coffee-shop.pages.dev`.

### 8. Build a second site
```
/new-site portfolio Photographer portfolio, warm palette, gallery first
/deploy
```

That's it. `coffee-shop` is untouched. Both live in parallel on separate Pages projects.

---

## Commands

| Command | Description |
|---------|-------------|
| `/new-site <slug> [description]` | Create a new website at `projects/<slug>/` |
| `/new-project <slug> [description]` | Create a generic project folder (not only website) |
| `/edit [slug] [what to change]` | Modify a project (active project if slug omitted) |
| `/deploy [slug]` | Publish project to Cloudflare Pages |
| `/list` | List all projects with live URLs |
| `/use <slug>` | Switch active project |
| `/status` | Verify credentials + show projects |
| `/domain [slug]` | Optional: connect a custom domain to a specific project |

**Slug** is a kebab-case identifier (`coffee-shop`, `portfolio`, `cafe-landing`). Each slug becomes:
1. The folder name under `projects/`
2. The Cloudflare Pages project name (so the URL is `https://<slug>.pages.dev`)

If you don't pass a slug, Claude generates one from the description and shows it to you before creating.

---

## Custom domain (optional)

If you want `mysite.com` instead of `mysite.pages.dev`:
1. Buy a domain at [namecheap.com](https://namecheap.com).
2. Get Namecheap API key: Profile → Tools → API Access → enable + whitelist your IP.
3. Fill `NAMECHEAP_*` and `DOMAIN` in `.env`.
4. Run `/domain <slug>` in Claude Code Desktop.

Each project can have its own domain.

Without this — your sites live on the free `*.pages.dev` URLs forever, with HTTPS.

---

## Migrating from v2 (single-site layout)

If you already used a previous version of this kit (with one `site/` folder), don't worry — Claude will offer to migrate your existing site to the new `projects/<slug>/` structure on first command. Just say "yes" when asked.

For a manual migration in your already-installed kit folder, use the migration prompt: see `BLUEPRINT-MIGRATE-TO-V3.md` in the repo.

---

## Files

- `projects/<slug>/` — each project lives here (HTML, CSS, JS, assets)
- `projects/<slug>/.project.json` — project metadata (cf project name, domain, etc.)
- `projects/.active` — pointer to the currently active project
- `templates/site/` — reference template Claude uses for `/new-site`
- `welcome/` — Claude's multilingual greeting (uk/ru/en/es)
- `scripts/` — Python helpers (auto-install dependencies on first run)
- `CLAUDE.md` — instructions for the Claude agent
- `.env` — your global credentials (never commit)

---

## Support

- Telegram bot: [@your_ai_site_bot](https://t.me/your_ai_site_bot)
- Course: [create-your-ai.site](https://create-your-ai.site)
