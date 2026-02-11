import os, requests

token = os.getenv("GITHUB_TOKEN")
repo = os.getenv("GITHUB_REPOSITORY")
pr = os.getenv("PR_NUMBER")
commit_sha = os.getenv("GITHUB_HEAD_SHA") or os.getenv("GITHUB_SHA")

headers = {"Authorization": f"Bearer {token}"}

def post_inline_comment(file, position, body):
    url = f"https://api.github.com/repos/{repo}/pulls/{pr}/comments"
    payload = {
    "body": body,
    "commit_id": commit_sha,
    "path": file,
    "position": position
    }
    requests.post(url, headers=headers, json=payload)