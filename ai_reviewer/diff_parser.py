from unidiff import PatchSet

def parse_diff(diff_text):
    return PatchSet(diff_text)

def find_diff_position(patch, file, line):
    for pf in patch:
        if pf.path.endswith(file):
            for hunk in pf.hunks:
                for i, diff_line in enumerate(hunk.lines):
                    if diff_line.target_line_no == line:
                        return diff_line.position
    return None
