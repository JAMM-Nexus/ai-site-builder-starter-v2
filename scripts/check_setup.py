#!/usr/bin/env python3
"""
/status — check connections.
CF API token is OPTIONAL (only for /domain). Basic flow needs nothing.
"""
import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def have_dotenv():
    """Auto-install python-dotenv if missing."""
    try:
        from dotenv import load_dotenv
        load_dotenv(ROOT / ".env")
        return True
    except ImportError:
        try:
            subprocess.check_call(
                [sys.executable, "-m", "pip", "install", "-q", "python-dotenv"]
            )
            from dotenv import load_dotenv
            load_dotenv(ROOT / ".env")
            return True
        except Exception:
            return False


def main():
    print("🔍 AI Site Builder v2 — status check\n")

    # 1. Required: site/ exists
    if (ROOT / "site" / "index.html").exists():
        print("✓ site/index.html  — found")
    else:
        print("✗ site/index.html  — missing (run /new-site first)")

    # 2. Required: git initialized
    if (ROOT / ".git").exists():
        print("✓ git              — initialized")
        # remote check
        r = subprocess.run(
            ["git", "remote", "get-url", "origin"],
            cwd=ROOT, capture_output=True, text=True
        )
        if r.returncode == 0:
            print(f"✓ remote origin    — {r.stdout.strip()}")
        else:
            print("✗ remote origin    — not set")
    else:
        print("✗ git              — not initialized")

    # 3. Optional: .env for /domain
    env_path = ROOT / ".env"
    if env_path.exists():
        have_dotenv()
        cf_token = bool(os.getenv("CLOUDFLARE_API_TOKEN", "").strip())
        nc_key = bool(os.getenv("NAMECHEAP_API_KEY", "").strip())
        domain = os.getenv("DOMAIN", "").strip()
        print(f"\n.env (optional, for /domain only):")
        print(f"  {'✓' if cf_token else '○'} CLOUDFLARE_API_TOKEN")
        print(f"  {'✓' if nc_key else '○'} NAMECHEAP_API_KEY")
        print(f"  {'✓' if domain else '○'} DOMAIN")
        if cf_token and nc_key and domain:
            print("  → /domain available")
        else:
            print("  → /domain not configured (fine — basic flow works without it)")
    else:
        print("\n.env: not present — /domain disabled (OK for basic flow)")

    # 4. Reminder
    print("\n💡 Cloudflare GitHub App must be installed via dashboard:")
    print("   dash.cloudflare.com → Workers & Pages → Create → Pages → Connect to Git")
    print("   This is a manual one-time step that this script cannot verify.")


if __name__ == "__main__":
    main()
