#!/usr/bin/env python3
"""
Scaffold a new project at projects/<slug>/ from templates/site/.

Usage:
    python3 scripts/new_project.py <slug> [--type site|other] [--no-template]

Creates:
    projects/<slug>/                   (copy of templates/site/ if type=site)
    projects/<slug>/.project.json      (metadata)
    projects/.active                   (slug → active project)
"""
import json
import re
import shutil
import sys
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PROJECTS = ROOT / 'projects'
TEMPLATES_SITE = ROOT / 'templates' / 'site'

SLUG_RE = re.compile(r'^[a-z0-9]+(?:-[a-z0-9]+)*$')


def validate_slug(slug: str) -> bool:
    if not slug:
        return False
    if not (3 <= len(slug) <= 40):
        return False
    return bool(SLUG_RE.match(slug))


def main():
    if len(sys.argv) < 2:
        print("Usage: python3 scripts/new_project.py <slug> [--type site|other] [--no-template]")
        sys.exit(1)

    slug = sys.argv[1]
    args = sys.argv[2:]
    project_type = 'site'
    use_template = True

    if '--type' in args:
        i = args.index('--type')
        if i + 1 < len(args):
            project_type = args[i + 1]
    if '--no-template' in args:
        use_template = False

    if not validate_slug(slug):
        print(f"❌ Invalid slug: '{slug}'")
        print("   → Use kebab-case (lowercase, digits, dashes), 3-40 chars")
        print("   → Examples: coffee-shop, portfolio, my-first-site")
        sys.exit(1)

    PROJECTS.mkdir(exist_ok=True)
    target = PROJECTS / slug

    if target.exists():
        print(f"❌ projects/{slug}/ already exists.")
        print(f"   → Pick a different slug or remove the folder manually.")
        sys.exit(1)

    if project_type == 'site' and use_template and TEMPLATES_SITE.exists():
        shutil.copytree(TEMPLATES_SITE, target)
        print(f"✅ Scaffolded projects/{slug}/ from templates/site/")
    else:
        target.mkdir(parents=True)
        print(f"✅ Created empty projects/{slug}/")

    meta = {
        'slug': slug,
        'type': project_type,
        'cf_project_name': slug,
        'domain': None,
        'created': date.today().isoformat(),
    }
    (target / '.project.json').write_text(json.dumps(meta, indent=2) + '\n')
    print(f"✅ Wrote projects/{slug}/.project.json")

    (PROJECTS / '.active').write_text(slug + '\n')
    print(f"✅ Set active project: {slug}")
    print()
    print("Next: Claude will customize the project for your description.")
    print(f"      Then `/deploy` (or `/deploy {slug}`) to publish.")


if __name__ == '__main__':
    main()
