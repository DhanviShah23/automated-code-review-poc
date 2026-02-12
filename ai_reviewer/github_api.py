import os, requests

TOKEN = os.getenv("GITHUB_TOKEN")
REPO = os.getenv("GITHUB_REPOSITORY")
PR = os.getenv("PR_NUMBER")
HEAD_SHA = os.getenv("GITHUB_HEAD_SHA")

def post_inline_comment(path, position, body):
    url = f"https://api.github.com/repos/{REPO}/pulls/{PR}/comments"

    payload = {
        "body": body,
        "commit_id": HEAD_SHA,
        "path": path,
        "position": position
    }

    headers = {
        "Authorization": f"Bearer {TOKEN}",
        "Accept": "application/vnd.github+json"
    }

    r = requests.post(url, json=payload, headers=headers)
    print("COMMENT API:", r.status_code, r.text)

def get_existing_comments():
    url = f"https://api.github.com/repos/{REPO}/pulls/{PR}/comments"
    headers = {"Authorization": f"Bearer {TOKEN}"}
    res = requests.get(url, headers=headers)
    res.raise_for_status()
    return res.json()