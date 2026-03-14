#!/usr/bin/env python3
"""
Generate the visitor progression SVG graph and update visitor data.
Pure stdlib — no matplotlib, no external deps.
"""

import json
import os
from datetime import datetime, timezone, timedelta
from pathlib import Path
from collections import defaultdict

ROOT = Path(__file__).parent.parent
DATA_DIR = ROOT / "data"
DATA_DIR.mkdir(exist_ok=True)

VISITORS_FILE = DATA_DIR / "visitors.json"
GRAPH_FILE = DATA_DIR / "visitor-graph.svg"

W, H = 800, 280
PAD_L, PAD_R, PAD_T, PAD_B = 60, 20, 30, 50


def load_visitors() -> dict:
    if VISITORS_FILE.exists():
        with open(VISITORS_FILE, encoding="utf-8") as f:
            return json.load(f)
    return {"recent": [], "daily": {}, "total": 0}


def save_visitors(data: dict) -> None:
    with open(VISITORS_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def record_visit(country: str = "Unknown", page: str = "/", os_name: str = "Unknown") -> None:
    data = load_visitors()
    now = datetime.now(timezone.utc)
    today = now.strftime("%Y-%m-%d")

    visit = {
        "country": country,
        "page": page,
        "os": os_name,
        "time": now.strftime("%Y-%m-%d %H:%M UTC"),
    }
    data.setdefault("recent", []).append(visit)
    data["recent"] = data["recent"][-50:]  # Keep last 50

    data.setdefault("daily", {})[today] = data["daily"].get(today, 0) + 1
    data["total"] = data.get("total", 0) + 1

    save_visitors(data)


def generate_graph_svg(data: dict) -> str:
    """Generate an SVG line chart of daily visitors for the past 30 days."""
    daily = data.get("daily", {})
    total = data.get("total", 0)

    # Last 30 days
    today = datetime.now(timezone.utc).date()
    days = [(today - timedelta(days=i)) for i in range(29, -1, -1)]
    labels = [d.strftime("%d/%m") for d in days]
    values = [daily.get(d.strftime("%Y-%m-%d"), 0) for d in days]

    max_val = max(values) if any(v > 0 for v in values) else 1
    chart_w = W - PAD_L - PAD_R
    chart_h = H - PAD_T - PAD_B

    def x(i):
        return PAD_L + (i / (len(values) - 1)) * chart_w

    def y(v):
        return PAD_T + chart_h - (v / max_val) * chart_h

    # Build polyline points
    points = " ".join(f"{x(i):.1f},{y(v):.1f}" for i, v in enumerate(values))

    # Area fill points (closed path)
    area_points = (
        f"{x(0):.1f},{PAD_T + chart_h:.1f} "
        + points
        + f" {x(len(values)-1):.1f},{PAD_T + chart_h:.1f}"
    )

    # Grid lines and labels
    grid_lines = []
    y_ticks = 5
    for i in range(y_ticks + 1):
        val = (max_val * i) / y_ticks
        ypos = y(val)
        grid_lines.append(
            f'<line x1="{PAD_L}" y1="{ypos:.1f}" x2="{W - PAD_R}" y2="{ypos:.1f}" '
            f'stroke="#ffffff10" stroke-width="1"/>'
        )
        grid_lines.append(
            f'<text x="{PAD_L - 8}" y="{ypos + 4:.1f}" '
            f'font-family="monospace" font-size="10" fill="#94a3b8" text-anchor="end">'
            f'{int(val)}</text>'
        )

    # X-axis labels (every 5 days)
    x_labels = []
    for i, label in enumerate(labels):
        if i % 5 == 0 or i == len(labels) - 1:
            xpos = x(i)
            x_labels.append(
                f'<text x="{xpos:.1f}" y="{H - 8}" '
                f'font-family="monospace" font-size="10" fill="#94a3b8" text-anchor="middle">'
                f'{label}</text>'
            )

    # Data points
    dots = []
    for i, v in enumerate(values):
        if v > 0:
            dots.append(
                f'<circle cx="{x(i):.1f}" cy="{y(v):.1f}" r="3" fill="#ff6b35" '
                f'stroke="#0d1117" stroke-width="1.5"/>'
            )

    svg = f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}">
  <defs>
    <linearGradient id="areaGrad" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0%" stop-color="#ff6b35" stop-opacity="0.4"/>
      <stop offset="100%" stop-color="#ff6b35" stop-opacity="0.02"/>
    </linearGradient>
    <linearGradient id="lineGrad" x1="0" y1="0" x2="1" y2="0">
      <stop offset="0%" stop-color="#ff6b35"/>
      <stop offset="100%" stop-color="#f7931e"/>
    </linearGradient>
  </defs>

  <!-- Background -->
  <rect width="{W}" height="{H}" rx="12" fill="#0d1117"/>
  <rect x="1" y="1" width="{W-2}" height="{H-2}" rx="12" fill="none" stroke="#ffffff12" stroke-width="1"/>

  <!-- Title -->
  <text x="{PAD_L}" y="20" font-family="'Segoe UI',Arial,sans-serif" font-size="13"
        font-weight="600" fill="#e2e8f0">Visiteurs / Visitors — 30 derniers jours</text>
  <text x="{W - PAD_R}" y="20" font-family="monospace" font-size="12" fill="#ff6b35"
        text-anchor="end">Total: {total:,}</text>

  <!-- Grid -->
  {"".join(grid_lines)}

  <!-- Area fill -->
  <polygon points="{area_points}" fill="url(#areaGrad)"/>

  <!-- Line -->
  <polyline points="{points}" fill="none" stroke="url(#lineGrad)" stroke-width="2.5"
            stroke-linejoin="round" stroke-linecap="round"/>

  <!-- Data points -->
  {"".join(dots)}

  <!-- X axis -->
  <line x1="{PAD_L}" y1="{PAD_T + chart_h}" x2="{W - PAD_R}" y2="{PAD_T + chart_h}"
        stroke="#ffffff20" stroke-width="1"/>
  {"".join(x_labels)}
</svg>"""
    return svg


def main():
    country = os.environ.get("VISITOR_COUNTRY", "")
    page = os.environ.get("VISITOR_PAGE", "")
    os_name = os.environ.get("VISITOR_OS", "")

    data = load_visitors()

    if country:
        record_visit(country, page, os_name)
        data = load_visitors()

    svg = generate_graph_svg(data)
    GRAPH_FILE.write_text(svg, encoding="utf-8")
    print(f"  Graph updated. Total visitors: {data.get('total', 0)}")


if __name__ == "__main__":
    main()
