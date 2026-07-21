import os

base_dir = "c:/Users/a2132/Documents/星靈王/XingLingWang_v7_fixed"
game_js_path = os.path.join(base_dir, "static/game_v8.js")

with open(game_js_path, "r", encoding="utf-8") as f:
    lines = f.readlines()

print("=== Searching for Prajna/Hannya cemetery pushes ===")
for idx, line in enumerate(lines, 1):
    if "grave" in line or "graveyard" in line:
        # Check context
        start = max(0, idx - 4)
        end = min(len(lines), idx + 3)
        context = "".join(lines[start:end])
        if any(x in context for x in ["般若", "Prajna", "hannya"]):
            print(f"Line {idx}: {line.strip()}")
