# -*- coding: utf-8 -*-
import sys, re

def audit_run_enemy():
    sys.stdout.reconfigure(encoding='utf-8')
    content = open('static/game_v8.js', encoding='utf-8').read()
    
    start_pos = content.find('async function runEnemyTurn()')
    end_pos = content.find('async function endPlayerTurnAndRunEnemy()')
    code = content[start_pos:end_pos]
    
    # Find all function calls inside runEnemyTurn
    func_calls = set(re.findall(r'([a-zA-Z0-9_$]+)\s*\(', code))
    print(f"Total unique function calls in runEnemyTurn: {len(func_calls)}")
    
    missing = []
    for fn in func_calls:
        if fn in ['if', 'for', 'while', 'switch', 'catch', 'function', 'return', 'concat', 'indexOf', 'some', 'filter', 'map', 'forEach', 'findIndex', 'slice', 'splice', 'includes', 'push', 'pop', 'Math', 'Number', 'parseInt', 'parseFloat', 'String', 'JSON', 'Set', 'Array', 'Object', 'structuredClone', 'console', 'logBattle', 'setStatus', 'render', 'sleep']:
            continue
        # Check if function exists in game_v8.js or index.html
        if f'function {fn}' not in content and f'window.{fn}' not in content and f'{fn} =' not in content and f'{fn}:' not in content:
            missing.append(fn)
            
    print("Missing or undefined function calls in runEnemyTurn:", missing)

if __name__ == '__main__':
    audit_run_enemy()
