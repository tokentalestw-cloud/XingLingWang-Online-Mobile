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
print("Scanning workspace for data files:")
for root, dirs, files in os.walk(base_dir):
    # skip some system/dependency directories
    if ".git" in root or ".gemini" in root or "__pycache__" in root:
        continue
    for f in files:
        if f.endswith(('.txt', '.csv', '.json', '.xlsx')):
            path = os.path.join(root, f)
            print(f"  {os.path.relpath(path, base_dir)} ({os.path.getsize(path)} bytes)")
