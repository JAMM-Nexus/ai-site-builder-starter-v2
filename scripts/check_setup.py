#!/usr/bin/env python3
"""
/status — verify setup (multi-project).

Required: Cloudflare credentials (global).
Optional: Namecheap credentials (only for /domain command).
Shows: list of projects under projects/.
"""
import json
import os
import subprocess
import sys
from pathlib import Path


def ensure_deps():
    try:
        from dotenv import load_dotenv  # noqa
    except ImportError:
        subprocess.check_call(
            [sys.executable, "-m", "pip", "install", "-q", "--user",
             "python-dotenv", "requests"]
        )


ensure_deps()
from dotenv import load_dotenv  # noqa: E402
import requests  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
load_dotenv(ROOT / ".env")

OK = "✅"
FAIL = "❌"
SKIP = "○ "


def header(msg):
    print(f"\n{msg}")
    print("─" * 50)


def main():
    print("🔍 AI Site Builder — status check (multi-project)")

    # ── REQUIRED — Cloudflare ──
    header("Required: Cloudflare credentials")
    cf_token = os.getenv("CLOUDFLARE_API_TOKEN", "").strip()
    cf_account = os.getenv("CLOUDFLARE_ACCOUNT_ID", "").strip()

    print(f"{OK if cf_token else FAIL} CLOUDFLARE_API_TOKEN — {'set' if cf_token else 'missing in .env'}")
    print(f"{OK if cf_account else FAIL} CLOUDFLARE_ACCOUNT_ID — {'set' if cf_account else 'missing in .env'}")

    if cf_token and cf_account:
        r = requests.get(
            f"https://api.cloudflare.com/client/v4/accounts/{cf_account}",
            headers={"Authorization": f"Bearer {cf_token}"},
            timeout=10,
        )
        if r.status_code == 200:
            print(f"{OK} CF API call — token works, account verified")
        else:
            print(f"{FAIL} CF API call failed — HTTP {r.status_code}")
            print(f"   → check that token has 'Cloudflare Pages — Edit' permission")
            print(f"   → check Account ID is correct")

    # Deprecation hint
    if os.getenv("CF_PAGES_PROJECT_NAME"):
        print(f"\n⚠️  CF_PAGES_PROJECT_NAME found in .env — ignored in v3.")
        print(f"   In v3 each project stores its CF name inside projects/<slug>/.project.json.")
        print(f"   Safe to remove this line from .env.")

    # ── OPTIONAL — Namecheap ──
    header("Optional: Namecheap (for /domain only)")
    nc_key = os.getenv("NAMECHEAP_API_KEY", "").strip()
    nc_user = os.getenv("NAMECHEAP_USERNAME", "").strip()
    nc_ip = os.getenv("NAMECHEAP_IP", "").strip()

    nc_filled = bool(nc_key and nc_user and nc_ip)
    if nc_filled:
        print(f"{OK} NAMECHEAP_API_KEY")
        print(f"{OK} NAMECHEAP_USERNAME")
        print(f"{OK} NAMECHEAP_IP")
        print(f"\n→ /domain available (pass DOMAIN as arg or set in project meta)")
    else:
        print(f"{SKIP} NAMECHEAP_API_KEY — empty")
        print(f"{SKIP} NAMECHEAP_USERNAME — empty")
        print(f"{SKIP} NAMECHEAP_IP — empty")
        print(f"\nℹ /domain disabled (this is fine — basic flow works without it)")

    # ── PROJECTS ──
    header("Projects")
    projects_dir = ROOT / "projects"
    if not projects_dir.exists():
        # Legacy v2 detection
        if (ROOT / "site").exists() or (ROOT / "site-template").exists():
            print(f"⚠️  Legacy v2 layout detected (./site or ./site-template).")
            print(f"   Run the migration: ask Claude to migrate to v3 (see CLAUDE.md → Auto-migration).")
        else:
            print(f"{SKIP} No projects yet — run /new-site <slug> to create your first")
    else:
        active_file = projects_dir / ".active"
        active = active_file.read_text().strip() if active_file.exists() else ""
        slugs = sorted([p.name for p in projects_dir.iterdir()
                        if p.is_dir() and not p.name.startswith('.')])
        if not slugs:
            print(f"{SKIP} projects/ exists but is empty — run /new-site <slug>")
        else:
            for slug in slugs:
                meta_path = projects_dir / slug / ".project.json"
                meta = {}
                if meta_path.exists():
                    try:
                        meta = json.loads(meta_path.read_text())
                    except Exception:
                        pass
                cf_name = meta.get("cf_project_name", slug)
                domain = meta.get("domain")
                target = domain if domain else f"{cf_name}.pages.dev"
                marker = "★" if slug == active else " "
                print(f"  {marker} {slug:<25} → {target}")
            if active:
                print(f"\n  ★ active: {active}")

    # ── Template ──
    template = ROOT / "templates" / "site" / "index.html"
    legacy_template = ROOT / "site-template" / "index.html"
    if template.exists():
        print(f"\n{OK} templates/site/index.html — reference for /new-site")
    elif legacy_template.exists():
        print(f"\n⚠️  legacy site-template/ still exists — migration will move it to templates/site/")
    else:
        print(f"\n{FAIL} templates/site/index.html missing")

    # ── Summary ──
    header("Summary")
    cf_ready = cf_token and cf_account
    if cf_ready:
        print(f"{OK} Ready for /new-site and /deploy")
    else:
        print(f"{FAIL} Fill required Cloudflare creds in .env first")
    if nc_filled:
        print(f"{OK} /domain command available")


if __name__ == "__main__":
    main()
