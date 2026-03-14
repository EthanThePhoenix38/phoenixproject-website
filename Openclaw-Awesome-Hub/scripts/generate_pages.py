#!/usr/bin/env python3
"""
Generate individual Markdown pages for each repo in pages/ directory.
No external dependencies.
"""

import json
import urllib.request
import urllib.parse
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).parent.parent
DATA_DIR = ROOT / "data"
PAGES_DIR = ROOT / "pages"
PAGES_DIR.mkdir(exist_ok=True)

GITHUB_TOKEN = __import__("os").environ.get("GITHUB_TOKEN", "")


def fetch_readme(full_name: str) -> str:
    """Fetch the raw README of a repo. Returns empty string on failure."""
    headers = {
        "Accept": "application/vnd.github.raw+json",
        "X-GitHub-Api-Version": "2022-11-28",
        "User-Agent": "Openclaw-Awesome-Hub/1.0",
    }
    if GITHUB_TOKEN:
        headers["Authorization"] = f"Bearer {GITHUB_TOKEN}"
    url = f"https://api.github.com/repos/{full_name}/readme"
    try:
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=15) as resp:
            return resp.read().decode("utf-8")
    except Exception:
        return ""


def load_repos() -> list:
    f = DATA_DIR / "repos.json"
    if not f.exists():
        return []
    with open(f, encoding="utf-8") as fh:
        return json.load(fh).get("repos", [])


def page_filename(full_name: str) -> str:
    return full_name.replace("/", "-") + ".md"


def build_page(repo: dict, readme_content: str) -> str:
    name = repo["name"]
    full_name = repo["full_name"]
    url = repo["url"]
    desc_en = repo.get("description") or ""
    desc_fr = repo.get("description_fr") or desc_en
    stars = repo.get("stars", 0)
    lang = repo.get("language") or "Unknown"
    topics = repo.get("topics", [])
    license_ = repo.get("license", "Unknown")
    cat = repo.get("category", "tools")
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d")

    topics_badges = " ".join(
        f"![{t}](https://img.shields.io/badge/{urllib.parse.quote(t, safe='')}-333?style=flat-square)"
        for t in topics[:8]
    )

    readme_section = ""
    if readme_content.strip():
        readme_section = f"""
---

## README du Projet / Project README

> Contenu original traduit depuis le dépôt source.

{readme_content[:8000]}
{"...\n\n*[README tronqué — voir le repo original pour la version complète](" + url + ")*" if len(readme_content) > 8000 else ""}
"""

    return f"""<div align="center">

[![Back to Home](https://img.shields.io/badge/←_Retour_/_Back-Awesome_OpenClaw-ff6b35?style=for-the-badge&labelColor=0d1117)](../README.md)

# {name}

[![Stars](https://img.shields.io/github/stars/{full_name}?style=flat-square&color=ff6b35)](https://github.com/{full_name})
[![Forks](https://img.shields.io/github/forks/{full_name}?style=flat-square&color=f7931e)](https://github.com/{full_name}/network)
[![Language](https://img.shields.io/badge/lang-{urllib.parse.quote(lang, safe='')}-7c3aed?style=flat-square)](#)
[![License](https://img.shields.io/badge/license-{urllib.parse.quote(license_, safe='')}-2563eb?style=flat-square)](#)
[![Category](https://img.shields.io/badge/catégorie-{cat}-10b981?style=flat-square)](#)

{topics_badges}

</div>

---

## Description

**[Voir le dépôt original / View original repo]({url})**

| | |
|---|---|
| **Description (FR)** | {desc_fr} |
| **Description (EN)** | {desc_en} |
| **Langage principal** | {lang} |
| **Étoiles** | {stars:,} |
| **Licence** | {license_} |
| **Catégorie** | {cat} |

{readme_section}

---

<div align="center">

[![Back to Home](https://img.shields.io/badge/←_Retour_à_l'accueil-ff6b35?style=for-the-badge&labelColor=0d1117)](../README.md)
[![Back to Category](https://img.shields.io/badge/←_Retour_catégorie-7c3aed?style=for-the-badge&labelColor=0d1117)](../README.md#{cat.replace("_", "-")})

**[ThePhoenixAgency.github.io](http://ThePhoenixAgency.github.io)**

<img src="../assets/phoenix-logo-small.svg" width="32" alt="Phoenix"/>

*Page mise à jour le {now}*

</div>
"""


def main():
    print(f"[{datetime.now().strftime('%H:%M:%S')}] Generating repo pages...")
    repos = load_repos()
    if not repos:
        print("  No repos to process.")
        return

    generated = 0
    for repo in repos:
        full_name = repo["full_name"]
        out_file = PAGES_DIR / page_filename(full_name)

        # Only re-generate if outdated or missing
        if out_file.exists():
            continue

        print(f"  Generating page for {full_name}...")
        readme = fetch_readme(full_name)
        content = build_page(repo, readme)
        out_file.write_text(content, encoding="utf-8")
        generated += 1

    print(f"  Generated {generated} new pages. Total in pages/: {len(list(PAGES_DIR.glob('*.md')))}")


if __name__ == "__main__":
    main()
