# -*- coding: utf-8 -*-
import sys

def check_js_brackets(filepath):
    content = open(filepath, encoding='utf-8').read()
    stack = []
    mapping = {')': '(', '}': '{', ']': '['}
    
    in_string = None
    in_comment = None
    escaped = False
    
    i = 0
    n = len(content)
    while i < n:
        char = content[i]
        
        if in_string and escaped:
            escaped = False
            i += 1
            continue
            
        if in_string and char == '\\':
            escaped = True
            i += 1
            continue
            
        if in_comment == 'line' and char == '\n':
            in_comment = None
            i += 1
            continue
        elif in_comment == 'block' and char == '*' and i + 1 < n and content[i+1] == '/':
            in_comment = None
            i += 2
            continue
            
        if in_comment:
            i += 1
            continue
            
        if in_string:
            if char == in_string:
                in_string = None
            i += 1
            continue
            
        if char == '/' and i + 1 < n and content[i+1] == '/':
            in_comment = 'line'
            i += 2
            continue
        elif char == '/' and i + 1 < n and content[i+1] == '*':
            in_comment = 'block'
            i += 2
            continue
            
        if char in ("'", '"', '`'):
            in_string = char
            i += 1
            continue
            
        if char in '({[':
            stack.append((char, i))
        elif char in ')}]':
            if not stack:
                lines = content[:i].split('\n')
                print(f"Unmatched closing bracket {char} at line {len(lines)}: {lines[-1].strip()}")
                return False
            top, top_idx = stack.pop()
            if top != mapping[char]:
                lines_top = content[:top_idx].split('\n')
                lines_cur = content[:i].split('\n')
                print(f"Mismatched bracket {char} at line {len(lines_cur)} (matched {top} at line {len(lines_top)})")
                print(f"Opening: {lines_top[-1].strip()}")
                print(f"Closing: {lines_cur[-1].strip()}")
                return False
        i += 1
        
    if stack:
        print("Unmatched opening brackets remaining:")
        for top, top_idx in stack[-5:]:
            lines = content[:top_idx].split('\n')
            print(f"  {top} at line {len(lines)}: {lines[-1].strip()}")
        return False
        
    print("JavaScript syntax check: All brackets balanced successfully!")
    return True

if __name__ == '__main__':
    check_js_brackets("static/game_v8.js")
