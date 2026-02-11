from groq_client import call_llm
from diff_parser import get_diff
from github_client import post_inline_comments

CRITICAL_KEYWORDS = ["eval(", "password", "hardcoded", "sql injection", "xss"]

def build_prompt(diff):
    return f"""
Review this code diff. Output JSON array:
[
  {{ "file": "...", "line": 10, "comment": "...", "severity": "LOW|MEDIUM|CRITICAL" }}
]
Code:
{diff}
"""

def main():
    diff = get_diff()
    if not diff:
        print("No diff found")
        return

    response = call_llm(build_prompt(diff))
    print("LLM RAW:", response)

    import json
    issues = json.loads(response)

    comments = []
    critical_found = False

    for i in issues:
        comments.append({
            "path": i["file"],
            "line": i["line"],
            "side": "RIGHT",
            "body": f"**{i['severity']}**: {i['comment']}"
        })

        if i["severity"] == "CRITICAL":
            critical_found = True

    post_inline_comments(comments)

    if critical_found:
        print("Critical issues detected. Failing pipeline.")
        exit(1)

    print("No critical issues")

if __name__ == "__main__":
    main()
