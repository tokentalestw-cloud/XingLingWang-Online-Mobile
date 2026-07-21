# -*- coding: utf-8 -*-
import sys

def trace_ai():
    sys.stdout.reconfigure(encoding='utf-8')
    content = open('static/game_v8.js', encoding='utf-8').read()
    
    start_pos = content.find('async function runEnemyTurn()')
    end_pos = content.find('async function endPlayerTurnAndRunEnemy()')
    
    code = content[start_pos:end_pos]
    with open('scratch/run_enemy_turn_full.txt', 'w', encoding='utf-8') as f:
        f.write(code)
    print(f"Saved runEnemyTurn full code ({len(code)} bytes) to scratch/run_enemy_turn_full.txt")

if __name__ == '__main__':
    trace_ai()
