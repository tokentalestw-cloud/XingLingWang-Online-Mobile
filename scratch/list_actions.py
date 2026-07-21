import re

def list_actions(filepath):
    print(f"=== ACTIONS IN {filepath} ===")
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Matches action: "some_action"
    pattern = re.compile(r'action:\s*["\']([^"\']+)["\']')
    actions = sorted(list(set(pattern.findall(content))))
    for a in actions:
        print(f"  - {a}")

list_actions("c:/Users/a2132/Documents/星靈王/XingLingWang_v7_fixed/static/game.js")
list_actions("c:/Users/a2132/Documents/星靈王/XingLingWang_v7_fixed/static/game_v8.js")
