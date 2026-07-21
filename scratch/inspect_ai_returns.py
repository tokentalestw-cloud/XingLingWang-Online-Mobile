# -*- coding: utf-8 -*-
import sys

def inspect_returns():
    sys.stdout.reconfigure(encoding='utf-8')
    content = open('static/game_v8.js', encoding='utf-8').read()
    
    start_idx = content.find('async function runEnemyTurn()')
    end_idx = content.find('async function endPlayerTurnAndRunEnemy()')
    
    ai_code = content[start_idx:end_idx]
    lines = ai_code.split('\n')
    
    print("All return statements in runEnemyTurn:")
    for i, line in enumerate(lines):
        if 'return' in line:
            print(f"Line {i+1}: {line.strip()}")
            # print surrounding 3 lines
            sub = lines[max(0, i-2):min(len(lines), i+3)]
            for s in sub:
                print("   ", s)
            print("-" * 40)

if __name__ == '__main__':
    inspect_returns()
