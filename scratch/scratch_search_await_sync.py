import os

base_dir = "c:/Users/a2132/Documents/星靈王/XingLingWang_v7_fixed"

for f_name in ["static/game.js", "static/game_v8.js"]:
    f_path = os.path.join(base_dir, f_name)
    print(f"\n=== Searching in {f_name} ===")
    with open(f_path, "r", encoding="utf-8") as f:
        lines = f.readlines()
        
    # Find ws.onmessage
    for idx, line in enumerate(lines, 1):
        if "ws.onmessage" in line:
            print(f"Line {idx}: {line.strip()}")
            break
            
    # Find functions containing "await performPlayerTurnStartDraw"
    # We will search back for the function keyword to find the enclosing function
    for idx, line in enumerate(lines, 1):
        if "performPlayerTurnStartDraw" in line and "await" in line:
            print(f"Line {idx} has await call: {line.strip()}")
            # Search backward for the enclosing function definition
            enclosing_func = "unknown"
            for j in range(idx - 1, -1, -1):
                if "function " in lines[j] or "=>" in lines[j]:
                    enclosing_func = f"Line {j+1}: {lines[j].strip()}"
                    break
            print(f"  Enclosing function: {enclosing_func}")
