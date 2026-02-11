import subprocess, json
from pathlib import Path
from diff_parser import parse_diff, find_diff_position
from groq_client import call_llm
from github_api import post_inline_comment

def load_prompt(diff):
    template = Path("ai_reviewer/prompt.txt").read_text()
    return template.replace("{diff}", diff)

def get_diff():
    return subprocess.check_output(["git", "diff", "origin/main...HEAD"]).decode()

def chunk_text(text, size=7000):
    return [text[i:i+size] for i in range(0, len(text), size)]

def main():
    diff = get_diff()
    patch = parse_diff(diff)

    issues_all = []

    for chunk in chunk_text(diff):
        prompt = load_prompt(chunk)
        response = call_llm(prompt)
        try:
            issues = json.loads(response)
            issues_all.extend(issues)
        except Exception:
            continue

        seen = set()
        final_issues = []
        for i in issues_all:
            key = (i["file"], i["line"], i["comment"])
            if key not in seen:
                seen.add(key)
                final_issues.append(i)

        for issue in final_issues:
            pos = find_diff_position(patch, issue["file"], issue["line"])
            if pos:
                comment = f"[{issue['severity']}] {issue['comment']}"
                post_inline_comment(issue["file"], pos, comment)

if __name__ == "__main__":
    main()