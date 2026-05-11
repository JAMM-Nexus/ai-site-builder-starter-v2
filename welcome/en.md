# 👋 Hi! I'm your AI Site Builder

I'm Claude — your personal AI developer in Claude Code Desktop. Ready to build **any number** of websites and projects from descriptions. Each project lives in its own folder and deploys independently.

## 0. Pre-flight (one-time before start)

Check that `.env` in the project folder is filled:

✅ `CLOUDFLARE_API_TOKEN` — from [dash.cloudflare.com → API Tokens](https://dash.cloudflare.com/profile/api-tokens)
✅ `CLOUDFLARE_ACCOUNT_ID` — from the Workers & Pages sidebar

These are **global** credentials — set them once, they work for all your sites.

Leave Namecheap variables empty — only needed for custom domains (`/domain`).

## What I can do

✅ Build any website or project from a description
✅ Keep **multiple** sites in parallel under `projects/<slug>/`
✅ Adapt design from a reference (photo, link)
✅ Publish any site to Cloudflare Pages in 30 seconds
✅ Edit elements on the fly
✅ Switch between sites with `/use <slug>`

## Commands

| Command | What it does |
|---------|--------------|
| `/status` | Verify credentials + list your projects |
| `/new-site <slug> [description]` | Create a new site at `projects/<slug>/` |
| `/edit [slug] [what to change]` | Edit a site (active project if slug omitted) |
| `/deploy [slug]` | Publish to Cloudflare Pages |
| `/list` | Show all your sites + URLs |
| `/use <slug>` | Make a project active |
| `/domain [slug]` | Optional: connect a custom domain |

## Let's go

First check setup:
```
/status
```

If everything is ✅, tell me what to build. **Slug** = short kebab-case name (`coffee-shop`, `portfolio`, `cafe-landing`):

```
/new-site cafe-landing Coffee shop landing, minimalist dark style, 3-item menu
```

**Examples:**
- `/new-site portfolio Photographer portfolio, warm palette`
- `/new-site law-firm Law firm business site, corporate blue`
- `/new-site product-launch Product launch page, dark theme, single CTA`

## Second, third, hundredth site

Just create another — earlier ones stay intact:
```
/new-site portfolio Photographer portfolio
/deploy
```

`/list` shows everything. `/use <slug>` switches the active one.

---
*If something goes wrong — just tell me, I'll figure it out.*
