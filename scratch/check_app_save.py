with open('app.py', 'r', encoding='utf-8') as f:
    text = f.read()

# Find def save_deck definition
import re
match = re.search(r'def save_deck\(.*?\):.*?(?=def |@app\.)', text, re.DOTALL)
if match:
    print(match.group(0))
else:
    print("def save_deck not found")
