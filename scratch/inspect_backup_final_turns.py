import sys

# Safe print setup
if sys.stdout.encoding != 'utf-8':
    try:
        import codecs
        sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'replace')
    except Exception:
        pass

with open("c:/Users/a2132/Documents/星靈王/XingLingWang_v7_fixed/backup/game.js", "r", encoding="utf-8") as f:
    lines = f.readlines()

targets = [5528, 5531, 5749, 6274, 7075, 7085, 7577, 7589, 8121, 8136, 8762, 8777, 9318, 9333]
for t in targets:
    print(f"=== Backup Line {t} ===")
    for idx in range(max(0, t - 3), min(len(lines), t + 3)):
        print(f"  {idx+1}: {lines[idx].rstrip()}")
    print("-" * 50)
