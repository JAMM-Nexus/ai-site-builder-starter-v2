#!/usr/bin/env python3
"""
/deploy — git-driven publish.
Pushes site/ to main; Cloudflare Pages auto-rebuilds via webhook.

No API tokens needed. No wrangler. Works from any environment with git.
"""
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

# Sanity check
if not (ROOT / "site" / "index.html").exists():
    print("❌ site/index.html missing — run /new-site first")
    sys.exit(1)


def run(cmd, check=True):
    return subprocess.run(cmd, cwd=ROOT, check=check)


# Add + commit + push
run(["git", "add", "site/"])

# Allow empty commit if nothing changed (for re-trigger CF webhook)
result = subprocess.run(
    ["git", "commit", "-m", "deploy: site update"],
    cwd=ROOT,
)
if result.returncode != 0:
    print("ℹ Nothing new to commit — pushing anyway in case main is ahead")

run(["git", "push", "origin", "main"])

print("\n✅ Pushed to main.")
print("⏱  Cloudflare Pages will rebuild in ~30 seconds.")
print("🌐 Watch: https://dash.cloudflare.com/?to=/:account/workers-and-pages")
