#!/usr/bin/env python3
"""
Update README files with latest curated repo lists.
Translates EN -> FR using Google Translate public endpoint (no API key needed).
No external dependencies — stdlib only.
"""

import json
import re
import time
import urllib.request
import urllib.parse
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).parent.parent
DATA_DIR = ROOT / "data"

CATEGORY_ORDER = [
    "core_robotics",
    "arms_manipulation",
    "motion_control",
    "electronics",
    "ai_ml",
    "computer_vision",
    "simulation",
    "iot",
    "tools",
]

REPOS_PER_PAGE = 50


def translate_en_fr(text: str) -> str:
    """Translate text EN->FR using Google Translate (no API key, public endpoint)."""
    if not text:
        return text
    try:
        params = urllib.parse.urlencode({
            "client": "gtx",
            "sl": "en",
            "tl": "fr",
            "dt": "t",
            "q": text[:500],
        })
        url = f"https://translate.googleapis.com/translate_a/single?{params}"
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            translated = "".join(part[0] for part in data[0] if part[0])
            time.sleep(0.2)
            return translated
    except Exception:
        return text  # Fallback: return original


def load_repos() -> list:
    f = DATA_DIR / "repos.json"
    if not f.exists():
        return []
    with open(f, encoding="utf-8") as fh:
        return json.load(fh).get("repos", [])


def save_repos_with_translations(repos: list) -> None:
    f = DATA_DIR / "repos.json"
    with open(f, encoding="utf-8") as fh:
        data = json.load(fh)
    data["repos"] = repos
    with open(f, "w", encoding="utf-8") as fh:
        json.dump(data, fh, indent=2, ensure_ascii=False)


def fill_translations(repos: list) -> list:
    changed = False
    for repo in repos:
        if repo.get("description") and not repo.get("description_fr"):
            repo["description_fr"] = translate_en_fr(repo["description"])
            changed = True
    if changed:
        save_repos_with_translations(repos)
    return repos


def build_table_rows(repos: list, category: str, page: int) -> str:
    cat_repos = [
        r for r in repos
        if r.get("category") == category and r.get("page", 1) == page
    ]
    cat_repos.sort(key=lambda r: r.get("name", "").lower())

    if not cat_repos:
        return "| — | *Aucun résultat pour l'instant / No results yet* | — | — | — | — |"

    rows = []
    for r in cat_repos:
        full_name = r["full_name"]
        name = r["name"]
        url = r["url"]
        desc_en = (r.get("description") or "")[:80]
        desc_fr = (r.get("description_fr") or desc_en)[:80]
        lang = r.get("language") or "—"
        page_file = f"./pages/{full_name.replace('/', '-')}.md"
        badge = (
            f"[![Stars](https://img.shields.io/github/stars/{full_name}"
            f"?style=flat-square&color=ff6b35)]({url})"
        )
        rows.append(
            f"| {badge} | **[{name}]({url})** | {desc_fr} | {desc_en} | {lang} | [Voir]({page_file}) |"
        )
    return "\n".join(rows)


def replace_block(content: str, start_tag: str, end_tag: str, inner: str) -> str:
    pattern = rf"{re.escape(start_tag)}.*?{re.escape(end_tag)}"
    replacement = f"{start_tag}\n{inner}\n{end_tag}"
    if re.search(pattern, content, re.DOTALL):
        return re.sub(pattern, replacement, content, flags=re.DOTALL)
    return content


def update_readme(path: Path, repos: list, page: int) -> None:
    if not path.exists():
        return
    content = path.read_text(encoding="utf-8")

    # Update each category table
    for cat in CATEGORY_ORDER:
        start = f"<!-- CATEGORY:{cat} START -->"
        end = f"<!-- CATEGORY:{cat} END -->"
        header = (
            "| ⭐ Stars | Projet / Project | Description 🇫🇷 | Description 🇬🇧 | Langue | Page |\n"
            "|---------|-----------------|-----------------|-----------------|--------|------|"
        )
        rows = build_table_rows(repos, cat, page)
        inner = f"{header}\n{rows}"
        content = replace_block(content, start, end, inner)

    # Update page 2 extras
    if page == 2:
        start = "<!-- PAGE2_REPOS START -->"
        end = "<!-- PAGE2_REPOS END -->"
        p2 = [r for r in repos if r.get("page", 1) == 2]
        p2.sort(key=lambda r: r.get("name", "").lower())
        header = (
            "| ⭐ Stars | Projet / Project | Catégorie | Description 🇫🇷 | Description 🇬🇧 | Page |\n"
            "|---------|-----------------|-----------|-----------------|-----------------|------|"
        )
        rows = []
        for r in p2:
            full_name = r["full_name"]
            name = r["name"]
            url = r["url"]
            desc_fr = (r.get("description_fr") or r.get("description") or "")[:80]
            desc_en = (r.get("description") or "")[:80]
            cat = r.get("category", "tools")
            page_file = f"./pages/{full_name.replace('/', '-')}.md"
            badge = f"[![Stars](https://img.shields.io/github/stars/{full_name}?style=flat-square&color=ff6b35)]({url})"
            rows.append(f"| {badge} | **[{name}]({url})** | {cat} | {desc_fr} | {desc_en} | [Voir]({page_file}) |")
        inner = f"{header}\n" + ("\n".join(rows) if rows else "| — | *En attente* | — | — | — | — |")
        content = replace_block(content, start, end, inner)

    # Update last modified date
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    content = re.sub(
        r"<!-- LAST_UPDATE -->.*?<!-- /LAST_UPDATE -->",
        f"<!-- LAST_UPDATE -->{now}<!-- /LAST_UPDATE -->",
        content,
    )

    path.write_text(content, encoding="utf-8")
    print(f"  Updated: {path.name}")


def update_visitors_in_readme(path: Path) -> None:
    visitors_file = DATA_DIR / "visitors.json"
    if not path.exists() or not visitors_file.exists():
        return
    with open(visitors_file, encoding="utf-8") as f:
        data = json.load(f)
    visitors = data.get("recent", [])[-5:]

    content = path.read_text(encoding="utf-8")
    start = "<!-- VISITORS_START -->"
    end = "<!-- VISITORS_END -->"
    header = (
        "| # | 🌍 Pays / Country | 🕐 Heure / Time | 💻 OS | 🔗 Page |\n"
        "|---|------------------|----------------|-------|---------|"
    )
    rows = []
    for i in range(1, 6):
        if i <= len(visitors):
            v = visitors[i - 1]
            rows.append(
                f"| {i} | {v.get('country','🌐 —')} | {v.get('time','—')} | {v.get('os','—')} | {v.get('page','—')} |"
            )
        else:
            rows.append(f"| {i} | 🌐 — | — | — | — |")

    inner = f"{header}\n" + "\n".join(rows)
    content = replace_block(content, start, end, inner)
    path.write_text(content, encoding="utf-8")


def main():
    ts = datetime.now().strftime("%H:%M:%S")
    print(f"[{ts}] Updating README files...")
    repos = load_repos()
    if not repos:
        print("  No repos data. Run scan_trending.py first.")
        return

    print(f"  Translating {sum(1 for r in repos if r.get('description') and not r.get('description_fr'))} descriptions...")
    repos = fill_translations(repos)

    update_readme(ROOT / "README.md", repos, page=1)
    update_readme(ROOT / "README-2.md", repos, page=2)
    update_visitors_in_readme(ROOT / "README.md")

    print("  README update complete.")


if __name__ == "__main__":
    main()
