import os
import sys

# Safe print setup
if sys.stdout.encoding != 'utf-8':
    try:
        import codecs
        sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'replace')
    except Exception:
        pass

downloads_dir = 'C:/Users/a2132/Downloads'
if not os.path.exists(downloads_dir):
    print("Downloads dir not found.")
    sys.exit(0)

print("Listing all files in C:/Users/a2132/Downloads:")
files = []
for entry in os.scandir(downloads_dir):
    if entry.is_file():
        files.append((entry.name, entry.stat().st_size))

# Sort by name
files.sort()
for name, size in files:
    safe_name = name.encode('utf-8', errors='replace').decode('utf-8')
    print(f"  {safe_name} ({size} bytes)")
