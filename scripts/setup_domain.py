#!/usr/bin/env python3
"""
Configure custom domain for your site.

Actions:
  1. Namecheap: set CNAME records pointing to CF Pages
  2. Cloudflare Pages: add custom domain to the project
  3. Verify: check DNS propagation status

Reads credentials from .env file.
"""
import os
import sys
import json
import time
import urllib.parse
import xml.etree.ElementTree as ET
from pathlib import Path
from dotenv import load_dotenv

load_dotenv(Path(__file__).parent.parent / '.env')


def get_env_or_exit(key: str) -> str:
    val = os.getenv(key)
    if not val:
        print(f"❌ Missing: {key}")
        print(f"   → Add it to .env file")
        sys.exit(1)
    return val


def namecheap_api(params: dict) -> ET.Element:
    """Call Namecheap XML API and return result element."""
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


def get_existing_hosts(sld: str, tld: str) -> list[dict]:
    """Get existing DNS hosts for domain."""
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
    """Set CNAME records on Namecheap for CF Pages."""
    print(f"🔧 Configuring Namecheap DNS for {domain}...")

    parts = domain.rsplit('.', 1)
    if len(parts) != 2:
        print(f"❌ Invalid domain format: {domain}")
        sys.exit(1)
    sld, tld = parts[0], parts[1]

    # Get existing hosts to preserve them
    existing = get_existing_hosts(sld, tld)
    print(f"   Found {len(existing)} existing DNS records")

    # Remove old CNAME for www and @ if present
    filtered = [h for h in existing
                if not (h['HostName'] in ('www', '@') and h['RecordType'] == 'CNAME')]

    # Add new CNAME records pointing to CF Pages
    new_hosts = filtered + [
        {'HostName': 'www', 'RecordType': 'CNAME', 'Address': pages_domain, 'TTL': '1800'},
    ]

    # Build params for setHosts
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


def add_cf_pages_domain(token: str, account_id: str, project_name: str, domain: str):
    """Add custom domain to CF Pages project."""
    try:
        import requests
    except ImportError:
        import subprocess
        subprocess.run([sys.executable, '-m', 'pip', 'install', 'requests', '-q'], check=True)
        import requests

    print(f"\n🔧 Adding custom domain to CF Pages...")
    headers = {'Authorization': f'Bearer {token}', 'Content-Type': 'application/json'}
    url = (f'https://api.cloudflare.com/client/v4/accounts/{account_id}'
           f'/pages/projects/{project_name}/domains')

    # Add www. version
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
    """Basic DNS check via socket."""
    import socket
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

    token = get_env_or_exit('CLOUDFLARE_API_TOKEN')
    account_id = get_env_or_exit('CLOUDFLARE_ACCOUNT_ID')
    project_name = get_env_or_exit('CF_PAGES_PROJECT_NAME')
    domain = get_env_or_exit('DOMAIN')

    pages_domain = f'{project_name}.pages.dev'
    print(f"   Domain:       {domain}")
    print(f"   CF Pages:     {pages_domain}")
    print()

    # Step 1: Namecheap DNS
    set_namecheap_dns(domain, pages_domain)

    # Step 2: CF Pages custom domain
    add_cf_pages_domain(token, account_id, project_name, domain)

    # Step 3: DNS check
    check_dns_propagation(domain)

    print()
    print("✅ Domain setup complete!")
    print(f"🌐 Your site will be available at: https://www.{domain}")
    print("   (DNS propagation: 5-30 minutes)")


if __name__ == '__main__':
    main()
