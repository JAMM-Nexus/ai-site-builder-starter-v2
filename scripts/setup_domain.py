#!/usr/bin/env python3
"""
Configure custom domain for a project (multi-project).

Usage:
    python3 scripts/setup_domain.py <slug> [domain]

If <slug> omitted — uses projects/.active.
If [domain] omitted — reads from projects/<slug>/.project.json (if present).

Actions:
  1. Namecheap: set CNAME records pointing to CF Pages
  2. Cloudflare Pages: add custom domain to the project
  3. Verify: check DNS propagation status
  4. Save: write domain into projects/<slug>/.project.json
"""
import json
import os
import socket
import sys
import time
import urllib.parse
import xml.etree.ElementTree as ET
from pathlib import Path
from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parent.parent
PROJECTS = ROOT / 'projects'
load_dotenv(ROOT / '.env')


def get_env_or_exit(key: str) -> str:
    val = os.getenv(key)
    if not val:
        print(f"❌ Missing: {key}")
        print(f"   → Add it to .env file")
        sys.exit(1)
    return val


def resolve_slug(argv_slug: str | None) -> str:
    if argv_slug:
        return argv_slug
    active_file = PROJECTS / '.active'
    if active_file.exists():
        slug = active_file.read_text().strip()
        if slug and (PROJECTS / slug).is_dir():
            return slug
    candidates = [p.name for p in PROJECTS.iterdir()
                  if p.is_dir() and not p.name.startswith('.')] if PROJECTS.exists() else []
    if len(candidates) == 1:
        return candidates[0]
    print(f"❌ Provide slug as first arg. Available: {', '.join(candidates) or '(none)'}")
    sys.exit(1)


def load_meta(slug: str) -> dict:
    p = PROJECTS / slug / '.project.json'
    if not p.exists():
        print(f"❌ projects/{slug}/.project.json not found")
        sys.exit(1)
    return json.loads(p.read_text())


def save_meta(slug: str, meta: dict):
    (PROJECTS / slug / '.project.json').write_text(json.dumps(meta, indent=2) + '\n')


def namecheap_api(params: dict) -> ET.Element:
    try:
        import requests
    except ImportError:
        import subprocess
        subprocess.run([sys.executable, '-m', 'pip', 'install', 'requests', '-q'], check=True)
        import requests

    base = {
        'ApiUser': get_env_or_exit('NAMECHEAP_USERNAME'),
        'ApiKey': get_env_or_exit('NAMECHEAP_API_KEY'),
        'UserName': get_env_or_exit('NAMECHEAP_USERNAME'),
        'ClientIp': get_env_or_exit('NAMECHEAP_IP'),
    }
    all_params = {**base, **params}
    url = 'https://api.namecheap.com/xml.response?' + urllib.parse.urlencode(all_params)
    resp = requests.get(url, timeout=30)
    resp.raise_for_status()
    root = ET.fromstring(resp.text)
    ns = {'nc': 'http://api.namecheap.com/xml.response'}
    errors = root.findall('.//nc:Error', ns)
    if errors:
        for e in errors:
            print(f"❌ Namecheap API error: {e.text}")
        sys.exit(1)
    return root


def get_existing_hosts(sld: str, tld: str) -> list:
    root = namecheap_api({
        'Command': 'namecheap.domains.dns.getHosts',
        'SLD': sld,
        'TLD': tld,
    })
    ns = {'nc': 'http://api.namecheap.com/xml.response'}
    hosts = []
    for host in root.findall('.//nc:host', ns):
        hosts.append({
            'HostName': host.get('Name'),
            'RecordType': host.get('Type'),
            'Address': host.get('Address'),
            'TTL': host.get('TTL', '1800'),
        })
    return hosts


def set_namecheap_dns(domain: str, pages_domain: str):
    print(f"🔧 Configuring Namecheap DNS for {domain}...")
    parts = domain.rsplit('.', 1)
    if len(parts) != 2:
        print(f"❌ Invalid domain format: {domain}")
        sys.exit(1)
    sld, tld = parts[0], parts[1]

    existing = get_existing_hosts(sld, tld)
    print(f"   Found {len(existing)} existing DNS records")

    filtered = [h for h in existing
                if not (h['HostName'] in ('www', '@') and h['RecordType'] == 'CNAME')]

    new_hosts = filtered + [
        {'HostName': 'www', 'RecordType': 'CNAME', 'Address': pages_domain, 'TTL': '1800'},
    ]

    params = {
        'Command': 'namecheap.domains.dns.setHosts',
        'SLD': sld,
        'TLD': tld,
    }
    for i, host in enumerate(new_hosts, start=1):
        params[f'HostName{i}'] = host['HostName']
        params[f'RecordType{i}'] = host['RecordType']
        params[f'Address{i}'] = host['Address']
        params[f'TTL{i}'] = host.get('TTL', '1800')

    namecheap_api(params)
    print(f"   ✅ www.{domain} → {pages_domain} (CNAME)")
    print(f"   ✅ DNS updated on Namecheap")


def add_cf_pages_domain(token: str, account_id: str, cf_project_name: str, domain: str):
    try:
        import requests
    except ImportError:
        import subprocess
        subprocess.run([sys.executable, '-m', 'pip', 'install', 'requests', '-q'], check=True)
        import requests

    print(f"\n🔧 Adding custom domain to CF Pages...")
    headers = {'Authorization': f'Bearer {token}', 'Content-Type': 'application/json'}
    url = (f'https://api.cloudflare.com/client/v4/accounts/{account_id}'
           f'/pages/projects/{cf_project_name}/domains')

    for subdomain in [f'www.{domain}']:
        resp = requests.post(url, headers=headers, json={'name': subdomain})
        data = resp.json()
        if data.get('success'):
            print(f"   ✅ {subdomain} added to CF Pages")
        elif 'already exists' in str(data.get('errors', '')).lower():
            print(f"   ℹ️  {subdomain} already configured")
        else:
            print(f"   ⚠️  {subdomain}: {json.dumps(data.get('errors', []))}")


def check_dns_propagation(domain: str):
    fqdn = f'www.{domain}'
    print(f"\n⏳ Checking DNS propagation for {fqdn}...")
    for attempt in range(3):
        try:
            ip = socket.gethostbyname(fqdn)
            print(f"   ✅ {fqdn} resolves to {ip}")
            return True
        except socket.gaierror:
            if attempt < 2:
                print(f"   ⏳ Not propagated yet, waiting 10s...")
                time.sleep(10)
    print(f"   ⚠️  DNS not propagated yet — this is normal (takes 5-30 min)")
    print(f"   → Check back in 15 minutes: https://www.{domain}")
    return False


def main():
    print("🌐 AI Site Builder — Custom Domain Setup")
    print("─" * 50)

    argv_slug = sys.argv[1] if len(sys.argv) > 1 else None
    argv_domain = sys.argv[2] if len(sys.argv) > 2 else None

    slug = resolve_slug(argv_slug)
    meta = load_meta(slug)
    cf_project_name = meta.get('cf_project_name') or slug

    domain = argv_domain or meta.get('domain') or os.getenv('DOMAIN', '').strip()
    if not domain:
        print(f"❌ No domain provided. Usage: python3 scripts/setup_domain.py {slug} example.com")
        sys.exit(1)

    token = get_env_or_exit('CLOUDFLARE_API_TOKEN')
    account_id = get_env_or_exit('CLOUDFLARE_ACCOUNT_ID')

    pages_domain = f'{cf_project_name}.pages.dev'
    print(f"   Project:      {slug}")
    print(f"   Domain:       {domain}")
    print(f"   CF Pages:     {pages_domain}")
    print()

    set_namecheap_dns(domain, pages_domain)
    add_cf_pages_domain(token, account_id, cf_project_name, domain)
    check_dns_propagation(domain)

    meta['domain'] = domain
    save_meta(slug, meta)

    print()
    print("✅ Domain setup complete!")
    print(f"🌐 Your site will be available at: https://www.{domain}")
    print("   (DNS propagation: 5-30 minutes)")


if __name__ == '__main__':
    main()
