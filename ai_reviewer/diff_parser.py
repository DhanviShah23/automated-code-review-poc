# from unidiff import PatchSet

# def parse_diff(diff_text):
#     return PatchSet(diff_text)

# def find_diff_position(patch, file_path, target_line):
#     for pf in patch:
#         if pf.path == file_path:
#             pos = 0
#             for hunk in pf:
#                 for line in hunk:
#                     pos += 1
#                     if line.target_line_no == target_line:
#                         return pos
#     return None

import subprocess

def get_diff():
    return subprocess.check_output(["git", "diff", "origin/main...HEAD"]).decode()