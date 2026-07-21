# -*- coding: utf-8 -*-
import sys

def add_set_status():
    sys.stdout.reconfigure(encoding='utf-8')
    js_path = 'static/game_v8.js'
    js_content = open(js_path, encoding='utf-8').read()

    if 'function setStatus' not in js_content:
        target_str = 'function logBattle(text) {'
        new_code = """function setStatus(t) {
  const s = $("status");
  if (s) s.textContent = t;
}

function logBattle(text) {"""
        js_content = js_content.replace(target_str, new_code)
        open(js_path, 'w', encoding='utf-8').write(js_content)
        print("Successfully restored function setStatus(t) in static/game_v8.js!")
    else:
        print("function setStatus already exists.")

if __name__ == '__main__':
    add_set_status()
