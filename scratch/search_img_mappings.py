import os
import sys

# Safe print setup
if sys.stdout.encoding != 'utf-8':
    try:
        import codecs
        sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'replace')
    except Exception:
        pass

base_dir = 'c:/Users/a2132/Documents/星靈王/XingLingWang_v7_fixed'
for root, dirs, files in os.walk(base_dir):
    if ".git" in root or ".gemini" in root or "__pycache__" in root:
        continue
    for f in files:
        if f.endswith(('.js', '.py', '.json', '.txt', '.html')):
            path = os.path.join(root, f)
            try:
                with open(path, 'r', encoding='utf-8', errors='ignore') as file:
                    content = file.read()
                if "IMG_61" in content:
                    print(f"Found IMG_61 in {os.path.relpath(path, base_dir)}")
                    # print matching lines
                    lines = content.split('\n')
                    for idx, line in enumerate(lines):
                        if "IMG_61" in line:
                            print(f"  L{idx+1}: {line.strip()}")
            except Exception:
                pass
