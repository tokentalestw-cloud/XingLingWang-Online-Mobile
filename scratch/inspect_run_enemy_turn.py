# -*- coding: utf-8 -*-
import sys

def inspect_run_enemy():
    sys.stdout.reconfigure(encoding='utf-8')
    content = open('static/game_v8.js', encoding='utf-8').read()
    
    start_pos = content.find('async function runEnemyTurn()')
    end_pos = content.find('async function endPlayerTurnAndRunEnemy()')
    
    fn_code = content[start_pos:end_pos]
    lines = fn_code.split('\n')
    
    for i, line in enumerate(lines):
        print(f"{i+1:4d}: {line}")

if __name__ == '__main__':
    inspect_run_enemy()
