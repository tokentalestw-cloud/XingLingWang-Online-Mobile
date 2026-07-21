# -*- coding: utf-8 -*-
import sys

def fix_init():
    sys.stdout.reconfigure(encoding='utf-8')
    js_path = 'static/game_v8.js'
    js_content = open(js_path, encoding='utf-8').read()

    # 1. Update populateLobbyDecksDropdown and populateDeckSelect with null checks
    old_pop1 = 'const presetKeys = Object.keys(decks).filter('
    new_pop1 = 'const presetKeys = Object.keys(decks || {}).filter('
    js_content = js_content.replace(old_pop1, new_pop1)

    old_pop2 = 'const keys = Object.keys(decks).filter('
    new_pop2 = 'const keys = Object.keys(decks || {}).filter('
    js_content = js_content.replace(old_pop2, new_pop2)

    # 2. Update init() function with fallbacks and isolated try-catches
    init_start = "async function init() {"
    init_end = "// 建立線上雙人新局"

    i_start = js_content.find(init_start)
    i_end = js_content.find(init_end)

    if i_start >= 0 and i_end >= 0:
        new_init_code = """async function init() {
  if (window.location.protocol === "file:") {
    showCORSProtocolWarning();
    return;
  }
  try {
    try {
      allCards = await fetch("/api/cards?v=" + Date.now()).then(r => r.json());
    } catch (eCards) {
      console.warn("API cards fetch error, using static fallback:", eCards);
      allCards = await fetch("/static/card_images/cards.json").then(r => r.json()).catch(() => []);
    }

    try {
      decks = await fetch("/api/decks?v=" + Date.now()).then(r => r.json());
    } catch (eDecks) {
      console.warn("API decks fetch error, using static fallback:", eDecks);
      decks = await fetch("/static/decks.json").then(r => r.json()).catch(() => ({}));
    }

    if (!Array.isArray(allCards)) allCards = [];
    if (!decks || typeof decks !== "object") decks = {};

    populateDeckSelect();
    
    // 確保所有卡牌圖片有正確預設值
    allCards.forEach(c => {
      if (!c) return;
      if (!c.image) {
        c.image = "/static/card_back.jpeg";
      }
    });

    try { makeSlots(); } catch (e) { console.warn("makeSlots error:", e); }
    try { setupGlobalEvents(); } catch (e) { console.warn("setupGlobalEvents error:", e); }
    try { setupDebugToggle(); } catch (e) { console.warn("setupDebugToggle error:", e); }
    try {
      adjustBoardScale();
      window.addEventListener("resize", adjustBoardScale);
      window.addEventListener("orientationchange", () => setTimeout(adjustBoardScale, 250));
    } catch (e) {}

    // 解析線上房間參數
    try {
      const urlParams = new URLSearchParams(window.location.search);
      room_id = urlParams.get('room');
      player_id = urlParams.get('player');
      player_role = urlParams.get('role');
      const urlDeck = urlParams.get('deck');

      if (urlDeck) {
        const factionSelect = document.getElementById("factionSelect");
        const deckSelect = document.getElementById("deckSelect");
        const normFac = typeof normDeckName === "function" ? normDeckName(urlDeck) : urlDeck;
        
        if (factionSelect) {
          factionSelect.value = normFac;
          factionSelect.disabled = true;
        }
        
        populateLobbyDecksDropdown();
        
        if (deckSelect) {
          deckSelect.value = urlDeck;
          deckSelect.disabled = true;
        }
      } else {
        const factionSelect = document.getElementById("factionSelect");
        if (factionSelect) {
          factionSelect.addEventListener("change", () => {
            populateLobbyDecksDropdown();
          });
        }
      }

      if (room_id && player_id && player_role) {
        isMultiplayer = true;
        isMyTurn = (player_role === "player1");
        
        const stateRestored = loadLocalGameState();
        const ws_protocol = window.location.protocol === "https:" ? "wss:" : "ws:";
        const ws_url = `${ws_protocol}//${window.location.host}/ws/battle/${room_id}/${player_id}/${player_role}`;
        ws = new WebSocket(ws_url);
        setupWebSocketEvents();
        
        if (stateRestored) {
          render();
        } else {
          initGameEmptyState();
          isMultiplayer = true;
          isMyTurn = (player_role === "player1");
        }
      } else {
        initGameEmptyState();
      }
    } catch (eParams) {
      console.warn("Lobby params resolution warning:", eParams);
      initGameEmptyState();
    }
  } catch (err) {
    console.error("初始化對戰引擎非致命告警:", err);
    try { initGameEmptyState(); } catch (e) {}
  }
}
"""
        js_content = js_content[:i_start] + new_init_code + "\n\n" + js_content[i_end:]
        open(js_path, 'w', encoding='utf-8').write(js_content)
        print("Successfully updated init() and dropdown populate functions in static/game_v8.js!")

if __name__ == '__main__':
    fix_init()
