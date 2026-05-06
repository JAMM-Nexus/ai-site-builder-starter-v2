#!/usr/bin/env python3
"""
/domain — connect custom domain via Namecheap API + Cloudflare API.
OPTIONAL — only run if you have a custom domain bought.
"""
import os
import subprocess
import sys
from pathlib import Path


def ensure_deps():
    """Auto-install requests and python-dotenv if missing."""
    for pkg in ["requests", "python-dotenv"]:
        try:
            __import__(pkg.replace("-", "_"))
        except ImportError:
            subprocess.check_call(
                [sys.executable, "-m", "pip", "install", "-q", pkg]
            )


ensure_deps()

import requests  # noqa: E402
from dotenv import load_dotenv  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
load_dotenv(ROOT / ".env")

CF_TOKEN = os.getenv("CLOUDFLARE_API_TOKEN", "").strip()
CF_ACCOUNT = os.getenv("CLOUDFLARE_ACCOUNT_ID", "").strip()
NC_KEY = os.getenv("NAMECHEAP_API_KEY", "").strip()
NC_USER = os.getenv("NAMECHEAP_USERNAME", "").strip()
NC_IP = os.getenv("NAMECHEAP_IP", "").strip()
DOMAIN = os.getenv("DOMAIN", "").strip()
PROJECT = os.getenv("CF_PAGES_PROJECT_NAME", "").strip()

required = {
    "CLOUDFLARE_API_TOKEN": CF_TOKEN,
    "CLOUDFLARE_ACCOUNT_ID": CF_ACCOUNT,
    "NAMECHEAP_API_KEY": NC_KEY,
    "NAMECHEAP_USERNAME": NC_USER,
    "DOMAIN": DOMAIN,
}
missing = [k for k, v in required.items() if not v]
if missing:
    print(f"❌ Missing in .env: {', '.join(missing)}")
    print("   Copy .env.example to .env and fill the values.")
    sys.exit(1)

if not PROJECT:
    PROJECT = DOMAIN.split(".")[0].replace("-", "").lower()

# Namecheap — set CNAME records
sld, tld = DOMAIN.split(".", 1)
nc_url = "https://api.namecheap.com/xml.response"
common = {
    "ApiUser": NC_USER,
    "ApiKey": NC_KEY,
    "UserName": NC_USER,
    "ClientIp": NC_IP,
    "SLD": sld,
    "TLD": tld,
}
target = f"{PROJECT}.pages.dev"

# Get current hosts to preserve non-managed records
get = requests.get(
    nc_url,
    params={**common, "Command": "namecheap.domains.dns.getHosts"},
    timeout=15,
)
print(f"Namecheap getHosts: HTTP {get.status_code}")

# Set new CNAMEs (apex + www)
set_params = {
    **common,
    "Command": "namecheap.domains.dns.setHosts",
    "HostName1": "@",
    "RecordType1": "CNAME",
    "Address1": target,
    "TTL1": "1800",
    "HostName2": "www",
    "RecordType2": "CNAME",
    "Address2": target,
    "TTL2": "1800",
}
r = requests.post(nc_url, data=set_params, timeout=15)
print(f"Namecheap setHosts: HTTP {r.status_code}")

# Cloudflare Pages — add custom hostname
cf_url = f"https://api.cloudflare.com/client/v4/accounts/{CF_ACCOUNT}/pages/projects/{PROJECT}/domains"
for hostname in [DOMAIN, f"www.{DOMAIN}"]:
    cf_resp = requests.post(
        cf_url,
        headers={"Authorization": f"Bearer {CF_TOKEN}"},
        json={"name": hostname},
        timeout=15,
    )
    print(f"CF add {hostname}: HTTP {cf_resp.status_code}")

print(f"\n✅ Domain {DOMAIN} configured.")
print("⏱  DNS propagation: 5 min — 24h. Monitor:")
print(f"   https://dnschecker.org/#CNAME/{DOMAIN}")
