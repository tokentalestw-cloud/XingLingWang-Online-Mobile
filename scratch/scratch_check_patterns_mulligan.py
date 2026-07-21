import os

base_dir = "c:/Users/a2132/Documents/星靈王/XingLingWang_v7_fixed"

patterns = {
    "confirmMulligan_def": "function confirmMulligan() {",
    "checkMulliganCompletion_def": "function checkMulliganCompletion() {",
    "checkMulliganCompletion_call1": "    checkMulliganCompletion();\n  } else {",
    "checkMulliganCompletion_call2": "    opponent_mulligan_done = true;\n    checkMulliganCompletion();"
}

for f_name in ["static/game.js", "static/game_v8.js"]:
    f_path = os.path.join(base_dir, f_name)
    print(f"\nChecking patterns in {f_name}...")
    with open(f_path, "r", encoding="utf-8") as f:
        content = f.read()
    
    for p_name, p_val in patterns.items():
        p_val_lf = p_val.replace("\r\n", "\n")
        content_lf = content.replace("\r\n", "\n")
        count = content_lf.count(p_val_lf)
        print(f"  {p_name}: {count} occurrences")
