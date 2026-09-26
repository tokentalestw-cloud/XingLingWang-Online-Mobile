import codecs

def fix_syntax_error():
    with codecs.open('static/game_v8.js', 'r', encoding='utf-8') as f:
        lines = f.readlines()

    start_idx = -1
    for i, line in enumerate(lines):
        if 'const hasEnemySummonPhrase = text.includes(' in line:
            start_idx = i
            break
            
    if start_idx == -1:
        print("Could not find the broken line.")
        return

    # Find the end of the corrupted block
    end_idx = -1
    for i in range(start_idx, start_idx + 50):
        if 'function handleSummon(summoner, zone, index, summonSourceCard = null, fromZone = null, fromIndex = null) {' in lines[i] or 'return hasEnemySummonPhrase;' in lines[i]:
            # This is the next function, so the corruption ends before this.
            end_idx = i
            break

    if end_idx == -1:
        # Fallback if we can't find the end marker. Look for the next closing brace at the root level?
        pass

    # Actually, we know what the correct code is. Let's just find the exact function start and replace the whole function until its closing brace.
    func_start = -1
    for i, line in enumerate(lines):
        if 'function xlwIsEnemySummonCard(c) {' in line:
            func_start = i
            break
            
    if func_start == -1:
        print("Could not find xlwIsEnemySummonCard")
        return
        
    func_end = -1
    for i in range(func_start, func_start + 100):
        # The next function is handleSummon or something else.
        if lines[i].strip() == '};' or lines[i].strip() == '}' or 'function handleSummon' in lines[i] or 'function checkGameOver' in lines[i]:
            if 'function' not in lines[i] or '}' in lines[i-1]:
                # find the closing brace
                for j in range(i, i - 100, -1):
                    if lines[j].strip() == '}':
                        func_end = j
                        break
                break

    if func_end == -1:
        print("Could not find end of xlwIsEnemySummonCard")
        # Just manually replace lines 1472 to 1506
        func_start = 1471
        func_end = 1505

    correct_function = [
        'function xlwIsEnemySummonCard(c) {\\r\\n',
        '  if (!c) return false;\\r\\n',
        '  if (c.id === "ART-0003" || c.id === "R-ART-0003" || c.id === "R-ART-0003-新年" || c.name?.includes("沉思的男人")) return true; \\r\\n',
        '  if (c.id === "CAT-0012" || c.name?.includes("喵玩具") || c.id === "R-CAT-0043" || c.name?.includes("喵喵球") || c.id === "R-VLG-0036" || c.name?.includes("人臉魚") || c.id === "R-VLG-0045" || c.name?.includes("殭屍女") || c.id === "R-VLG-0046" || c.name?.includes("背後靈") || c.id === "R-CAT-0037" || c.name?.includes("喵抓板")) return true;\\r\\n',
        '  const text = c.effect_text || c.effect || "";\\r\\n',
        '  \\r\\n',
        '  // 使用 Unicode 轉義序列以徹底免除 Traditional Chinese (Big5) 瀏覽器解碼混亂\\r\\n',
        '  const hasEnemySummonPhrase = text.includes("\\\\u53ec\\\\u559a") || text.includes("\\\\u7279\\\\u6b8a\\\\u53ec\\\\u559a"); // "召喚" or "特殊召喚"\\r\\n',
        '  return hasEnemySummonPhrase;\\r\\n',
        '}\\r\\n'
    ]

    # Let's verify by just printing lines to replace
    # We will replace from 1472 (index 1471) to where `function handleSummon` starts
    
    start_replace = -1
    end_replace = -1
    for i, line in enumerate(lines):
        if line.startswith('function xlwIsEnemySummonCard(c) {'):
            start_replace = i
        if line.startswith('function handleSummon('):
            end_replace = i
            break
            
    if start_replace != -1 and end_replace != -1:
        new_lines = lines[:start_replace] + correct_function + ['\\r\\n'] + lines[end_replace:]
        with codecs.open('static/game_v8.js', 'w', encoding='utf-8') as f:
            f.writelines(new_lines)
        print(f"Successfully repaired lines {start_replace} to {end_replace}")
    else:
        print("Could not find markers.")

fix_syntax_error()
