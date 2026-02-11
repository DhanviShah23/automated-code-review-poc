
import subprocess, json
from pathlib import Path
from diff_parser import parse_diff, find_diff_position
from groq_client import call_llm
from github_api import post_inline_comment
import os

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

    for chunk in chunk_text(diff):
        prompt = load_prompt(chunk)
        response = call_llm(prompt)

        print("RAW AI OUTPUT:\n", response)

        # Remove markdown if AI adds it
        response = response.replace("```json", "").replace("```", "").strip()

        try:
            issues = json.loads(response)
            issues_all.extend(issues)
        except Exception as e:
            print("JSON parse failed:", e)
            continue

    # Deduplicate issues AFTER all chunks
    seen = set()
    final_issues = []
    for i in issues_all:
        key = (i["file"], i["line"], i["comment"])
        if key not in seen:
            seen.add(key)
            final_issues.append(i)

    critical_found = False
            
    for issue in final_issues:
        pos = find_diff_position(patch, issue["file"], issue["line"])

        if not pos:
            print(f"⚠️ Could not map diff position for {issue}")
            continue

        comment = f"[{issue['severity']}] {issue['comment']}"
        post_inline_comment(issue["file"], pos, comment)
    
    if critical_found:
        print("❌ Critical issues detected. Failing pipeline.")
        exit(1)

    print("No critical issues")

if __name__ == "__main__":
    main()
