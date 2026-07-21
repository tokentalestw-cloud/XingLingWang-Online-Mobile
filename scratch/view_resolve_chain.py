with open(r"c:\Users\a2132\Documents\星靈王\XingLingWang_v7_fixed\static\game_v8.js", 'r', encoding='utf-8') as f:
    lines = f.readlines()

start_line = 0
for idx, line in enumerate(lines):
    if "function resolveLocalSpellChain" in line or "async function resolveLocalSpellChain" in line:
        start_line = idx
        break

if start_line > 0:
    with open(r"c:\Users\a2132\Documents\星靈王\XingLingWang_v7_fixed\scratch\resolveSpellChain_dump.txt", "w", encoding="utf-8") as out:
        for i in range(start_line, start_line + 150):
            if i < len(lines):
                out.write(f"{i+1}: {lines[i]}")
else:
    print("resolveLocalSpellChain not found")
