with open('static/game_v8.js', 'r', encoding='utf-8') as f:
    lines = f.readlines()

def get_function_name_above(line_idx):
    for i in range(line_idx, -1, -1):
        if 'function ' in lines[i]:
            return i + 1, lines[i].strip()
    return None

targets = [14213, 14452, 20385, 22090]
for t in targets:
    ctx = get_function_name_above(t)
    if ctx:
        print(f"Target line {t} is under line {ctx[0]}: {ctx[1]}")
    else:
        print(f"Target line {t} has no function above it")
