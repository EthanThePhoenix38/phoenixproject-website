#!/usr/bin/env python3
"""
Create a silent auto-PR from Links branch to main.
Checks if a PR already exists to avoid duplicates.
No external dependencies.
"""

import json
import os
import time
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN", "")
REPO_NAME = os.environ.get("REPO_NAME", "ThePhoenixAgency/Openclaw-Awesome-Hub")
LINKS_BRANCH = "Links"
BASE_BRANCH = "main"


def github_api(method: str, path: str, body: dict = None) -> dict:
    url = f"https://api.github.com{path}"
    headers = {
        "Accept": "application/vnd.github+json",
        "Authorization": f"Bearer {GITHUB_TOKEN}",
        "X-GitHub-Api-Version": "2022-11-28",
        "User-Agent": "Openclaw-Awesome-Hub/1.0",
        "Content-Type": "application/json",
    }
    data = json.dumps(body).encode() if body else None
    req = urllib.request.Request(url, data=data, headers=headers, method=method)
    for attempt in range(4):
        try:
            with urllib.request.urlopen(req, timeout=30) as resp:
                return json.loads(resp.read().decode("utf-8"))
        except urllib.error.HTTPError as e:
            if e.code == 422:
                return {"error": "already_exists"}
            wait = 2 ** attempt
            time.sleep(wait)
        except Exception as e:
            wait = 2 ** attempt
            time.sleep(wait)
    return {}


def get_open_prs_from_links() -> list:
    resp = github_api(
        "GET",
        f"/repos/{REPO_NAME}/pulls?state=open&head=ThePhoenixAgency:{LINKS_BRANCH}&base={BASE_BRANCH}&per_page=5",
    )
    return resp if isinstance(resp, list) else []


def create_pr(batch_count: int) -> None:
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    body = (
        f"Automated batch of {batch_count} new repository links.\n\n"
        f"Generated: {now}\n\n"
        f"*This PR was created automatically by the hourly scan workflow.*"
    )
    resp = github_api("POST", f"/repos/{REPO_NAME}/pulls", {
        "title": f"links: {batch_count} new repos — {now}",
        "body": body,
        "head": LINKS_BRANCH,
        "base": BASE_BRANCH,
        "draft": False,
    })
    if "number" in resp:
        print(f"  PR #{resp['number']} created: {resp.get('html_url','')}")

        # Auto-approve as bot (add label)
        github_api("POST", f"/repos/{REPO_NAME}/issues/{resp['number']}/labels", {
            "labels": ["auto-links", "bot"],
        })

        # Enable auto-merge if available
        github_api("PUT", f"/repos/{REPO_NAME}/pulls/{resp['number']}/merge", {
            "merge_method": "squash",
            "commit_title": f"links: merge {batch_count} new repos [skip ci]",
        })
    elif resp.get("error") == "already_exists":
        print("  PR already exists.")
    else:
        print(f"  PR creation response: {resp}")


def main():
    if not GITHUB_TOKEN:
        print("  No GITHUB_TOKEN.")
        return

    existing_prs = get_open_prs_from_links()
    if existing_prs:
        print(f"  PR already open (#{existing_prs[0].get('number','')}). Skipping.")
        return

    # Get count of links pushed in last batch (read from data file)
    links_file = Path(__file__).parent.parent / "data" / "links-pushed.json"
    batch_count = 5  # Default
    if links_file.exists():
        with open(links_file) as f:
            try:
                batch_count = min(5, len(json.load(f)))
            except Exception:
                pass

    create_pr(batch_count)


if __name__ == "__main__":
    main()
