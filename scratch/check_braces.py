# -*- coding: utf-8 -*-
import sys

def main():
    try:
        code = open('static/game_v8.js', encoding='utf-8').read()
    except Exception as e:
        print(f"Error reading file: {e}")
        return

    stack = []
    line = 1
    col = 0
    in_string = None
    in_comment = None
    escaped = False

    i = 0
    n = len(code)
    while i < n:
        char = code[i]
        col += 1
        if char == '\n':
            line += 1
            col = 0

        if escaped:
            escaped = False
            i += 1
            continue

        if in_comment == 'single':
            if char == '\n':
                in_comment = None
            i += 1
            continue
        elif in_comment == 'multi':
            if char == '/' and i > 0 and code[i-1] == '*':
                in_comment = None
            i += 1
            continue

        if in_string:
            if char == '\\':
                escaped = True
            elif char == in_string:
                in_string = None
            i += 1
            continue

        # Check for string starters
        if char in ('"', "'", '`'):
            in_string = char
            i += 1
            continue

        # Check for comments
        if char == '/' and i + 1 < n:
            next_char = code[i+1]
            if next_char == '/':
                in_comment = 'single'
                i += 2
                col += 1
                continue
            elif next_char == '*':
                in_comment = 'multi'
                i += 2
                col += 1
                continue

        if char in ('(', '{', '['):
            stack.append((char, line, col))
        elif char in (')', '}', ']'):
            if not stack:
                print(f"Mismatched closing {char} at line {line}, col {col}")
                return
            prev, pl, pc = stack.pop()
            if (char == ')' and prev != '(') or (char == '}' and prev != '{') or (char == ']' and prev != '['):
                print(f"Mismatched closing {char} at line {line}, col {col}. Opened {prev} at line {pl}, col {pc}")
                return

        i += 1

    if stack:
        print("Unclosed brackets at end of file:")
        for item in stack[-20:]:
            print(f"  {item[0]} opened at line {item[1]}, col {item[2]}")
    else:
        print("Brackets are perfectly balanced!")

if __name__ == '__main__':
    main()
