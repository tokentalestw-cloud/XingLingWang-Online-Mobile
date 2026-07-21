import os

workspace_dir = "c:/Users/a2132/Documents/星靈王/XingLingWang_v7_fixed"
html_files = []
for root, dirs, files in os.walk(workspace_dir):
    for f in files:
        if f.endswith(".html"):
            html_files.append(os.path.join(root, f))

for path in html_files:
    with open(path, 'r', encoding='utf-8') as file:
        content = file.read()
    if "game.js" in content:
        print(f"game.js found in: {os.path.basename(path)}")
    if "game_v8.js" in content:
        print(f"game_v8.js found in: {os.path.basename(path)}")
