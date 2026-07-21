import os
import sys

# Safe print setup
if sys.stdout.encoding != 'utf-8':
    try:
        import codecs
        sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'replace')
    except Exception:
        pass

base_dir = "c:/Users/a2132/Documents/星靈王/XingLingWang_v7_fixed"
for root, dirs, files in os.walk(base_dir):
    for f in files:
        if f.endswith('.html'):
            f_path = os.path.join(root, f)
            with open(f_path, 'r', encoding='utf-8', errors='ignore') as file:
                content = file.read()
            if "turn" in content.lower() or "limit" in content.lower():
                print(f"=== {f_path} ===")
                lines = content.split('\n')
                for idx, line in enumerate(lines):
                    if any(term in line.lower() for term in ["turn", "limit", "max", "over"]):
                        print(f"  L{idx+1}: {line.strip()}")
