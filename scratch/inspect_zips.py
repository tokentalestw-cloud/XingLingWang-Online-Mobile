import os
import zipfile
import sys

# Safe print setup
if sys.stdout.encoding != 'utf-8':
    try:
        import codecs
        sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'replace')
    except Exception:
        pass

downloads_dir = 'C:/Users/a2132/Downloads'

def inspect_zip(filename):
    path = os.path.join(downloads_dir, filename)
    if not os.path.exists(path):
        print(f"File not found: {filename}")
        return
    print(f"\n=== Inspecting {filename} ===")
    try:
        with zipfile.ZipFile(path, 'r') as z:
            names = z.namelist()
            print(f"Total files in zip: {len(names)}")
            # Search for cards.json or decks.json or files named like card list
            matching = [name for name in names if "cards.json" in name or "decks.json" in name or name.endswith('.json') or "data/" in name]
            print(f"Matching data files in zip ({len(matching)}):")
            for m in matching[:20]:
                print(f"  {m}")
            if len(matching) > 20:
                print("  ...")
    except Exception as e:
        print("Error reading zip:", e)

inspect_zip("星靈王_藝術品修正完成版_v4.zip")
inspect_zip("星靈王_v6_藝術品完整修正版_FINAL.zip")
inspect_zip("星靈王_藝術品修正版_v5_原架構可用.zip")
