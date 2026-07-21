import json
import sys
sys.stdout.reconfigure(encoding='utf-8')

with open('data/cards.json', 'r', encoding='utf-8') as f:
    cards = json.load(f)

target_names = ["迴旋飛斧", "賞金", "突擊獸人", "躺平獸人", "雷哥"]

for c in cards:
    if c.get('name') in target_names or any(name in c.get('name', '') for name in target_names):
        print(json.dumps(c, ensure_ascii=False, indent=2))
