from unidiff import PatchSet

def parse_diff(diff_text):
    return PatchSet(diff_text)

def find_diff_position(patch, filename, target_line):
    for pf in patch:
        if pf.path.endswith(filename):
            position = 0
            for hunk in pf:
                for line in hunk:
                    position += 1
                    if line.target_line_no == target_line and (line.is_added or line.is_context):
                        return position
    return None
