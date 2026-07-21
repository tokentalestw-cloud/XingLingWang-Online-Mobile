import os

base_dir = "c:/Users/a2132/Documents/星靈王/XingLingWang_v7_fixed"

for f_name in ["static/game.js", "static/game_v8.js"]:
    f_path = os.path.join(base_dir, f_name)
    if not os.path.exists(f_path):
        continue
    print(f"Checking syntax for {f_name}...")
    with open(f_path, "r", encoding="utf-8") as f:
        content = f.read()
    
    # Clean string literals and comments to avoid counting characters inside comments/strings
    # This is a basic minifier-like cleaner
    clean_chars = []
    in_string = False
    string_char = None
    in_single_comment = False
    in_multi_comment = False
    
    i = 0
    while i < len(content):
        c = content[i]
        
        # Check comments
        if in_single_comment:
            if c == '\n':
                in_single_comment = False
            i += 1
            continue
        if in_multi_comment:
            if c == '*' and i + 1 < len(content) and content[i+1] == '/':
                in_multi_comment = False
                i += 2
            else:
                i += 1
            continue
        
        # Check strings
        if in_string:
            if c == '\\':
                # Skip escaped character
                i += 2
                continue
            if c == string_char:
                in_string = False
            i += 1
            continue
            
        # Check start of comment
        if c == '/' and i + 1 < len(content):
            if content[i+1] == '/':
                in_single_comment = True
                i += 2
                continue
            elif content[i+1] == '*':
                in_multi_comment = True
                i += 2
                continue
                
        # Check start of string
        if c in ['"', "'", '`']:
            in_string = True
            string_char = c
            i += 1
            continue
            
        # Add normal characters
        clean_chars.append(c)
        i += 1
        
    clean_content = "".join(clean_chars)
    
    counts = {
        '{': clean_content.count('{'),
        '}': clean_content.count('}'),
        '(': clean_content.count('('),
        ')': clean_content.count(')'),
        '[': clean_content.count('['),
        ']': clean_content.count(']')
    }
    
    print(f"  Curly brackets {{ }}: {counts['{']} open, {counts['}']} close")
    print(f"  Parentheses ( ): {counts['(']} open, {counts[')']} close")
    print(f"  Square brackets [ ]: {counts['[']} open, {counts[']']} close")
    
    ok = True
    if counts['{'] != counts['}']:
        print("  [ERROR] Unbalanced curly brackets!")
        ok = False
    if counts['('] != counts[')']:
        print("  [ERROR] Unbalanced parentheses!")
        ok = False
    if counts['['] != counts[']']:
        print("  [ERROR] Unbalanced square brackets!")
        ok = False
        
    if ok:
        print("  [OK] Syntax is balanced.")
