import os
import sys

# Safe print setup
if sys.stdout.encoding != 'utf-8':
    try:
        import codecs
        sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'replace')
    except Exception:
        pass

base_dir = 'C:/Users/a2132/Downloads/星靈王圖片'
if not os.path.exists(base_dir):
    print(f"Directory {base_dir} does not exist.")
    sys.exit(0)

print(f"Subdirectories in {base_dir}:")
for entry in os.scandir(base_dir):
    if entry.is_dir():
        # count files in it
        files = os.listdir(entry.path)
        print(f"  {entry.name}: {len(files)} files")
        if files:
            print(f"    First 5 files: {files[:5]}")
