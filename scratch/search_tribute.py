import re

filepath = r"c:\Users\a2132\Documents\星靈王\XingLingWang_v7_fixed\static\game_v8.js"
with open(filepath, 'r', encoding='utf-8') as f:
    lines = f.readlines()

keywords = ["confirmTribute", "executeTributeEffects", "tribute", "晴天娃娃"]
for i, line in enumerate(lines):
    for kw in keywords:
        if kw in line:
            print(f"Line {i+1}: {line.strip()[:100]}")
            break
