# -*- coding: utf-8 -*-
import os, sys, re

def fix_lobby_default_hidden():
    sys.stdout.reconfigure(encoding='utf-8')

    base_dir = os.getcwd()
    js_path = os.path.join(base_dir, 'static', 'game_v8.js')
    css_path = os.path.join(base_dir, 'static', 'style_v8.css')
    idx_path = os.path.join(base_dir, 'static', 'index.html')

    # 1. Update static/style_v8.css: Remove display: flex !important from #multiplayerLobby
    css = open(css_path, encoding='utf-8').read()

    old_lobby_css = """/* 全螢幕不透明深色線上對戰大廳浮層 (#multiplayerLobby) */
#multiplayerLobby {
  position: fixed !important;
  top: 0 !important;
  left: 0 !important;
  width: 100vw !important;
  height: 100vh !important;
  background: rgba(8, 6, 16, 0.98) !important;
  z-index: 9999999 !important;
  display: flex !important;
  justify-content: center !important;
  align-items: center !important;
}"""

    new_lobby_css = """/* 全螢幕不透明深色線上對戰大廳浮層 (#multiplayerLobby) */
#multiplayerLobby {
  position: fixed !important;
  top: 0 !important;
  left: 0 !important;
  width: 100vw !important;
  height: 100vh !important;
  background: rgba(8, 6, 16, 0.98) !important;
  z-index: 9999999 !important;
  display: none;
  justify-content: center !important;
  align-items: center !important;
}"""

    css = css.replace(old_lobby_css, new_lobby_css)
    open(css_path, 'w', encoding='utf-8').write(css)
    print("1. Updated style_v8.css #multiplayerLobby default display to none successfully!")

    # 2. Update static/index.html: Update showMultiplayerLobby & hideMultiplayerLobby to use setProperty
    idx = open(idx_path, encoding='utf-8').read()

    # Ensure inline style is display: none !important
    idx = re.sub(
        r'<div id="multiplayerLobby"[^>]*>',
        '<div id="multiplayerLobby" class="score-panel" style="display: none !important; justify-content: center; align-items: center; background: rgba(8,6,16,0.98); z-index: 9999999; position: fixed; top: 0; left: 0; width: 100vw; height: 100vh;">',
        idx
    )

    old_show_lobby_func = """    function showMultiplayerLobby() {
      document.getElementById('multiplayerLobby').style.display = 'flex';
      document.getElementById('lobbyStatusArea').style.display = 'none';
    }
    
    function hideMultiplayerLobby() {
      document.getElementById('multiplayerLobby').style.display = 'none';
    }"""

    new_show_lobby_func = """    function showMultiplayerLobby() {
      const lobby = document.getElementById('multiplayerLobby');
      if (lobby) lobby.style.setProperty("display", "flex", "important");
      const statusArea = document.getElementById('lobbyStatusArea');
      if (statusArea) statusArea.style.display = 'none';
    }
    
    function hideMultiplayerLobby() {
      const lobby = document.getElementById('multiplayerLobby');
      if (lobby) lobby.style.setProperty("display", "none", "important");
    }"""

    idx = idx.replace(old_show_lobby_func, new_show_lobby_func)

    idx = re.sub(r'game_v8\.js\?v=[^"\']+', 'game_v8.js?v=20.80-multiplayer-lobby-hidden-by-default', idx)
    idx = re.sub(r'style_v8\.css\?v=[^"\']+', 'style_v8.css?v=20.80-multiplayer-lobby-hidden-by-default', idx)
    open(idx_path, 'w', encoding='utf-8').write(idx)
    print("2. Updated index.html showMultiplayerLobby & hideMultiplayerLobby functions successfully!")

    # 3. Update static/game_v8.js: Ensure hideMultiplayerLobby() is called on init
    js = open(js_path, encoding='utf-8').read()

    old_init = "function initGameEmptyState() {"
    new_init = "function initGameEmptyState() {\n  if (typeof hideMultiplayerLobby === 'function') hideMultiplayerLobby();"

    js = js.replace(old_init, new_init)

    old_return_title = "window.xlwReturnToTitle = function() {"
    new_return_title = "window.xlwReturnToTitle = function() {\n  if (typeof hideMultiplayerLobby === 'function') hideMultiplayerLobby();"

    js = js.replace(old_return_title, new_return_title)

    open(js_path, 'w', encoding='utf-8').write(js)
    print("3. Updated game_v8.js init & returnToTitle to hide lobby successfully!")

if __name__ == '__main__':
    fix_lobby_default_hidden()
