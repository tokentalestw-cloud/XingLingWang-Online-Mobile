import os

search_terms = ["般若", "Prajna", "hannya"]
files_to_search = [
    "app.py",
    "static/game.js",
    "static/game_v8.js",
    "static/decks.json",
    "scratch_cards.json"
]

base_dir = "c:/Users/a2132/Documents/星靈王/XingLingWang_v7_fixed"

for f_name in files_to_search:
    f_path = os.path.join(base_dir, f_name)
    if not os.path.exists(f_path):
        print(f"File not found: {f_path}")
        continue
    print(f"\n=== Searching in {f_name} ===")
    try:
        with open(f_path, "r", encoding="utf-8") as f:
            for line_no, line in enumerate(f, 1):
                for term in search_terms:
                    if term in line:
                        print(f"Line {line_no} ({term}): {line.strip()[:150]}")
                        break
    except Exception as e:
        print(f"Error reading {f_name}: {e}")
