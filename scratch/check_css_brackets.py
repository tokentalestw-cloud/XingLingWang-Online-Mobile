# -*- coding: utf-8 -*-
import sys

def check_css():
    sys.stdout.reconfigure(encoding='utf-8')
    content = open('static/style_v8.css', encoding='utf-8').read()
    
    stack = []
    lines = content.split('\n')
    errors = []
    
    for i, line in enumerate(lines):
        for col, char in enumerate(line):
            if char == '{':
                stack.append((i+1, col+1, '{'))
            elif char == '}':
                if not stack:
                    errors.append(f"Unexpected closing brace '}}' at line {i+1}, col {col+1}")
                else:
                    stack.pop()
                    
    if stack:
        for line_no, col, char in stack:
            print(f"Unclosed opening brace '{{' at line {line_no}, col {col}")
    
    for err in errors:
        print(err)
        
    if not stack and not errors:
        print("CSS brackets are 100% balanced and syntactically clean!")

if __name__ == '__main__':
    check_css()
