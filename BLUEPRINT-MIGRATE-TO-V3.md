# Blueprint: Migrate AI Site Builder Starter Kit from v2 (single-site) to v3 (multi-project)

> **For existing clients who already installed the kit and built sites in it.**
> Paste this entire file into a fresh Claude Code Desktop session opened in your Starter Kit folder, and let Claude perform the refactor automatically.
> Estimated time: 1–2 minutes. No re-download needed.

---

## What this does

Your current kit has one `site/` folder and one `CF_PAGES_PROJECT_NAME` in `.env` — meaning every `/new-site` overwrites the previous site. v3 replaces that with `projects/<slug>/` — many sites, each in its own folder with its own Cloudflare Pages target. Your **existing site is preserved** and becomes the first project after migration.

---

## Instructions to Claude (this is the actual prompt — Claude reads from here down)

You are about to perform an in-place refactor of an installed AI Site Builder Starter Kit from v2 (single-site) to v3 (multi-project). The user has pasted this Blueprint into a fresh Claude Code Desktop session. The current working directory is the Starter Kit root. Do **not** re-download files — fetch only the canonical v3 files from the public repo and reuse what's already on disk where possible.

### Step 0 — Sanity checks (do this first, stop if anything fails)

1. Confirm you are in a Starter Kit folder by checking that **all** of these exist:
   - `CLAUDE.md`
   - `.env`
   - `scripts/deploy.py`
   - At least one of: `site/`, `site-template/`
2. If any of those is missing → stop and tell the user: *"This doesn't look like a v2 Starter Kit folder. Open Claude Code Desktop in the folder where you have `CLAUDE.md`, `.env`, and `site/`, then re-run the Blueprint."*
3. If `projects/` already exists **and** contains at least one subfolder → tell the user the kit looks like it's already on v3 and ask whether to abort or force-rerun.

### Step 1 — Backup

Create a timestamped backup so the user can roll back:

```
.backup-pre-v3-YYYYMMDD-HHMMSS/
  ├── CLAUDE.md          (current)
  ├── .env               (current — yes including any creds, this stays local)
  ├── site/              (current — full copy)
  ├── site-template/     (current — full copy)
  ├── scripts/           (current — full copy)
  └── welcome/           (current — full copy)
```

Use Bash:
```bash
TS=$(date +%Y%m%d-%H%M%S)
BACKUP=".backup-pre-v3-$TS"
mkdir -p "$BACKUP"
cp -R CLAUDE.md .env scripts welcome "$BACKUP/" 2>/dev/null
[ -d site ] && cp -R site "$BACKUP/"
[ -d site-template ] && cp -R site-template "$BACKUP/"
echo "Backup: $BACKUP"
```

Tell the user where the backup is.

### Step 2 — Determine slug for the existing site

Read `.env` and find `CF_PAGES_PROJECT_NAME`. Logic:
- If non-empty and matches kebab-case (lowercase letters, digits, dashes, 3–40 chars) → use that as the slug for the existing project.
- Otherwise → propose `my-first-site` and ask the user to confirm or override.

Store the chosen slug as `<SLUG>` for the next steps.

### Step 3 — Build new layout

```bash
mkdir -p projects/<SLUG> templates
```

Move existing site files into the new project folder:

```bash
if [ -d site ] && [ -f site/index.html ]; then
  # Copy contents of site/ into projects/<SLUG>/
  cp -R site/. projects/<SLUG>/
fi
```

Move the reference template:

```bash
if [ -d site-template ] && [ ! -d templates/site ]; then
  mv site-template templates/site
fi
```

If `site-template/` was missing entirely (rare), fetch the reference template from the public repo:

```
templates/site/index.html         → https://raw.githubusercontent.com/JAMM-Nexus/ai-site-builder-starter-v2/main/templates/site/index.html
templates/site/_headers           → https://raw.githubusercontent.com/JAMM-Nexus/ai-site-builder-starter-v2/main/templates/site/_headers
templates/site/assets/style.css   → https://raw.githubusercontent.com/JAMM-Nexus/ai-site-builder-starter-v2/main/templates/site/assets/style.css
```

Use Bash `curl -fsSL <url> -o <path>` to fetch each.

### Step 4 — Write per-project metadata

Create `projects/<SLUG>/.project.json` with:

```json
{
  "slug": "<SLUG>",
  "type": "site",
  "cf_project_name": "<SLUG>",
  "domain": null,
  "created": "<today YYYY-MM-DD>"
}
```

If the user's `.env` had a populated `DOMAIN` field, set `"domain"` to that value.
If `CF_PAGES_PROJECT_NAME` in `.env` was different from `<SLUG>` (rare — e.g. user manually set a slug-incompatible CF project name), keep `cf_project_name` equal to the **original `CF_PAGES_PROJECT_NAME` value**, not the new slug — this ensures the next `/deploy` still hits the same Cloudflare Pages target as before.

### Step 5 — Set active project

```bash
echo "<SLUG>" > projects/.active
```

### Step 6 — Replace orchestrator and helper files (fetch from public repo)

Overwrite these files in place with v3 versions from the public repo. Use `curl -fsSL` for each:

| Path | Source |
|------|--------|
| `CLAUDE.md` | `https://raw.githubusercontent.com/JAMM-Nexus/ai-site-builder-starter-v2/main/CLAUDE.md` |
| `README.md` | `https://raw.githubusercontent.com/JAMM-Nexus/ai-site-builder-starter-v2/main/README.md` |
| `welcome/uk.md` | `https://raw.githubusercontent.com/JAMM-Nexus/ai-site-builder-starter-v2/main/welcome/uk.md` |
| `welcome/ru.md` | `https://raw.githubusercontent.com/JAMM-Nexus/ai-site-builder-starter-v2/main/welcome/ru.md` |
| `welcome/en.md` | `https://raw.githubusercontent.com/JAMM-Nexus/ai-site-builder-starter-v2/main/welcome/en.md` |
| `welcome/es.md` | `https://raw.githubusercontent.com/JAMM-Nexus/ai-site-builder-starter-v2/main/welcome/es.md` |
| `scripts/deploy.py` | `https://raw.githubusercontent.com/JAMM-Nexus/ai-site-builder-starter-v2/main/scripts/deploy.py` |
| `scripts/new_project.py` | `https://raw.githubusercontent.com/JAMM-Nexus/ai-site-builder-starter-v2/main/scripts/new_project.py` |
| `scripts/list_projects.py` | `https://raw.githubusercontent.com/JAMM-Nexus/ai-site-builder-starter-v2/main/scripts/list_projects.py` |
| `scripts/check_setup.py` | `https://raw.githubusercontent.com/JAMM-Nexus/ai-site-builder-starter-v2/main/scripts/check_setup.py` |
| `scripts/setup_domain.py` | `https://raw.githubusercontent.com/JAMM-Nexus/ai-site-builder-starter-v2/main/scripts/setup_domain.py` |
| `.gitignore` | `https://raw.githubusercontent.com/JAMM-Nexus/ai-site-builder-starter-v2/main/.gitignore` |

### Step 7 — Clean .env

Leave **all existing values** as the user had them (especially Cloudflare and Namecheap creds — they stay valid). The only change: the line `CF_PAGES_PROJECT_NAME=<value>` is no longer used in v3 (project name now lives in `projects/<slug>/.project.json`). Do **not** delete it automatically — v3 scripts ignore it gracefully and will print a one-time hint on `/status`. Tell the user they can remove that line manually when convenient.

If the user's `.env` has `DOMAIN=...` populated and you already copied it into the project's `.project.json` in Step 4, mention to the user that `DOMAIN` can also be removed from `.env` (it's now per-project).

### Step 8 — Remove now-empty old folders

```bash
[ -d site ] && rmdir site 2>/dev/null  # only removes if empty (it should be — content moved)
```

If `site/` is not empty for any reason, leave it and tell the user.

### Step 9 — Verify

Run the new status script and the new list script:

```bash
python3 scripts/check_setup.py
python3 scripts/list_projects.py
```

Confirm output contains:
- `✅` for Cloudflare creds
- `<SLUG>` listed under "Projects" with the `★` active marker

### Step 10 — Final report to user

Tell the user, in their language (UK by default — check chat language first):

> Migration done. Your previous site is now at `projects/<SLUG>/` and is set as active. Backup of the old layout is at `.backup-pre-v3-<TS>/` — keep it for a few days, then delete.
>
> Try:
> - `/list` — see all your sites
> - `/new-site <new-slug> <description>` — build another site (the first one stays untouched)
> - `/deploy` — re-deploy the migrated site to verify the Cloudflare URL still works
>
> If anything looks wrong, restore from `.backup-pre-v3-<TS>/` and tell me what failed.

### Rules

- **Do not** print contents of `.env` in chat.
- **Do not** delete the backup folder for the user — they decide when.
- **Do not** modify Cloudflare or Namecheap accounts via API in this migration. Pure local refactor.
- If any step fails (curl 404, missing file, write permission), stop immediately, report exactly which step failed and which file, and **do not** proceed further. The backup is the user's rollback path.
