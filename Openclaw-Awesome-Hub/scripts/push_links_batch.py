#!/usr/bin/env python3
"""
Push 5 new links at a time to the 'Links' branch.
No external dependencies — stdlib + GitHub API via urllib.
"""

import base64
import json
import os
import time
import urllib.request
import urllib.parse
from datetime import datetime, timezone
from pathlib import Path

GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN", "")
REPO_NAME = os.environ.get("REPO_NAME", "ThePhoenixAgency/Openclaw-Awesome-Hub")
ROOT = Path(__file__).parent.parent
DATA_DIR = ROOT / "data"
BATCH_SIZE = 5
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
            content = e.read().decode("utf-8", errors="ignore")
            if e.code == 404:
                return {}
            if e.code == 422:
                return {"error": "exists"}
            wait = 2 ** attempt
            print(f"  HTTP {e.code} (attempt {attempt+1}): {content[:200]}")
            time.sleep(wait)
        except Exception as e:
            wait = 2 ** attempt
            print(f"  Error (attempt {attempt+1}): {e}")
            time.sleep(wait)
    return {}


def get_branch_sha(branch: str) -> str:
    resp = github_api("GET", f"/repos/{REPO_NAME}/git/ref/heads/{branch}")
    return resp.get("object", {}).get("sha", "")


def ensure_links_branch() -> str:
    """Create Links branch from main if it doesn't exist."""
    sha = get_branch_sha(LINKS_BRANCH)
    if sha:
        return sha
    main_sha = get_branch_sha(BASE_BRANCH)
    if not main_sha:
        print("  Cannot get main branch SHA.")
        return ""
    resp = github_api("POST", f"/repos/{REPO_NAME}/git/refs", {
        "ref": f"refs/heads/{LINKS_BRANCH}",
        "sha": main_sha,
    })
    return resp.get("object", {}).get("sha", main_sha)


def get_already_pushed_links() -> set:
    """Get links already committed in the Links branch."""
    resp = github_api("GET", f"/repos/{REPO_NAME}/contents/data/links-pushed.json?ref={LINKS_BRANCH}")
    if not resp or "content" not in resp:
        return set()
    content = base64.b64decode(resp["content"]).decode("utf-8")
    return set(json.loads(content))


def load_all_repo_urls() -> list:
    f = DATA_DIR / "repos.json"
    if not f.exists():
        return []
    with open(f, encoding="utf-8") as fh:
        repos = json.load(fh).get("repos", [])
    return [r["url"] for r in repos]


def build_links_file_content(urls: list) -> str:
    """Build markdown list of links."""
    lines = [
        "# Links — OpenClaw Ecosystem",
        f"*Dernière mise à jour / Last updated: {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}*",
        "",
        "## Liens / Links",
        "",
    ]
    for url in urls:
        lines.append(f"- {url}")
    return "\n".join(lines)


def create_blob(content: str) -> str:
    resp = github_api("POST", f"/repos/{REPO_NAME}/git/blobs", {
        "content": content,
        "encoding": "utf-8",
    })
    return resp.get("sha", "")


def create_tree(base_tree_sha: str, files: dict) -> str:
    tree = []
    for path, content in files.items():
        blob_sha = create_blob(content)
        if blob_sha:
            tree.append({
                "path": path,
                "mode": "100644",
                "type": "blob",
                "sha": blob_sha,
            })
    resp = github_api("POST", f"/repos/{REPO_NAME}/git/trees", {
        "base_tree": base_tree_sha,
        "tree": tree,
    })
    return resp.get("sha", "")


def create_commit(tree_sha: str, parent_sha: str, message: str) -> str:
    resp = github_api("POST", f"/repos/{REPO_NAME}/git/commits", {
        "message": message,
        "tree": tree_sha,
        "parents": [parent_sha],
        "author": {
            "name": "github-actions[bot]",
            "email": "github-actions[bot]@users.noreply.github.com",
            "date": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        },
    })
    return resp.get("sha", "")


def update_branch_ref(branch: str, sha: str) -> None:
    github_api("PATCH", f"/repos/{REPO_NAME}/git/refs/heads/{branch}", {
        "sha": sha,
        "force": False,
    })


def main():
    if not GITHUB_TOKEN:
        print("No GITHUB_TOKEN set.")
        return

    print(f"  Checking Links branch...")
    branch_sha = ensure_links_branch()
    if not branch_sha:
        print("  Failed to ensure Links branch.")
        return

    all_urls = load_all_repo_urls()
    pushed = get_already_pushed_links()
    new_urls = [u for u in all_urls if u not in pushed][:BATCH_SIZE]

    if not new_urls:
        print("  No new links to push.")
        return

    print(f"  Pushing {len(new_urls)} new links to '{LINKS_BRANCH}'...")

    updated_pushed = sorted(pushed | set(new_urls))
    links_md = build_links_file_content(updated_pushed)
    pushed_json = json.dumps(sorted(updated_pushed), indent=2)

    tree_sha = create_tree(branch_sha, {
        "data/links.md": links_md,
        "data/links-pushed.json": pushed_json,
    })
    if not tree_sha:
        print("  Failed to create tree.")
        return

    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    commit_sha = create_commit(tree_sha, branch_sha, f"links: add {len(new_urls)} repos — {now} [skip ci]")
    if not commit_sha:
        print("  Failed to create commit.")
        return

    update_branch_ref(LINKS_BRANCH, commit_sha)
    print(f"  Done. {len(new_urls)} links pushed to '{LINKS_BRANCH}'.")


if __name__ == "__main__":
    main()
