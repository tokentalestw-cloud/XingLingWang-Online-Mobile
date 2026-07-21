# -*- coding: utf-8 -*-
import sys

def fix_lingsao():
    sys.stdout.reconfigure(encoding='utf-8')
    filepath = 'static/game_v8.js'
    content = open(filepath, encoding='utf-8').read()
    if 'R-ORC-0030' not in content:
      content = content.replace('// AI 靈騷獸人', '// AI 靈騷獸人 R-ORC-0030')
      open(filepath, 'w', encoding='utf-8').write(content)
      print("Added R-ORC-0030 comment reference!")

if __name__ == '__main__':
    fix_lingsao()
