#!/usr/bin/env python3
"""
List all projects under projects/ with their metadata.

Usage:
    python3 scripts/list_projects.py
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PROJECTS = ROOT / 'projects'


def main():
    if not PROJECTS.exists():
        print("ℹ️  No projects/ folder yet.")
        print("   → Run /new-site <slug> to create your first project.")
        return

    active = ''
    active_file = PROJECTS / '.active'
    if active_file.exists():
        active = active_file.read_text().strip()

    projects = sorted([p for p in PROJECTS.iterdir()
                       if p.is_dir() and not p.name.startswith('.')])

    if not projects:
        print("ℹ️  No projects yet.")
        print("   → Run /new-site <slug> to create your first project.")
        return

    print(f"📋 Projects ({len(projects)})")
    print("─" * 70)
    print(f"{'':2} {'SLUG':<25} {'TYPE':<8} {'CF PROJECT / DOMAIN':<30}")
    print("─" * 70)

    for p in projects:
        meta_path = p / '.project.json'
        if meta_path.exists():
            try:
                meta = json.loads(meta_path.read_text())
            except Exception:
                meta = {}
        else:
            meta = {}

        marker = '★' if p.name == active else ' '
        slug = p.name
        ptype = meta.get('type', 'site')
        cf_name = meta.get('cf_project_name') or slug
        domain = meta.get('domain')
        target = domain if domain else f'{cf_name}.pages.dev'
        print(f"{marker:2} {slug:<25} {ptype:<8} {target}")

    print("─" * 70)
    if active:
        print(f"★ active: {active}")
    else:
        print("ℹ no active project set — pass slug explicitly or run /use <slug>")


if __name__ == '__main__':
    main()
