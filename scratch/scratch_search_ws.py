import os

base_dir = "c:/Users/a2132/Documents/星靈王/XingLingWang_v7_fixed"
game_js_path = os.path.join(base_dir, "static/game_v8.js")

with open(game_js_path, "r", encoding="utf-8") as f:
    lines = f.readlines()

print("=== WebSocket sends ===")
for idx, line in enumerate(lines, 1):
    if "ws.send" in line:
        print(f"Line {idx}: {line.strip()[:120]}")

print("\n=== WebSocket onmessage action handlers ===")
inside_onmessage = False
for idx, line in enumerate(lines, 1):
    if "ws.onmessage" in line:
        inside_onmessage = True
        print(f"Line {idx}: onmessage starts")
    if inside_onmessage:
        if "action ===" in line or 'action ===' in line or "data.action ===" in line or "case " in line:
            print(f"Line {idx}: {line.strip()[:120]}")
        if "};" in line and inside_onmessage and idx > 6400: # heuristic to print when it ends
            # We can search for the end of onmessage if we want, but let's just print matching lines.
            pass
