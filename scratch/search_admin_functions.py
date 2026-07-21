with open("c:/Users/a2132/Documents/星靈王/XingLingWang_v7_fixed/static/admin.html", "r", encoding="utf-8") as f:
    content = f.read()

lines = content.split('\n')
for idx, line in enumerate(lines):
    if "function " in line or "fetch(" in line or "upload" in line.lower() or "import" in line.lower() or "辨識" in line:
        if len(line) < 150:
            print(f"L{idx+1}: {line.strip()}")
