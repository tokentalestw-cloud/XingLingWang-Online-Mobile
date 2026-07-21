with open("static/game.js", "r", encoding="utf-8") as f:
    content = f.read()

idx = content.find("function belongsToDeck")
if idx != -1:
    print(content[idx:idx+1200].encode('ascii', errors='replace').decode('ascii'))
else:
    print("belongsToDeck not found")
