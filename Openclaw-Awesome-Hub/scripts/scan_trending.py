#!/usr/bin/env python3
"""
Scan GitHub for trending OpenClaw-related repositories.
No external dependencies — uses only stdlib urllib.
"""

import json
import os
import re
import time
import urllib.request
import urllib.parse
import urllib.error
from datetime import datetime, timezone
from pathlib import Path

# ── Configuration ──────────────────────────────────────────────────────────────

GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN", "")
MAX_REPOS = int(os.environ.get("MAX_REPOS", "50"))
ROOT = Path(__file__).parent.parent
DATA_DIR = ROOT / "data"
DATA_DIR.mkdir(exist_ok=True)

SEARCH_KEYWORDS = [
    "openclaw",
    "open-claw",
    "clawbot",
    "moltbot",
    "claw-robot",
    "claw arm robot",
    "robotic claw",
    "openclaw game",
    "captain claw",
    "vex claw robot",
    "gripper robot",
    "robot gripper",
    "claw machine robot",
    "open claw simulator",
]

CATEGORY_RULES = {
    "core_robotics": [
        r"openclaw", r"open.?claw", r"clawbot", r"moltbot",
        r"captain.?claw", r"claw.?engine", r"claw.?platformer",
    ],
    "arms_manipulation": [
        r"robot.?arm", r"robotic.?arm", r"gripper", r"manipulator",
        r"end.?effector", r"servo.?arm", r"3d.?printed.?arm",
    ],
    "motion_control": [
        r"motion.?control", r"pid", r"trajectory", r"kinematics",
        r"stepper", r"servo.?control", r"motor.?driv",
    ],
    "electronics": [
        r"arduino", r"esp32", r"raspberry.?pi", r"\bpcb\b", r"firmware",
        r"embedded", r"microcontroller",
    ],
    "ai_ml": [
        r"machine.?learning", r"deep.?learning", r"neural.?net",
        r"reinforcement", r"pytorch", r"tensorflow", r"robot.?ai",
    ],
    "computer_vision": [
        r"computer.?vision", r"opencv", r"image.?process",
        r"object.?detect", r"yolo", r"pose.?estimation",
    ],
    "simulation": [
        r"simulat", r"gazebo", r"mujoco", r"pybullet",
        r"physics.?engine", r"\burdf\b", r"\brviz\b",
    ],
    "iot": [
        r"\biot\b", r"\bmqtt\b", r"\bros\b", r"\bros2\b",
        r"websocket", r"telemetry", r"bluetooth",
    ],
    "tools": [
        r"\btool\b", r"utilit", r"\bsdk\b", r"\bapi\b",
        r"framework", r"parser", r"converter", r"library",
    ],
}


def github_get(url: str, params: dict = None) -> dict:
    """Make a GitHub API GET request with retry logic."""
    if params:
        url = url + "?" + urllib.parse.urlencode(params)

    headers = {
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
        "User-Agent": "Openclaw-Awesome-Hub/1.0",
    }
    if GITHUB_TOKEN:
        headers["Authorization"] = f"Bearer {GITHUB_TOKEN}"

    for attempt in range(4):
        try:
            req = urllib.request.Request(url, headers=headers)
            with urllib.request.urlopen(req, timeout=30) as resp:
                return json.loads(resp.read().decode("utf-8"))
        except urllib.error.HTTPError as e:
            if e.code == 403:
                reset = int(e.headers.get("X-RateLimit-Reset", time.time() + 60))
                wait = max(reset - time.time(), 1)
                print(f"    Rate limit hit, waiting {min(wait, 120):.0f}s...")
                time.sleep(min(wait, 120))
                continue
            if e.code == 422:
                print(f"    Invalid query, skipping.")
                return {"items": []}
            print(f"    HTTP {e.code}: {e.reason}")
            return {"items": []}
        except Exception as e:
            wait = 2 ** attempt
            print(f"    Error (attempt {attempt+1}): {e}. Retry in {wait}s...")
            time.sleep(wait)
    return {"items": []}


def classify_repo(repo: dict) -> str:
    text = " ".join(filter(None, [
        repo.get("name", ""),
        repo.get("description", "") or "",
        " ".join(repo.get("topics", [])),
        repo.get("language", "") or "",
    ])).lower()

    for category, patterns in CATEGORY_RULES.items():
        for pattern in patterns:
            if re.search(pattern, text, re.IGNORECASE):
                return category
    return "tools"


def normalize_repo(raw: dict, category: str) -> dict:
    return {
        "id": raw["id"],
        "name": raw["name"],
        "full_name": raw["full_name"],
        "owner": raw["owner"]["login"],
        "url": raw["html_url"],
        "description": raw.get("description") or "",
        "description_fr": "",
        "stars": raw["stargazers_count"],
        "forks_count": raw["forks_count"],
        "language": raw.get("language") or "Unknown",
        "topics": raw.get("topics", []),
        "is_fork": raw.get("fork", False),
        "license": (raw.get("license") or {}).get("spdx_id", "Unknown"),
        "created_at": raw.get("created_at", ""),
        "updated_at": raw.get("updated_at", ""),
        "category": category,
        "page": 1,
        "added_at": datetime.now(timezone.utc).isoformat(),
    }


def load_existing() -> dict:
    f = DATA_DIR / "repos.json"
    if f.exists():
        with open(f, encoding="utf-8") as fh:
            return json.load(fh)
    return {"repos": [], "last_scan": None, "total_found": 0}


def save_data(data: dict) -> None:
    with open(DATA_DIR / "repos.json", "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def save_stats(repos: list) -> None:
    stats = {
        "categories": {cat: 0 for cat in CATEGORY_RULES},
        "total": len(repos),
        "last_update": datetime.now(timezone.utc).isoformat(),
    }
    for r in repos:
        cat = r.get("category", "tools")
        stats["categories"][cat] = stats["categories"].get(cat, 0) + 1

    with open(DATA_DIR / "stats.json", "w", encoding="utf-8") as f:
        json.dump(stats, f, indent=2)


def main():
    ts = datetime.now().strftime("%H:%M:%S")
    print(f"[{ts}] Starting OpenClaw repo scan...")

    existing = load_existing()
    seen_ids = {r["id"] for r in existing.get("repos", [])}
    new_repos = []

    for keyword in SEARCH_KEYWORDS:
        print(f"  Searching: '{keyword}'...")
        result = github_get(
            "https://api.github.com/search/repositories",
            {
                "q": f"{keyword} fork:false",
                "sort": "stars",
                "order": "desc",
                "per_page": min(MAX_REPOS, 100),
            },
        )
        items = result.get("items", [])
        added = 0
        for raw in items:
            if raw.get("fork", False):
                continue
            if raw["id"] in seen_ids:
                continue
            if raw["stargazers_count"] < 1:
                continue
            cat = classify_repo(raw)
            new_repos.append(normalize_repo(raw, cat))
            seen_ids.add(raw["id"])
            added += 1
        print(f"    {len(items)} results, {added} new repos added.")
        time.sleep(1.2)  # Rate limit courtesy pause

    all_repos = existing.get("repos", []) + new_repos
    all_repos.sort(key=lambda r: r["stars"], reverse=True)

    # Assign pages (50 per page)
    REPOS_PER_PAGE = 50
    for i, repo in enumerate(all_repos):
        repo["page"] = (i // REPOS_PER_PAGE) + 1

    data = {
        "repos": all_repos,
        "last_scan": datetime.now(timezone.utc).isoformat(),
        "total_found": len(all_repos),
        "new_this_scan": len(new_repos),
    }
    save_data(data)
    save_stats(all_repos)

    print(f"  Done. Total: {len(all_repos)} repos (+{len(new_repos)} new).")


if __name__ == "__main__":
    main()
