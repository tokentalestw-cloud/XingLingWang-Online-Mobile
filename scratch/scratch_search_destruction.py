import os

base_dir = "c:/Users/a2132/Documents/星靈王/XingLingWang_v7_fixed"
game_js_path = os.path.join(base_dir, "static/game_v8.js")

with open(game_js_path, "r", encoding="utf-8") as f:
    lines = f.readlines()

print("=== Search for destruction/graveyard pushes ===")
for idx, line in enumerate(lines, 1):
    if "grave.push" in line or "graveyard.push" in line or "destroy" in line.lower():
        if "logBattle" in line or "console.log" in line:
            continue
        print(f"Line {idx}: {line.strip()[:120]}")
