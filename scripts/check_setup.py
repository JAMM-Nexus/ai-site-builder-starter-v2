#!/usr/bin/env python3
"""
/status — verify setup.
Required: Cloudflare credentials.
Optional: Namecheap credentials (only for /domain command).
"""
import os
import subprocess
import sys
from pathlib import Path


def ensure_deps():
    try:
        from dotenv import load_dotenv  # noqa
    except ImportError:
        subprocess.check_call(
            [sys.executable, "-m", "pip", "install", "-q", "--user", "python-dotenv", "requests"]
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
    print("🔍 AI Site Builder — status check")

    # ── REQUIRED — Cloudflare ──
    header("Required: Cloudflare credentials")
    cf_token = os.getenv("CLOUDFLARE_API_TOKEN", "").strip()
    cf_account = os.getenv("CLOUDFLARE_ACCOUNT_ID", "").strip()
    cf_project = os.getenv("CF_PAGES_PROJECT_NAME", "").strip()

    print(f"{OK if cf_token else FAIL} CLOUDFLARE_API_TOKEN — {'set' if cf_token else 'missing in .env'}")
    print(f"{OK if cf_account else FAIL} CLOUDFLARE_ACCOUNT_ID — {'set' if cf_account else 'missing in .env'}")
    print(f"{OK if cf_project else FAIL} CF_PAGES_PROJECT_NAME — {'set: ' + cf_project if cf_project else 'missing in .env'}")

    if cf_token and cf_account:
        # Live API check
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

    # ── OPTIONAL — Namecheap ──
    header("Optional: Namecheap (for /domain only)")
    nc_key = os.getenv("NAMECHEAP_API_KEY", "").strip()
    nc_user = os.getenv("NAMECHEAP_USERNAME", "").strip()
    nc_ip = os.getenv("NAMECHEAP_IP", "").strip()
    domain = os.getenv("DOMAIN", "").strip()

    nc_filled = bool(nc_key and nc_user and nc_ip and domain)
    if nc_filled:
        print(f"{OK} NAMECHEAP_API_KEY")
        print(f"{OK} NAMECHEAP_USERNAME")
        print(f"{OK} NAMECHEAP_IP")
        print(f"{OK} DOMAIN — {domain}")
        print(f"\n→ /domain available")
    else:
        print(f"{SKIP} NAMECHEAP_API_KEY — empty")
        print(f"{SKIP} NAMECHEAP_USERNAME — empty")
        print(f"{SKIP} NAMECHEAP_IP — empty")
        print(f"{SKIP} DOMAIN — empty")
        print(f"\nℹ /domain disabled (this is fine — basic flow works without it)")

    # ── SITE files ──
    header("Project files")
    site_index = ROOT / "site" / "index.html"
    if site_index.exists():
        print(f"{OK} site/index.html — {site_index.stat().st_size} bytes")
    else:
        print(f"{SKIP} site/index.html — not yet (run /new-site to create)")

    template = ROOT / "site-template" / "index.html"
    print(f"{OK if template.exists() else FAIL} site-template/index.html — reference for /new-site")

    # ── Summary ──
    header("Summary")
    cf_ready = cf_token and cf_account and cf_project
    if cf_ready:
        print(f"{OK} Ready for /new-site and /deploy")
    else:
        print(f"{FAIL} Fill required Cloudflare creds in .env first")

    if nc_filled:
        print(f"{OK} /domain command available")


if __name__ == "__main__":
    main()
