#!/usr/bin/env python3
"""
Deploy site/ directory to Cloudflare Pages.

Uses wrangler via npx (preferred) or CF Pages REST API (fallback).
Reads credentials from .env file.
"""
import os
import sys
import json
import shutil
import hashlib
import mimetypes
import subprocess
from pathlib import Path
import subprocess as _sub

def _ensure_deps():
    try:
        from dotenv import load_dotenv  # noqa
    except ImportError:
        _sub.check_call(
            [sys.executable, "-m", "pip", "install", "-q", "--user", "python-dotenv"]
        )

_ensure_deps()
from dotenv import load_dotenv

# Load .env from project root
load_dotenv(Path(__file__).parent.parent / '.env')


def check_credentials():
    token = os.getenv('CLOUDFLARE_API_TOKEN')
    account_id = os.getenv('CLOUDFLARE_ACCOUNT_ID')
    project_name = os.getenv('CF_PAGES_PROJECT_NAME')
    missing = [k for k, v in {
        'CLOUDFLARE_API_TOKEN': token,
        'CLOUDFLARE_ACCOUNT_ID': account_id,
        'CF_PAGES_PROJECT_NAME': project_name,
    }.items() if not v]
    if missing:
        print(f"❌ Missing env vars: {', '.join(missing)}")
        print("   → Copy .env.example to .env and fill in your Cloudflare credentials")
        sys.exit(1)
    return token, account_id, project_name


def deploy_via_wrangler(project_name: str) -> bool:
    """Try deploying via npx wrangler. Returns True on success."""
    if not shutil.which('npx') and not shutil.which('node'):
        return False

    print("🔧 Deploying via wrangler...")
    env = {**os.environ, 'CLOUDFLARE_API_TOKEN': os.getenv('CLOUDFLARE_API_TOKEN')}
    result = subprocess.run(
        ['npx', '--yes', 'wrangler@3', 'pages', 'deploy', './site',
         '--project-name', project_name, '--commit-dirty=true'],
        env=env,
        capture_output=True,
        text=True,
        cwd=Path(__file__).parent.parent
    )

    if result.returncode == 0:
        for line in (result.stdout + result.stderr).split('\n'):
            if 'pages.dev' in line or line.strip().startswith('http'):
                print(f"✅ Deployed! URL: {line.strip()}")
                return True
        print(f"✅ Deployed! Check: https://{project_name}.pages.dev")
        return True

    print(f"⚠️  wrangler failed (code {result.returncode}), trying API fallback...")
    if result.stderr:
        print(f"   {result.stderr[:300]}")
    return False


def deploy_via_api(token: str, account_id: str, project_name: str):
    """Deploy via Cloudflare Pages Direct Upload API."""
    try:
        import requests
    except ImportError:
        print("Installing requests...")
        subprocess.run([sys.executable, '-m', 'pip', 'install', 'requests', '-q'], check=True)
        import requests

    site_dir = Path(__file__).parent.parent / 'site'
    headers = {'Authorization': f'Bearer {token}'}
    base = f'https://api.cloudflare.com/client/v4/accounts/{account_id}/pages/projects/{project_name}'

    # Collect all files with hashes
    print("📦 Preparing files...")
    manifest = {}
    file_map = {}  # hash → (rel_path, bytes, mime)

    for fp in sorted(site_dir.rglob('*')):
        if not fp.is_file():
            continue
        rel = '/' + fp.relative_to(site_dir).as_posix()
        content = fp.read_bytes()
        file_hash = hashlib.sha256(content).hexdigest()[:32]
        manifest[rel] = file_hash
        mime = mimetypes.guess_type(fp.name)[0] or 'application/octet-stream'
        file_map[file_hash] = (rel, content, mime)

    print(f"   Found {len(manifest)} files")

    # Step 1: Create deployment
    resp = requests.post(
        f'{base}/deployments',
        headers={**headers, 'Content-Type': 'application/json'},
        json={'manifest': manifest}
    )
    if not resp.ok:
        print(f"❌ Failed to create deployment: {resp.status_code} {resp.text[:300]}")
        sys.exit(1)

    data = resp.json()
    if not data.get('success'):
        print(f"❌ API error: {json.dumps(data.get('errors', []))}")
        sys.exit(1)

    deployment_id = data['result']['id']
    missing = data['result'].get('missing_hashes', list(manifest.values()))
    print(f"📤 Uploading {len(missing)} files (deployment {deployment_id[:8]}...)...")

    # Step 2: Upload missing files
    for file_hash in missing:
        if file_hash not in file_map:
            continue
        rel_path, content, mime = file_map[file_hash]
        up = requests.put(
            f'{base}/deployments/{deployment_id}/files{rel_path}',
            headers={**headers, 'Content-Type': mime},
            data=content
        )
        if not up.ok:
            print(f"   ⚠️  {rel_path}: {up.status_code}")

    # Step 3: Mark complete
    done = requests.post(f'{base}/deployments/{deployment_id}/complete', headers=headers)
    if done.ok:
        result = done.json().get('result', {})
        url = result.get('url', f'https://{project_name}.pages.dev')
        print(f"✅ Deployed successfully!")
        print(f"🌐 URL: {url}")
    else:
        print(f"⚠️  Completion signal failed: {done.text[:200]}")
        print(f"🌐 Check manually: https://{project_name}.pages.dev")


def main():
    print("🚀 AI Site Builder — Deploy to Cloudflare Pages")
    print("─" * 50)

    token, account_id, project_name = check_credentials()

    site_dir = Path(__file__).parent.parent / 'site'
    if not site_dir.exists() or not (site_dir / 'index.html').exists():
        print("❌ site/index.html not found.")
        print("   → Run /new-site first to build your website")
        sys.exit(1)

    files_count = sum(1 for _ in site_dir.rglob('*') if _.is_file())
    print(f"📁 Deploying {files_count} files from site/ → {project_name}")
    print()

    # Try wrangler first, fall back to API
    if not deploy_via_wrangler(project_name):
        deploy_via_api(token, account_id, project_name)


if __name__ == '__main__':
    main()
