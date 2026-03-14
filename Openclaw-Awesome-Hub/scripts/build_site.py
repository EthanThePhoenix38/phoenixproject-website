#!/usr/bin/env python3
"""
Build the static GitHub Pages site from templates and data.
Generates docs/index.html, docs/stats.html, docs/repos/*.html
No external dependencies.
"""

import json
import html
import re
import shutil
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).parent.parent
DATA_DIR = ROOT / "data"
TEMPLATES_DIR = ROOT / "docs" / "templates"
DOCS_DIR = ROOT / "docs"
REPOS_HTML_DIR = DOCS_DIR / "repos"
DOCS_DIR.mkdir(exist_ok=True)
REPOS_HTML_DIR.mkdir(exist_ok=True)

BASE_URL = "https://thephoenixagency.github.io/Openclaw-Awesome-Hub"
REPO_URL = "https://github.com/ThePhoenixAgency/Openclaw-Awesome-Hub"

CATEGORIES = {
    "core_robotics": ("Robotique Core", "Core Robotics", "ff6b35"),
    "arms_manipulation": ("Bras & Manipulation", "Arms & Manipulation", "f7931e"),
    "motion_control": ("Contrôle & Motion", "Motion Control", "ffd700"),
    "electronics": ("Électronique & Arduino", "Electronics & Arduino", "10b981"),
    "ai_ml": ("IA & Machine Learning", "AI & Machine Learning", "7c3aed"),
    "computer_vision": ("Vision par Ordinateur", "Computer Vision", "2563eb"),
    "simulation": ("Simulation & Modélisation", "Simulation & Modeling", "06b6d4"),
    "iot": ("IoT & Communication", "IoT & Communication", "ec4899"),
    "tools": ("Outils & Utilitaires", "Tools & Utilities", "64748b"),
}

CATEGORY_ICONS = {
    "core_robotics": "🤖",
    "arms_manipulation": "🦾",
    "motion_control": "🎮",
    "electronics": "🔌",
    "ai_ml": "🧠",
    "computer_vision": "👁️",
    "simulation": "🔧",
    "iot": "📡",
    "tools": "🛠️",
}


def load_repos() -> list:
    f = DATA_DIR / "repos.json"
    if not f.exists():
        return []
    with open(f, encoding="utf-8") as fh:
        return json.load(fh).get("repos", [])


def load_visitors() -> dict:
    f = DATA_DIR / "visitors.json"
    if not f.exists():
        return {"recent": [], "daily": {}, "total": 0}
    with open(f, encoding="utf-8") as fh:
        return json.load(fh)


def load_stats() -> dict:
    f = DATA_DIR / "stats.json"
    if not f.exists():
        return {"categories": {}, "total": 0}
    with open(f, encoding="utf-8") as fh:
        return json.load(fh)


def safe(text: str) -> str:
    return html.escape(str(text or ""))


def read_template(name: str) -> str:
    tmpl = TEMPLATES_DIR / name
    if tmpl.exists():
        return tmpl.read_text(encoding="utf-8")
    return ""


def now_str() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")


def build_repo_card(repo: dict) -> str:
    name = safe(repo["name"])
    full_name = repo["full_name"]
    url = safe(repo["url"])
    desc_fr = safe(repo.get("description_fr") or repo.get("description") or "")
    desc_en = safe(repo.get("description") or "")
    stars = repo.get("stars", 0)
    lang = safe(repo.get("language") or "Unknown")
    cat = repo.get("category", "tools")
    cat_color = CATEGORIES.get(cat, ("", "", "64748b"))[2]
    page_url = f"{BASE_URL}/repos/{full_name.replace('/', '-')}.html"

    return f"""<article class="repo-card" data-category="{cat}">
  <div class="repo-card__header">
    <a href="{url}" target="_blank" rel="noopener noreferrer" class="repo-card__name">{name}</a>
    <span class="repo-card__stars">⭐ {stars:,}</span>
  </div>
  <p class="repo-card__desc-fr">{desc_fr}</p>
  <p class="repo-card__desc-en">{desc_en}</p>
  <div class="repo-card__footer">
    <span class="repo-card__lang">{lang}</span>
    <span class="repo-card__cat" style="color:#{cat_color}">{CATEGORY_ICONS.get(cat,'')} {cat}</span>
    <a href="{page_url}" class="repo-card__detail">Voir la fiche →</a>
  </div>
</article>"""


def build_index(repos: list, stats: dict, visitors: dict) -> str:
    total = stats.get("total", len(repos))
    total_visitors = visitors.get("total", 0)
    recent = visitors.get("recent", [])[-5:]

    # Category nav
    cat_nav = ""
    for cat, (fr, en, color) in CATEGORIES.items():
        count = stats.get("categories", {}).get(cat, 0)
        icon = CATEGORY_ICONS.get(cat, "")
        cat_nav += (
            f'<a href="#{cat}" class="cat-pill" style="--cat-color:#{color}">'
            f'{icon} {fr} <span class="count">{count}</span></a>\n'
        )

    # Category sections
    sections = ""
    for cat, (fr, en, color) in CATEGORIES.items():
        cat_repos = sorted(
            [r for r in repos if r.get("category") == cat],
            key=lambda r: r.get("name", "").lower()
        )
        cards = "\n".join(build_repo_card(r) for r in cat_repos) if cat_repos else (
            '<p class="empty">Aucun dépôt pour l\'instant / No repos yet</p>'
        )
        icon = CATEGORY_ICONS.get(cat, "")
        sections += f"""<section id="{cat}" class="category-section">
  <h2 class="category-title" style="--cat-color:#{color}">{icon} {fr} / {en}
    <span class="category-count">{len(cat_repos)}</span>
  </h2>
  <div class="repo-grid">{cards}</div>
</section>\n"""

    # Visitors table
    visitor_rows = ""
    for i in range(1, 6):
        if i <= len(recent):
            v = recent[i - 1]
            visitor_rows += (
                f"<tr><td>{i}</td><td>{safe(v.get('country','—'))}</td>"
                f"<td>{safe(v.get('time','—'))}</td><td>{safe(v.get('os','—'))}</td>"
                f"<td>{safe(v.get('page','—'))}</td></tr>\n"
            )
        else:
            visitor_rows += f"<tr><td>{i}</td><td>—</td><td>—</td><td>—</td><td>—</td></tr>\n"

    # Daily visitor data for chart
    daily = visitors.get("daily", {})
    chart_labels = json.dumps(list(daily.keys())[-30:])
    chart_data = json.dumps(list(daily.values())[-30:])

    now = now_str()
    return f"""<!DOCTYPE html>
<html lang="fr">
<head>
  <meta charset="UTF-8"/>
  <meta name="viewport" content="width=device-width,initial-scale=1"/>
  <meta http-equiv="Content-Security-Policy" content="
    default-src 'self';
    script-src 'self' 'nonce-__CSP_NONCE__';
    style-src 'self' 'unsafe-inline';
    img-src 'self' data: https://img.shields.io https://raw.githubusercontent.com;
    connect-src 'self' https://api.github.com;
    frame-ancestors 'none';
    base-uri 'self';
    form-action 'self';
  "/>
  <meta name="referrer" content="strict-origin-when-cross-origin"/>
  <meta name="X-Frame-Options" content="DENY"/>
  <title>Openclaw Awesome Hub — ThePhoenixAgency</title>
  <meta name="description" content="Liste curatée des meilleurs projets OpenClaw ecosystem triés par catégories"/>
  <meta property="og:title" content="Openclaw Awesome Hub"/>
  <meta property="og:description" content="Curated list of the best OpenClaw ecosystem repositories"/>
  <meta property="og:image" content="{BASE_URL}/assets/banner.svg"/>
  <meta property="og:url" content="{BASE_URL}"/>
  <meta name="twitter:card" content="summary_large_image"/>
  <link rel="canonical" href="{BASE_URL}/"/>
  <link rel="stylesheet" href="./assets/style.css"/>
</head>
<body>
  <header class="site-header">
    <a href="{REPO_URL}" target="_blank" rel="noopener noreferrer">
      <img src="./assets/banner.svg" alt="Openclaw Awesome Hub" class="banner"/>
    </a>
    <nav class="cat-nav" aria-label="Catégories">
      {cat_nav}
      <a href="#stats" class="cat-pill" style="--cat-color:#22c55e">📊 Stats</a>
    </nav>
  </header>

  <main class="main-content">
    <div class="global-stats">
      <span>📦 {total:,} repos</span>
      <span>👥 {total_visitors:,} visites</span>
      <span>⏱️ Mis à jour toutes les heures</span>
    </div>

    {sections}

    <section id="stats" class="stats-section">
      <h2>Statistiques de visites</h2>
      <canvas id="visitor-chart" width="800" height="280" aria-label="Graphe des visiteurs"></canvas>
      <h3>5 derniers visiteurs</h3>
      <table class="visitor-table">
        <thead>
          <tr><th>#</th><th>Pays</th><th>Heure</th><th>OS</th><th>Page</th></tr>
        </thead>
        <tbody>{visitor_rows}</tbody>
      </table>
      <p><a href="./stats.html">Voir les statistiques complètes →</a></p>
    </section>
  </main>

  <footer class="site-footer">
    <a href="http://ThePhoenixAgency.github.io" target="_blank" rel="noopener noreferrer" class="footer-link">
      ThePhoenixAgency.github.io
    </a>
    <img src="./assets/phoenix-logo-small.svg" width="32" height="32" alt="Phoenix" class="footer-logo"/>
    <p class="footer-meta">Page 1 · Mis à jour le {now}</p>
  </footer>

  <script nonce="__CSP_NONCE__">
  (function() {{
    'use strict';
    // DOM purifier — strip dangerous content from any dynamic text
    function sanitize(str) {{
      return String(str)
        .replace(/&/g, '&amp;')
        .replace(/</g, '&lt;')
        .replace(/>/g, '&gt;')
        .replace(/"/g, '&quot;')
        .replace(/'/g, '&#x27;')
        .replace(/\//g, '&#x2F;')
        .replace(/javascript:/gi, '')
        .replace(/data:/gi, '')
        .replace(/on\w+=/gi, '');
    }}

    // Visitor chart
    const canvas = document.getElementById('visitor-chart');
    if (canvas && canvas.getContext) {{
      const ctx = canvas.getContext('2d');
      const labels = {chart_labels};
      const values = {chart_data};
      const W = canvas.width, H = canvas.height;
      const PL = 50, PR = 20, PT = 30, PB = 45;
      const cW = W - PL - PR, cH = H - PT - PB;
      const maxV = Math.max(...values, 1);

      function px(i) {{ return PL + (i / Math.max(values.length - 1, 1)) * cW; }}
      function py(v) {{ return PT + cH - (v / maxV) * cH; }}

      // Background
      ctx.fillStyle = '#0d1117';
      roundRect(ctx, 0, 0, W, H, 12);
      ctx.fill();

      // Grid
      ctx.strokeStyle = '#ffffff15';
      ctx.lineWidth = 1;
      for (let i = 0; i <= 4; i++) {{
        const yg = PT + (cH * i) / 4;
        ctx.beginPath();
        ctx.moveTo(PL, yg);
        ctx.lineTo(W - PR, yg);
        ctx.stroke();
        ctx.fillStyle = '#94a3b8';
        ctx.font = '10px monospace';
        ctx.textAlign = 'right';
        ctx.fillText(Math.round(maxV * (1 - i / 4)), PL - 5, yg + 4);
      }}

      // Area
      if (values.length > 1) {{
        const grad = ctx.createLinearGradient(0, PT, 0, PT + cH);
        grad.addColorStop(0, 'rgba(255,107,53,0.4)');
        grad.addColorStop(1, 'rgba(255,107,53,0.02)');
        ctx.fillStyle = grad;
        ctx.beginPath();
        ctx.moveTo(px(0), PT + cH);
        values.forEach((v, i) => ctx.lineTo(px(i), py(v)));
        ctx.lineTo(px(values.length - 1), PT + cH);
        ctx.closePath();
        ctx.fill();

        // Line
        const lineGrad = ctx.createLinearGradient(PL, 0, W - PR, 0);
        lineGrad.addColorStop(0, '#ff6b35');
        lineGrad.addColorStop(1, '#f7931e');
        ctx.strokeStyle = lineGrad;
        ctx.lineWidth = 2.5;
        ctx.lineJoin = 'round';
        ctx.lineCap = 'round';
        ctx.beginPath();
        values.forEach((v, i) => i === 0 ? ctx.moveTo(px(i), py(v)) : ctx.lineTo(px(i), py(v)));
        ctx.stroke();

        // Dots
        values.forEach((v, i) => {{
          if (v > 0) {{
            ctx.beginPath();
            ctx.arc(px(i), py(v), 3, 0, Math.PI * 2);
            ctx.fillStyle = '#ff6b35';
            ctx.fill();
          }}
        }});
      }}

      // X labels
      ctx.fillStyle = '#94a3b8';
      ctx.font = '10px monospace';
      ctx.textAlign = 'center';
      labels.forEach((l, i) => {{
        if (i % 5 === 0 || i === labels.length - 1) {{
          ctx.fillText(l.slice(5), px(i), H - 8);
        }}
      }});

      // Title
      ctx.fillStyle = '#e2e8f0';
      ctx.font = '600 13px sans-serif';
      ctx.textAlign = 'left';
      ctx.fillText('Visiteurs — 30 derniers jours', PL, 20);
    }}

    function roundRect(ctx, x, y, w, h, r) {{
      ctx.beginPath();
      ctx.moveTo(x + r, y);
      ctx.lineTo(x + w - r, y);
      ctx.quadraticCurveTo(x + w, y, x + w, y + r);
      ctx.lineTo(x + w, y + h - r);
      ctx.quadraticCurveTo(x + w, y + h, x + w - r, y + h);
      ctx.lineTo(x + r, y + h);
      ctx.quadraticCurveTo(x, y + h, x, y + h - r);
      ctx.lineTo(x, y + r);
      ctx.quadraticCurveTo(x, y, x + r, y);
      ctx.closePath();
    }}
  }})();
  </script>
</body>
</html>"""


def build_repo_html(repo: dict) -> str:
    name = safe(repo["name"])
    full_name = repo["full_name"]
    url = safe(repo["url"])
    desc_fr = safe(repo.get("description_fr") or repo.get("description") or "")
    desc_en = safe(repo.get("description") or "")
    stars = repo.get("stars", 0)
    lang = safe(repo.get("language") or "Unknown")
    cat = repo.get("category", "tools")
    license_ = safe(repo.get("license") or "Unknown")
    topics = repo.get("topics", [])
    now = now_str()

    topics_html = " ".join(
        f'<span class="topic-tag">{safe(t)}</span>' for t in topics[:10]
    )

    return f"""<!DOCTYPE html>
<html lang="fr">
<head>
  <meta charset="UTF-8"/>
  <meta name="viewport" content="width=device-width,initial-scale=1"/>
  <meta http-equiv="Content-Security-Policy" content="
    default-src 'self';
    script-src 'self' 'nonce-__CSP_NONCE__';
    style-src 'self' 'unsafe-inline';
    img-src 'self' data: https://img.shields.io https://raw.githubusercontent.com;
    connect-src 'self' https://api.github.com;
    frame-ancestors 'none';
    base-uri 'self';
    form-action 'self';
  "/>
  <meta name="referrer" content="strict-origin-when-cross-origin"/>
  <title>{name} — Openclaw Awesome Hub</title>
  <meta name="description" content="{desc_en}"/>
  <link rel="canonical" href="{BASE_URL}/repos/{full_name.replace('/','-')}.html"/>
  <link rel="stylesheet" href="../assets/style.css"/>
</head>
<body>
  <header class="page-header">
    <nav class="breadcrumb">
      <a href="../index.html" class="btn-back">← Accueil / Home</a>
      <a href="../index.html#{cat}" class="btn-back">← Catégorie</a>
    </nav>
    <h1 class="repo-title">{name}</h1>
    <div class="repo-meta-badges">
      <span class="badge badge--stars">⭐ {stars:,}</span>
      <span class="badge badge--lang">{lang}</span>
      <span class="badge badge--cat">{cat}</span>
      <span class="badge badge--license">{license_}</span>
    </div>
    {topics_html}
  </header>

  <main class="repo-page-content">
    <section class="repo-info">
      <a href="{url}" target="_blank" rel="noopener noreferrer" class="btn-primary">
        Voir le dépôt GitHub →
      </a>
      <table class="info-table">
        <tr><th>Description (FR)</th><td>{desc_fr}</td></tr>
        <tr><th>Description (EN)</th><td>{desc_en}</td></tr>
        <tr><th>Langage</th><td>{lang}</td></tr>
        <tr><th>Étoiles</th><td>{stars:,}</td></tr>
        <tr><th>Licence</th><td>{license_}</td></tr>
        <tr><th>Catégorie</th><td>{cat}</td></tr>
      </table>
    </section>

    <div id="readme-content" class="readme-content">
      <p class="loading">Chargement du README...</p>
    </div>
  </main>

  <footer class="site-footer">
    <a href="http://ThePhoenixAgency.github.io" target="_blank" rel="noopener noreferrer" class="footer-link">
      ThePhoenixAgency.github.io
    </a>
    <img src="../assets/phoenix-logo-small.svg" width="32" height="32" alt="Phoenix" class="footer-logo"/>
    <p class="footer-meta">Page mise à jour le {now}</p>
  </footer>

  <script nonce="__CSP_NONCE__">
  (function() {{
    'use strict';
    function sanitize(str) {{
      return String(str)
        .replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;')
        .replace(/"/g,'&quot;').replace(/'/g,'&#x27;')
        .replace(/javascript:/gi,'').replace(/data:/gi,'')
        .replace(/on\\w+=/gi,'');
    }}

    // Fetch README from GitHub API
    const readme = document.getElementById('readme-content');
    const apiUrl = 'https://api.github.com/repos/{full_name}/readme';
    fetch(apiUrl, {{
      headers: {{'Accept': 'application/vnd.github.html+json'}},
      mode: 'cors',
      cache: 'default',
    }})
    .then(r => r.ok ? r.text() : Promise.reject(r.status))
    .then(html => {{
      // Strip all script/iframe/on* attrs from fetched HTML
      const tmp = document.createElement('div');
      tmp.innerHTML = html;
      tmp.querySelectorAll('script,iframe,object,embed').forEach(el => el.remove());
      tmp.querySelectorAll('*').forEach(el => {{
        Array.from(el.attributes).forEach(attr => {{
          if (/^on/i.test(attr.name) || /javascript:/i.test(attr.value) || /data:/i.test(attr.value)) {{
            el.removeAttribute(attr.name);
          }}
        }});
      }});
      readme.innerHTML = tmp.innerHTML;
    }})
    .catch(() => {{
      readme.innerHTML = '<p>README non disponible. <a href="{url}" target="_blank" rel="noopener noreferrer">Voir sur GitHub →</a></p>';
    }});
  }})();
  </script>
</body>
</html>"""


def build_stats_html(visitors: dict, stats: dict) -> str:
    total = visitors.get("total", 0)
    daily = visitors.get("daily", {})
    recent = visitors.get("recent", [])[-5:]
    now = now_str()

    visitor_rows = ""
    for i in range(1, 6):
        if i <= len(recent):
            v = recent[i - 1]
            visitor_rows += (
                f"<tr><td>{i}</td><td>{safe(v.get('country','—'))}</td>"
                f"<td>{safe(v.get('time','—'))}</td><td>{safe(v.get('os','—'))}</td>"
                f"<td>{safe(v.get('page','—'))}</td></tr>\n"
            )
        else:
            visitor_rows += f"<tr><td>{i}</td><td>—</td><td>—</td><td>—</td><td>—</td></tr>\n"

    chart_labels = json.dumps(list(daily.keys())[-30:])
    chart_values = json.dumps(list(daily.values())[-30:])

    return f"""<!DOCTYPE html>
<html lang="fr">
<head>
  <meta charset="UTF-8"/>
  <meta name="viewport" content="width=device-width,initial-scale=1"/>
  <meta http-equiv="Content-Security-Policy" content="default-src 'self'; script-src 'self' 'nonce-__CSP_NONCE__'; style-src 'self' 'unsafe-inline'; img-src 'self' data:; frame-ancestors 'none';"/>
  <title>Statistiques — Openclaw Awesome Hub</title>
  <link rel="stylesheet" href="./assets/style.css"/>
</head>
<body>
  <header class="page-header">
    <nav class="breadcrumb">
      <a href="./index.html" class="btn-back">← Retour à l'accueil</a>
    </nav>
    <h1>Statistiques de visites</h1>
  </header>
  <main class="main-content">
    <div class="global-stats">
      <span>👥 {total:,} visites totales</span>
      <span>📦 {stats.get('total',0):,} repos suivis</span>
    </div>
    <canvas id="visitor-chart" width="800" height="280"></canvas>
    <h2>5 derniers visiteurs</h2>
    <table class="visitor-table">
      <thead><tr><th>#</th><th>Pays</th><th>Heure</th><th>OS</th><th>Page</th></tr></thead>
      <tbody>{visitor_rows}</tbody>
    </table>
  </main>
  <footer class="site-footer">
    <a href="http://ThePhoenixAgency.github.io" target="_blank" rel="noopener noreferrer">ThePhoenixAgency.github.io</a>
    <img src="./assets/phoenix-logo-small.svg" width="32" height="32" alt="Phoenix" class="footer-logo"/>
    <p class="footer-meta">Mis à jour le {now}</p>
  </footer>
  <script nonce="__CSP_NONCE__">
  (function(){{
    const labels={chart_labels}, values={chart_values};
    const canvas=document.getElementById('visitor-chart');
    if(!canvas||!canvas.getContext) return;
    const ctx=canvas.getContext('2d');
    const W=800,H=280,PL=50,PR=20,PT=30,PB=45;
    const cW=W-PL-PR,cH=H-PT-PB;
    const maxV=Math.max(...values,1);
    function px(i){{return PL+(i/Math.max(values.length-1,1))*cW;}}
    function py(v){{return PT+cH-(v/maxV)*cH;}}
    ctx.fillStyle='#0d1117';ctx.fillRect(0,0,W,H);
    if(values.length>1){{
      const g=ctx.createLinearGradient(0,PT,0,PT+cH);
      g.addColorStop(0,'rgba(255,107,53,0.4)');g.addColorStop(1,'rgba(255,107,53,0.02)');
      ctx.fillStyle=g;ctx.beginPath();ctx.moveTo(px(0),PT+cH);
      values.forEach((v,i)=>ctx.lineTo(px(i),py(v)));
      ctx.lineTo(px(values.length-1),PT+cH);ctx.closePath();ctx.fill();
      ctx.strokeStyle='#ff6b35';ctx.lineWidth=2.5;ctx.beginPath();
      values.forEach((v,i)=>i===0?ctx.moveTo(px(i),py(v)):ctx.lineTo(px(i),py(v)));
      ctx.stroke();
    }}
  }})();
  </script>
</body>
</html>"""


def main():
    print(f"[{datetime.now().strftime('%H:%M:%S')}] Building site...")
    repos = load_repos()
    visitors = load_visitors()
    stats = load_stats()

    # Copy static assets
    src_assets = ROOT / "assets"
    dst_assets = DOCS_DIR / "assets"
    if src_assets.exists():
        shutil.copytree(src_assets, dst_assets, dirs_exist_ok=True)
    if (DATA_DIR / "visitor-graph.svg").exists():
        shutil.copy(DATA_DIR / "visitor-graph.svg", dst_assets / "visitor-graph.svg")

    # Build index
    index_html = build_index(repos, stats, visitors)
    (DOCS_DIR / "index.html").write_text(index_html, encoding="utf-8")
    print("  Built: docs/index.html")

    # Build stats page
    stats_html = build_stats_html(visitors, stats)
    (DOCS_DIR / "stats.html").write_text(stats_html, encoding="utf-8")
    print("  Built: docs/stats.html")

    # Build individual repo pages
    built = 0
    for repo in repos:
        full_name = repo["full_name"]
        out = REPOS_HTML_DIR / f"{full_name.replace('/', '-')}.html"
        if not out.exists():
            out.write_text(build_repo_html(repo), encoding="utf-8")
            built += 1
    print(f"  Built {built} new repo pages.")

    # Create 404 page
    (DOCS_DIR / "404.html").write_text(
        f"""<!DOCTYPE html><html lang="fr"><head><meta charset="UTF-8"/>
<meta name="viewport" content="width=device-width,initial-scale=1"/>
<meta http-equiv="Content-Security-Policy" content="default-src 'self'; style-src 'self' 'unsafe-inline'; frame-ancestors 'none';"/>
<title>404 — Openclaw Awesome Hub</title>
<link rel="stylesheet" href="./assets/style.css"/>
</head><body>
<div style="text-align:center;padding:4rem">
<h1>404</h1><p>Page non trouvée / Page not found</p>
<a href="./index.html">← Retour / Back</a>
</div>
</body></html>""",
        encoding="utf-8"
    )

    print("  Site build complete.")


if __name__ == "__main__":
    main()
