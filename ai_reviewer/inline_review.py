
import subprocess, json
from pathlib import Path
from diff_parser import parse_diff, find_diff_position
from groq_client import call_llm
from github_api import post_inline_comment, get_existing_comments
import os
import re


def extract_json(text: str) -> str:
    """
    Extract first valid JSON array or object from LLM output.
    Handles markdown, extra text, broken fences.
    """
    # Remove markdown fences
    text = re.sub(r"```.*?\n", "", text)
    text = text.replace("```", "").strip()

    # Find JSON array or object
    match = re.search(r"(\[.*\]|\{.*\})", text, re.S)
    if not match:
        raise ValueError("No JSON found in LLM output")

    return match.group(1)

def load_prompt(diff):
    template = Path("ai_reviewer/prompt.txt").read_text()
    return template.replace("{diff}", diff)

def get_diff():
    base = os.getenv("GITHUB_BASE_REF", "main")
    return subprocess.check_output(["git", "diff", f"origin/{base}...HEAD"]).decode()

def chunk_text(text, size=7000):
    return [text[i:i+size] for i in range(0, len(text), size)]

def annotate_diff(diff):
    annotated = []
    for i, line in enumerate(diff.splitlines(), 1):
        annotated.append(f"{i}: {line}")
    return "\n".join(annotated)

def main():
    raw_diff = get_diff()
    diff = annotate_diff(raw_diff)
    if not diff.strip():
        print("No diff detected")
        return

    patch = parse_diff(diff)
    issues_all = []

    for chunk in chunk_text(diff):
        prompt = load_prompt(chunk)
        response = call_llm(prompt)

        print("RAW AI OUTPUT:\n", response)

        response = extract_json(response)

        try:
            issues = json.loads(response)
            issues_all.extend(issues)
        except Exception as e:
            print("JSON parse failed:", e)
            print("RAW:", response)

    seen = set()
    final_issues = []
    for i in issues_all:
        key = (i.get("file"), i.get("line"), i.get("comment"))
        if key not in seen:
            seen.add(key)
            final_issues.append(i)

    valid_files = {pf.path.split("/")[-1] for pf in patch}

    final_issues = [
        i for i in final_issues
        if i.get("file")
        and i["file"].split("/")[-1] in valid_files
        and i.get("line", 0) > 0
    ]

    SECURITY_KEYWORDS = ["eval", "password", "token", "secret", "innerHTML", "document"]

    def is_real_security_issue(issue):
        text = issue["comment"].lower()
        return any(k in text for k in SECURITY_KEYWORDS)

    filtered = []
    for i in final_issues:
        if i["severity"] in ["HIGH", "CRITICAL"]:
            if not is_real_security_issue(i):
                print("Skipping hallucinated security issue:", i)
                continue
        filtered.append(i)

    final_issues = filtered

    critical_found = False

    existing_comments = get_existing_comments()
    existing_keys = {
        (c["path"], c["position"], c["body"])
        for c in existing_comments
    }

    for issue in final_issues:
        pos = find_diff_position(patch, issue["file"], issue["line"])
        print(f"DEBUG POS: {issue['file']}:{issue['line']} => {pos}")

        if not pos:
            continue

        comment = f"[{issue['severity']}] {issue['comment']}"

        key = (issue["file"], pos, comment)
        if key in existing_keys:
            print("Skipping duplicate:", key)
            continue

        post_inline_comment(issue["file"], pos, comment)

        if issue["severity"] in ["CRITICAL", "HIGH"]:
            critical_found = True

    if critical_found:
        print("❌ Critical issues detected. Failing pipeline.")
        exit(1)

    print("No critical issues")

if __name__ == "__main__":
    main()
