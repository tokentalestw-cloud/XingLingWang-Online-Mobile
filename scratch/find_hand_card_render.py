with open("c:/Users/a2132/Documents/星靈王/XingLingWang_v7_fixed/static/game.js", "r", encoding="utf-8") as f:
    content = f.read()

lines = content.split('\n')
for idx, line in enumerate(lines):
    if "hand-card" in line or "selectHand" in line or "selectCard" in line or "click" in line.lower() and "hand" in line.lower():
        if len(line) < 150:
            print(f"L{idx+1}: {line.strip()}")
