import re

with open("c:/Users/a2132/Documents/星靈王/XingLingWang_v7_fixed/app.py", "r", encoding="utf-8") as f:
    lines = f.readlines()

for idx, line in enumerate(lines):
    line_lower = line.lower()
    if "turn" in line_lower and ("10" in line_lower or "limit" in line_lower or "max" in line_lower or "end" in line_lower or "over" in line_lower):
        print(f"L{idx+1}: {line.strip()}")
