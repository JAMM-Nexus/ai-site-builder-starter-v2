#!/usr/bin/env python3
"""
Deploy a project to Cloudflare Pages.

Usage:
    python3 scripts/deploy.py [slug]

If slug omitted — uses projects/.active. If .active missing and only one
project exists — uses it. Otherwise asks.

Reads:
    .env                       → CLOUDFLARE_API_TOKEN, CLOUDFLARE_ACCOUNT_ID
    projects/<slug>/.project.json → cf_project_name

Uses wrangler via npx (preferred) or CF Pages REST API (fallback).
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
from dotenv import load_dotenv  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
load_dotenv(ROOT / '.env')


def resolve_slug(argv_slug: str | None) -> str:
    projects_dir = ROOT / 'projects'
    if not projects_dir.exists():
        print("❌ projects/ folder not found. Run /new-site <slug> first.")
        sys.exit(1)

    if argv_slug:
        return argv_slug

    active_file = projects_dir / '.active'
    if active_file.exists():
        slug = active_file.read_text().strip()
        if slug and (projects_dir / slug).is_dir():
            return slug

    candidates = [p.name for p in projects_dir.iterdir()
                  if p.is_dir() and not p.name.startswith('.')]
    if len(candidates) == 1:
        return candidates[0]
    if len(candidates) == 0:
        print("❌ No projects yet. Run /new-site <slug> first.")
        sys.exit(1)

    print(f"❌ Multiple projects exist: {', '.join(candidates)}")
    print("   → Pass slug explicitly: python3 scripts/deploy.py <slug>")
    print("   → Or set active: write slug to projects/.active")
    sys.exit(1)


def load_project_meta(slug: str) -> dict:
    meta_path = ROOT / 'projects' / slug / '.project.json'
    if not meta_path.exists():
        print(f"❌ projects/{slug}/.project.json not found.")
        print(f"   → Re-run /new-site {slug} or create the file manually.")
        sys.exit(1)
    return json.loads(meta_path.read_text())


def check_credentials():
    token = os.getenv('CLOUDFLARE_API_TOKEN')
    account_id = os.getenv('CLOUDFLARE_ACCOUNT_ID')
    missing = [k for k, v in {
        'CLOUDFLARE_API_TOKEN': token,
        'CLOUDFLARE_ACCOUNT_ID': account_id,
    }.items() if not v]
    if missing:
        print(f"❌ Missing env vars: {', '.join(missing)}")
        print("   → Fill them in .env")
        sys.exit(1)
    return token, account_id


def deploy_via_wrangler(slug: str, cf_project_name: str) -> bool:
    if not shutil.which('npx') and not shutil.which('node'):
        return False

    print("🔧 Deploying via wrangler...")
    env = {**os.environ, 'CLOUDFLARE_API_TOKEN': os.getenv('CLOUDFLARE_API_TOKEN')}
    result = subprocess.run(
        ['npx', '--yes', 'wrangler@3', 'pages', 'deploy', f'./projects/{slug}',
         '--project-name', cf_project_name, '--commit-dirty=true'],
        env=env,
        capture_output=True,
        text=True,
        cwd=ROOT,
    )

    if result.returncode == 0:
        for line in (result.stdout + result.stderr).split('\n'):
            if 'pages.dev' in line or line.strip().startswith('http'):
                print(f"✅ Deployed! URL: {line.strip()}")
                return True
        print(f"✅ Deployed! Check: https://{cf_project_name}.pages.dev")
        return True

    print(f"⚠️  wrangler failed (code {result.returncode}), trying API fallback...")
    if result.stderr:
        print(f"   {result.stderr[:300]}")
    return False


def deploy_via_api(token: str, account_id: str, slug: str, cf_project_name: str):
    try:
        import requests
    except ImportError:
        print("Installing requests...")
        subprocess.run([sys.executable, '-m', 'pip', 'install', 'requests', '-q'], check=True)
        import requests

    site_dir = ROOT / 'projects' / slug
    headers = {'Authorization': f'Bearer {token}'}
    base = f'https://api.cloudflare.com/client/v4/accounts/{account_id}/pages/projects/{cf_project_name}'

    print("📦 Preparing files...")
    manifest = {}
    file_map = {}

    for fp in sorted(site_dir.rglob('*')):
        if not fp.is_file():
            continue
        rel_posix = fp.relative_to(site_dir).as_posix()
        # Skip per-project metadata (not part of the deployable site)
        if rel_posix.startswith('.project.json') or rel_posix.startswith('.project'):
            continue
        rel = '/' + rel_posix
        content = fp.read_bytes()
        file_hash = hashlib.sha256(content).hexdigest()[:32]
        manifest[rel] = file_hash
        mime = mimetypes.guess_type(fp.name)[0] or 'application/octet-stream'
        file_map[file_hash] = (rel, content, mime)

    print(f"   Found {len(manifest)} files")

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

    done = requests.post(f'{base}/deployments/{deployment_id}/complete', headers=headers)
    if done.ok:
        result = done.json().get('result', {})
        url = result.get('url', f'https://{cf_project_name}.pages.dev')
        print(f"✅ Deployed successfully!")
        print(f"🌐 URL: {url}")
    else:
        print(f"⚠️  Completion signal failed: {done.text[:200]}")
        print(f"🌐 Check manually: https://{cf_project_name}.pages.dev")


def main():
    print("🚀 AI Site Builder — Deploy to Cloudflare Pages")
    print("─" * 50)

    argv_slug = sys.argv[1] if len(sys.argv) > 1 else None
    slug = resolve_slug(argv_slug)
    meta = load_project_meta(slug)
    cf_project_name = meta.get('cf_project_name') or slug

    token, account_id = check_credentials()

    site_dir = ROOT / 'projects' / slug
    if not site_dir.exists() or not (site_dir / 'index.html').exists():
        print(f"❌ projects/{slug}/index.html not found.")
        print(f"   → Run /new-site {slug} first to build this project")
        sys.exit(1)

    files_count = sum(1 for f in site_dir.rglob('*')
                      if f.is_file() and not f.name.startswith('.project'))
    print(f"📁 Project:    {slug}")
    print(f"📁 CF target:  {cf_project_name}")
    print(f"📁 Files:      {files_count} → projects/{slug}/")
    print()

    if not deploy_via_wrangler(slug, cf_project_name):
        deploy_via_api(token, account_id, slug, cf_project_name)


if __name__ == '__main__':
    main()
