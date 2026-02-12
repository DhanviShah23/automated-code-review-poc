
import subprocess, json
from pathlib import Path
from diff_parser import parse_diff, find_diff_position
from groq_client import call_llm
from github_api import post_inline_comment
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

def main():
    diff = get_diff()
    if not diff.strip():
        print("No diff detected")
        return

    patch = parse_diff(diff)
    issues_all = []

    # ---- CALL LLM IN CHUNKS ----
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

    # ---- DEDUPLICATE ----
    seen = set()
    final_issues = []
    for i in issues_all:
        key = (i.get("file"), i.get("line"), i.get("comment"))
        if key not in seen:
            seen.add(key)
            final_issues.append(i)

    # ---- FILTER ONLY REAL DIFF FILES ----
    valid_files = {pf.path.split("/")[-1] for pf in patch}

    final_issues = [
        i for i in final_issues
        if i.get("file")
        and i["file"].split("/")[-1] in valid_files
        and i.get("line", 0) > 0
    ]

    critical_found = False

    # ---- POST INLINE COMMENTS ----
    for issue in final_issues:
        pos = find_diff_position(patch, issue["file"], issue["line"])
        print(f"DEBUG POS: {issue['file']}:{issue['line']} => {pos}")

        if not pos:
            continue

        comment = f"[{issue['severity']}] {issue['comment']}"
        post_inline_comment(issue["file"], pos, comment)

        if issue["severity"] in ["CRITICAL", "HIGH"]:
            critical_found = True

    # ---- FAIL PIPELINE ----
    if critical_found:
        print("❌ Critical issues detected. Failing pipeline.")
        exit(1)

    print("No critical issues")

if __name__ == "__main__":
    main()
