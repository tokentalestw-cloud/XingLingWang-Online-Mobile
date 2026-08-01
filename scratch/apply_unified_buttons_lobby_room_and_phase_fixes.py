# -*- coding: utf-8 -*-
import os, sys, re

def apply_all_fixes():
    sys.stdout.reconfigure(encoding='utf-8')

    base_dir = os.getcwd()
    js_path = os.path.join(base_dir, 'static', 'game_v8.js')
    css_path = os.path.join(base_dir, 'static', 'style_v8.css')
    idx_path = os.path.join(base_dir, 'static', 'index.html')

    # 1. Update static/index.html
    idx = open(idx_path, encoding='utf-8').read()

    # Unified button classes and shortened text for top-right action bar
    old_action_bar_html = """  <div id="xlwFixedTopRightActionBar" class="xlw-fixed-top-right-action-bar" style="display: none !important;">
    <button id="scoreBtn" class="topbar-setting-btn">📜 紀錄</button>
    <button id="xlwSfxToggleBtn" class="topbar-setting-btn" onclick="window.xlwToggleSFX()">🔊 音效: 開</button>
    <button id="xlwDebugToggleBtn" class="topbar-setting-btn" type="button">Debug：關</button>
    <button id="xlwReturnTitleBtn" class="topbar-action-btn" onclick="window.xlwReturnToTitle()" style="background: linear-gradient(135deg, #3c1e5c 0%, #1c0e2b 100%) !important; border: 2px solid #ffd76a !important; color: #ffe600 !important; font-weight: bold !important; font-size: 12px !important; padding: 4px 10px !important; border-radius: 50px !important; box-shadow: 0 0 10px rgba(255, 215, 106, 0.3) !important; cursor: pointer !important; white-space: nowrap !important;">🏠 首頁</button>
  </div>"""

    new_action_bar_html = """  <div id="xlwFixedTopRightActionBar" class="xlw-fixed-top-right-action-bar" style="display: none !important;">
    <button id="scoreBtn" class="topbar-pill-btn">📜 紀錄</button>
    <button id="xlwSfxToggleBtn" class="topbar-pill-btn" onclick="window.xlwToggleSFX()">🔊 音效: 開</button>
    <button id="xlwReturnTitleBtn" class="topbar-pill-btn" onclick="window.xlwReturnToTitle()">🏠 首頁</button>
  </div>"""

    idx = idx.replace(old_action_bar_html, new_action_bar_html)

    # Add top-right Home button inside multiplayerLobby modal
    old_lobby_card_header = '<div class="score-box" style="width: 420px; padding: 25px;'
    new_lobby_card_header = """<div class="score-box" style="position: relative; width: 440px; padding: 25px;
      <div style="position: absolute; top: 12px; right: 12px; z-index: 10;">
        <button onclick="hideMultiplayerLobby(); if(window.xlwReturnToTitle) window.xlwReturnToTitle();" class="topbar-pill-btn">🏠 首頁</button>
      </div>"""

    idx = idx.replace(old_lobby_card_header, new_lobby_card_header)

    # Update createOnlineRoom & joinOnlineRoom in index.html script to NOT reload page and stay on waiting screen
    old_lobby_scripts = """    function createOnlineRoom() {
      const roomId = Math.floor(1000 + Math.random() * 9000);
      const playerId = 'host_' + Math.floor(Math.random() * 10000);
      const deckSelect = document.getElementById("deckSelect");
      const deckName = deckSelect ? deckSelect.value : "";
      
      document.getElementById('lobbyStatusArea').style.display = 'block';
      document.getElementById('lobbyStatusText').textContent = `正在建立房號為 ${roomId} 的對戰房間，等待對手加入...`;
      
      setTimeout(() => {
        window.location.href = `/?room=${roomId}&player=${playerId}&role=player1&deck=${encodeURIComponent(deckName)}`;
      }, 1000);
    }
    
    function joinOnlineRoom() {
      const input = document.getElementById('lobbyRoomIdInput');
      const roomId = input.value.trim();
      if (!roomId) {
        alert("請輸入有效的房號！");
        return;
      }
      
      const deckSelect = document.getElementById("deckSelect");
      const deckName = deckSelect ? deckSelect.value : "";
      
      const playerId = 'guest_' + Math.floor(Math.random() * 10000);
      document.getElementById('lobbyStatusArea').style.display = 'block';
      document.getElementById('lobbyStatusText').textContent = `正在連接房號為 ${roomId} 的對戰房間，請稍候...`;
      
      setTimeout(() => {
        window.location.href = `/?room=${roomId}&player=${playerId}&role=player2&deck=${encodeURIComponent(deckName)}`;
      }, 1000);
    }"""

    new_lobby_scripts = """    function createOnlineRoom() {
      const roomId = Math.floor(1000 + Math.random() * 9000);
      const playerId = 'host_' + Math.floor(Math.random() * 10000);
      
      const statusArea = document.getElementById('lobbyStatusArea');
      const statusText = document.getElementById('lobbyStatusText');
      if (statusArea) statusArea.style.display = 'block';
      if (statusText) {
        statusText.innerHTML = `
          <div style="font-size: 16px; color: #ffe600; margin-bottom: 6px;">👑 房間建立成功！房號：<span style="font-weight: 900; font-size: 22px; color: #ffffff; letter-spacing: 2px;">${roomId}</span></div>
          <div style="font-size: 13px; color: #ffd76a;">正在等待對手輸入房號加入房間...</div>
          <div style="margin-top: 10px;">
            <button type="button" onclick="navigator.clipboard.writeText('${roomId}'); alert('房號已複製：${roomId}');" class="topbar-pill-btn" style="padding: 4px 12px !important;">📋 複製房號</button>
          </div>
        `;
      }
      
      const actions = document.querySelectorAll('.lobby-action-card');
      actions.forEach(a => a.style.display = 'none');
      
      if (typeof window.xlwStartOnlineHost === 'function') {
        window.xlwStartOnlineHost(roomId, playerId);
      }
    }
    
    function joinOnlineRoom() {
      const input = document.getElementById('lobbyRoomIdInput');
      const roomId = input.value.trim();
      if (!roomId) {
        alert("請輸入有效的房號！");
        return;
      }
      
      const playerId = 'guest_' + Math.floor(Math.random() * 10000);
      const statusArea = document.getElementById('lobbyStatusArea');
      const statusText = document.getElementById('lobbyStatusText');
      if (statusArea) statusArea.style.display = 'block';
      if (statusText) {
        statusText.innerHTML = `<div style="color: #ffd76a; font-size: 14px; font-weight: bold;">正在連接房號為 ${roomId} 的對戰房間，請稍候...</div>`;
      }
      
      if (typeof window.xlwStartOnlineGuest === 'function') {
        window.xlwStartOnlineGuest(roomId, playerId);
      }
    }"""

    idx = idx.replace(old_lobby_scripts, new_lobby_scripts)

    idx = re.sub(r'game_v8\.js\?v=[^"\']+', 'game_v8.js?v=20.90-unified-buttons-and-online-lobby', idx)
    idx = re.sub(r'style_v8\.css\?v=[^"\']+', 'style_v8.css?v=20.90-unified-buttons-and-online-lobby', idx)
    open(idx_path, 'w', encoding='utf-8').write(idx)
    print("1. Updated index.html successfully!")

    # 2. Update static/style_v8.css: Unified topbar-pill-btn & compact shortened phase panel
    css = open(css_path, encoding='utf-8').read()

    # Unified topbar pill button styling
    unified_btn_css = """
/* ===== 統一極致精美按鈕樣式 (.topbar-pill-btn) ===== */
.topbar-pill-btn {
  background: linear-gradient(135deg, rgba(30, 20, 45, 0.9) 0%, rgba(15, 10, 25, 0.95) 100%) !important;
  border: 1px solid rgba(255, 215, 106, 0.45) !important;
  border-radius: 50px !important;
  color: #ffd76a !important;
  font-weight: bold !important;
  font-size: 11px !important;
  padding: 3px 10px !important;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.5) !important;
  cursor: pointer !important;
  white-space: nowrap !important;
  height: 24px !important;
  display: inline-flex !important;
  align-items: center !important;
  justify-content: center !important;
  transition: all 0.2s ease !important;
}
.topbar-pill-btn:hover {
  border-color: #ffd76a !important;
  box-shadow: 0 0 10px rgba(255, 215, 106, 0.4) !important;
  transform: scale(1.05) !important;
}
"""
    css += unified_btn_css

    # Update phaseDisplayPanelHard in CSS: left: 205px (225px - 20px), width: 600px, compact fonts (12px / 9.5px)
    old_phase_css = """  #phaseDisplayPanelHard {
    position: absolute !important;
    top: 0px !important;
    left: 225px !important;
    width: 960px !important;
    transform: scale(0.62) !important;
    transform-origin: top left !important;
    z-index: 999999 !important;
    display: none;
    flex-direction: column !important;
    align-items: center !important;
  }
  .phase-hard-title { font-size: 19px !important; font-weight: 900 !important; color: #ffd76a !important; text-shadow: 0 0 10px rgba(255, 215, 106, 0.5) !important; line-height: 1.1 !important; }
  .phase-hard-help { font-size: 12px !important; color: #ffe6a0 !important; line-height: 1.1 !important; margin-top: 1px !important; }"""

    new_phase_css = """  #phaseDisplayPanelHard {
    position: absolute !important;
    top: 0px !important;
    left: 205px !important;
    width: 600px !important;
    transform: scale(0.50) !important;
    transform-origin: top left !important;
    z-index: 999999 !important;
    display: none;
    flex-direction: column !important;
    align-items: center !important;
    padding: 2px 10px !important;
  }
  .phase-hard-title { font-size: 12px !important; font-weight: bold !important; color: #ffd76a !important; line-height: 1.0 !important; margin: 0 !important; }
  .phase-hard-help { font-size: 9.5px !important; color: #ffe6a0 !important; line-height: 1.0 !important; margin: 0 !important; }"""

    css = css.replace(old_phase_css, new_phase_css)

    open(css_path, 'w', encoding='utf-8').write(css)
    print("2. Updated style_v8.css successfully!")

    # 3. Update static/game_v8.js: Define window.xlwStartOnlineHost & window.xlwStartOnlineGuest
    js = open(js_path, encoding='utf-8').read()

    online_helpers = """
window.xlwStartOnlineHost = function(roomId, playerId) {
  const deckSelect = document.getElementById("deckSelect");
  const deckName = deckSelect ? deckSelect.value : "";
  isMultiplayer = true;
  isMyTurn = true;
  room_id = roomId;
  player_id = playerId;
  player_role = "player1";
  
  const ws_protocol = window.location.protocol === "https:" ? "wss:" : "ws:";
  const ws_url = `${ws_protocol}//${window.location.host}/ws/battle/${roomId}/${playerId}/player1`;
  if (ws) { try { ws.close(); } catch(e){} }
  ws = new WebSocket(ws_url);
  setupWebSocketEvents();
  console.log("Online Room created & WebSocket connected for Host:", roomId);
};

window.xlwStartOnlineGuest = function(roomId, playerId) {
  const deckSelect = document.getElementById("deckSelect");
  const deckName = deckSelect ? deckSelect.value : "";
  isMultiplayer = true;
  isMyTurn = false;
  room_id = roomId;
  player_id = playerId;
  player_role = "player2";
  
  const ws_protocol = window.location.protocol === "https:" ? "wss:" : "ws:";
  const ws_url = `${ws_protocol}//${window.location.host}/ws/battle/${roomId}/${playerId}/player2`;
  if (ws) { try { ws.close(); } catch(e){} }
  ws = new WebSocket(ws_url);
  setupWebSocketEvents();
  console.log("Online Room joined & WebSocket connected for Guest:", roomId);
};
"""
    js += online_helpers
    open(js_path, 'w', encoding='utf-8').write(js)
    print("3. Updated game_v8.js successfully!")

if __name__ == '__main__':
    apply_all_fixes()
