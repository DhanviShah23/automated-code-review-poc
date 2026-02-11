import requests, os, json

def post_inline_comments(comments):
    token = os.getenv("GITHUB_TOKEN")
    repo = os.getenv("GITHUB_REPOSITORY")
    pr = os.getenv("PR_NUMBER")

    url = f"https://api.github.com/repos/{repo}/pulls/{pr}/reviews"
    headers = {"Authorization": f"Bearer {token}"}

    payload = {
        "body": "AI Code Review",
        "event": "COMMENT",
        "comments": comments
    }

    r = requests.post(url, headers=headers, json=payload)
    print("GitHub response:", r.status_code, r.text)
