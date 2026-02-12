import os
import requests

GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
REPO = os.getenv("GITHUB_REPOSITORY")
PR_NUMBER = os.getenv("PR_NUMBER")
HEAD_SHA = os.getenv("GITHUB_HEAD_SHA") or os.getenv("GITHUB_SHA")

def post_inline_comment(file, position, comment):
    url = f"https://api.github.com/repos/{REPO}/pulls/{PR_NUMBER}/comments"

    payload = {
        "body": comment,
        "commit_id": HEAD_SHA,
        "path": file,
        "position": position
    }

    headers = {
        "Authorization": f"Bearer {GITHUB_TOKEN}",
        "Accept": "application/vnd.github+json"
    }

    res = requests.post(url, json=payload, headers=headers)
    if res.status_code >= 300:
        print("GitHub comment failed:", res.status_code, res.text)
