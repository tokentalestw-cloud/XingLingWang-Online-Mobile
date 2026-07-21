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

print("Listing text/csv files in Downloads:")
for f in os.listdir(downloads_dir):
    path = os.path.join(downloads_dir, f)
    if os.path.isfile(path) and f.lower().endswith(('.txt', '.csv', '.json')):
        # Try to print filename safely
        safe_name = f.encode('utf-8', errors='replace').decode('utf-8')
        print(f"\n--- File: {safe_name} ---")
        # Try reading file with different encodings
        for encoding in ['utf-8', 'gbk', 'utf-16', 'big5']:
            try:
                with open(path, 'r', encoding=encoding) as file:
                    content = file.read()
                print(f"Decoded successfully with {encoding}:")
                # print first 500 characters
                print(content[:800])
                break
            except Exception:
                pass
