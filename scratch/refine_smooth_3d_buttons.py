# -*- coding: utf-8 -*-
import sys, re

def refine_buttons():
    sys.stdout.reconfigure(encoding='utf-8')
    css_path = 'static/style_v8.css'
    css_content = open(css_path, encoding='utf-8').read()

    # Clean previous 3D theme blocks at bottom of file if exists
    block_marker = "/* ==========================================================================\n   ULTRA-GLOSSY 3D TACTILE UI THEME"
    if block_marker in css_content:
        css_content = css_content[:css_content.find(block_marker)]

    smooth_3d_css = """/* ==========================================================================
   SLEEK & SMOOTH ULTRA-GLOSSY 3D TACTILE UI THEME
   (徹底去除銳利粗糙邊框，打造圓潤平滑、奢華立體之高級介面)
   ========================================================================== */

/* 1. 全域按鈕圓角與平滑過渡 */
button, select, .forest-summon-btn, .modal-content button, .xlw-modal button, .topbar button {
  border-radius: 14px !important;
  font-family: inherit !important;
  box-sizing: border-box !important;
  transition: all 0.2s cubic-bezier(0.16, 1, 0.3, 1) !important;
}

/* 2. 頂欄按鈕 (.topbar button) 圓潤光滑立體感 */
.topbar button, .topbar select, .topbar a button {
  border: 1.5px solid rgba(255, 230, 100, 0.75) !important;
  border-radius: 14px !important;
  letter-spacing: 0.5px !important;
  padding: 8px 18px !important;
  background: linear-gradient(180deg, rgba(255, 255, 255, 0.35) 0%, rgba(255, 255, 255, 0) 45%), linear-gradient(180deg, #fff480 0%, #ffd700 50%, #d69e00 100%) !important;
  color: #000000 !important;
  box-shadow: inset 0 2px 3px rgba(255, 255, 255, 0.65), inset 0 -3px 6px rgba(0, 0, 0, 0.3), 0 6px 18px rgba(0, 0, 0, 0.6), 0 0 12px rgba(255, 215, 0, 0.35) !important;
  text-shadow: 0 1px 0 rgba(255, 255, 255, 0.5) !important;
  font-weight: 800 !important;
}

.topbar button:hover:not(:disabled), .topbar select:hover, .topbar a button:hover {
  transform: translateY(-2.5px) !important;
  border-color: rgba(255, 255, 255, 0.95) !important;
  background: linear-gradient(180deg, rgba(255, 255, 255, 0.5) 0%, rgba(255, 255, 255, 0) 45%), linear-gradient(180deg, #ffffb3 0%, #ffe033 50%, #e6aa00 100%) !important;
  box-shadow: inset 0 2.5px 4px rgba(255, 255, 255, 0.85), inset 0 -3px 6px rgba(0, 0, 0, 0.3), 0 10px 24px rgba(0, 0, 0, 0.75), 0 0 20px rgba(255, 230, 0, 0.65) !important;
}

.topbar button:active:not(:disabled), .topbar select:active, .topbar a button:active {
  transform: translateY(2px) !important;
  box-shadow: inset 0 3px 6px rgba(0, 0, 0, 0.4), 0 2px 6px rgba(0, 0, 0, 0.5) !important;
}

/* 3. 單人/雙人對決按鈕光滑漸層 */
#newGameBtn {
  background: linear-gradient(180deg, rgba(255,255,255,0.3) 0%, rgba(255,255,255,0) 45%), linear-gradient(180deg, #fff7a0 0%, #ffd700 50%, #c99c00 100%) !important;
  border: 1.5px solid rgba(255, 235, 120, 0.85) !important;
  border-radius: 14px !important;
}

#multiplayerBtn {
  background: linear-gradient(180deg, rgba(255,255,255,0.35) 0%, rgba(255,255,255,0) 45%), linear-gradient(180deg, #ff6b8b 0%, #ff1f4c 50%, #b80024 100%) !important;
  border: 1.5px solid rgba(255, 180, 200, 0.85) !important;
  border-radius: 14px !important;
  color: #ffffff !important;
  text-shadow: 1px 1px 2px #000 !important;
  box-shadow: inset 0 2px 3px rgba(255, 255, 255, 0.6), inset 0 -3px 6px rgba(0, 0, 0, 0.35), 0 6px 18px rgba(0, 0, 0, 0.6), 0 0 14px rgba(255, 31, 76, 0.4) !important;
}

/* 4. 中央狀態提示欄 (#status) 圓潤玻璃質感 */
#status, .status-bar, .xlw-status-box {
  background: linear-gradient(180deg, rgba(32, 24, 44, 0.95) 0%, rgba(16, 12, 24, 0.97) 100%) !important;
  border: 1.5px solid rgba(255, 230, 100, 0.65) !important;
  border-radius: 16px !important;
  color: #fff6c2 !important;
  font-weight: 900 !important;
  letter-spacing: 0.6px !important;
  text-shadow: 1px 1px 2px rgba(0, 0, 0, 0.9), 0 0 8px rgba(255, 230, 0, 0.4) !important;
  box-shadow: inset 0 2px 4px rgba(255, 255, 255, 0.35), inset 0 -3px 8px rgba(0, 0, 0, 0.5), 0 8px 25px rgba(0, 0, 0, 0.85), 0 0 18px rgba(255, 230, 0, 0.2) !important;
  padding: 10px 20px !important;
  backdrop-filter: blur(14px) !important;
}

/* 5. 結束回合按鈕 (#endTurnBtn) 圓潤奢華立體 */
#endTurnBtn, .end-turn-btn {
  background: linear-gradient(180deg, rgba(255,255,255,0.35) 0%, rgba(255,255,255,0) 45%), linear-gradient(180deg, #ff7a7a 0%, #e61919 50%, #8c0000 100%) !important;
  color: #ffffff !important;
  border: 1.5px solid rgba(255, 200, 200, 0.8) !important;
  border-radius: 14px !important;
  font-weight: 900 !important;
  font-size: 15px !important;
  text-shadow: 1.5px 1.5px 2px #000000 !important;
  box-shadow: inset 0 2px 3px rgba(255, 255, 255, 0.6), inset 0 -3px 6px rgba(0, 0, 0, 0.4), 0 8px 22px rgba(0, 0, 0, 0.7), 0 0 16px rgba(230, 25, 25, 0.45) !important;
  cursor: pointer !important;
}

#endTurnBtn:hover:not(:disabled), .end-turn-btn:hover:not(:disabled) {
  transform: translateY(-2.5px) !important;
  border-color: #ffffff !important;
  background: linear-gradient(180deg, rgba(255,255,255,0.45) 0%, rgba(255,255,255,0) 45%), linear-gradient(180deg, #ff9494 0%, #ff2e2e 50%, #a80000 100%) !important;
  box-shadow: inset 0 2.5px 4px rgba(255, 255, 255, 0.8), inset 0 -3px 6px rgba(0, 0, 0, 0.4), 0 12px 28px rgba(0, 0, 0, 0.8), 0 0 22px rgba(255, 31, 76, 0.65) !important;
}

#endTurnBtn:active:not(:disabled), .end-turn-btn:active:not(:disabled) {
  transform: translateY(2px) !important;
  box-shadow: inset 0 3px 6px rgba(0, 0, 0, 0.6) !important;
}

/* 6. 雙方總分計分板 (.score-box) 圓潤光滑邊框 */
.score-box, #scoreBoard, #scorePanel .score-card, #enemyScore, #playerScore {
  background: linear-gradient(180deg, rgba(30, 22, 40, 0.95) 0%, rgba(14, 10, 20, 0.97) 100%) !important;
  border: 1.5px solid rgba(255, 230, 100, 0.65) !important;
  border-radius: 16px !important;
  color: #ffffff !important;
  font-weight: 900 !important;
  box-shadow: inset 0 2px 3px rgba(255, 255, 255, 0.4), inset 0 -3px 6px rgba(0, 0, 0, 0.4), 0 8px 25px rgba(0, 0, 0, 0.85), 0 0 16px rgba(255, 230, 0, 0.25) !important;
  text-shadow: 1px 1px 2px #000 !important;
}

.score-box:hover, #enemyScore:hover, #playerScore:hover {
  transform: translateY(-2px) !important;
  box-shadow: inset 0 2.5px 4px rgba(255, 255, 255, 0.6), inset 0 -3px 6px rgba(0, 0, 0, 0.4), 0 12px 30px rgba(0, 0, 0, 0.9), 0 0 22px rgba(255, 230, 0, 0.45) !important;
}

.score-val, #enemyScoreVal, #playerScoreVal {
  color: #ffe600 !important;
  font-weight: 900 !important;
  text-shadow: 0 0 12px rgba(255, 230, 0, 0.8), 1.5px 1.5px 0 #000 !important;
}

/* 7. 對手狀態欄位 (#xlwEnemyInfoPanel) 圓潤外框 */
#xlwEnemyInfoPanel, .xlw-enemy-info-panel {
  background: linear-gradient(180deg, rgba(38, 18, 28, 0.95) 0%, rgba(18, 8, 14, 0.97) 100%) !important;
  border: 1.5px solid rgba(255, 100, 100, 0.65) !important;
  border-radius: 16px !important;
  color: #fff0f2 !important;
  padding: 12px 16px !important;
  font-weight: 800 !important;
  box-shadow: inset 0 2px 3px rgba(255, 255, 255, 0.35), inset 0 -3px 6px rgba(0, 0, 0, 0.4), 0 8px 25px rgba(0, 0, 0, 0.9), 0 0 18px rgba(255, 77, 79, 0.3) !important;
  backdrop-filter: blur(14px) !important;
}

#xlwEnemyInfoPanel .enemy-info-title {
  color: #ff7875 !important;
  font-size: 15px !important;
  font-weight: 900 !important;
  text-shadow: 0 0 8px rgba(255, 77, 79, 0.6), 1.5px 1.5px 0 #000 !important;
  margin-bottom: 6px !important;
}

#xlwEnemyInfoPanel span {
  color: #ffe600 !important;
  font-weight: 900 !important;
  text-shadow: 1px 1px 0 #000 !important;
}

/* 8. 右下主操作面板與按鈕 (#stableActionPanel) */
#stableActionPanel {
  background: linear-gradient(180deg, rgba(22, 16, 30, 0.96) 0%, rgba(12, 8, 18, 0.98) 100%) !important;
  border: 1.5px solid rgba(255, 230, 100, 0.65) !important;
  border-radius: 18px !important;
  padding: 14px !important;
  box-shadow: inset 0 2px 4px rgba(255, 255, 255, 0.35), inset 0 -3px 8px rgba(0, 0, 0, 0.5), 0 10px 30px rgba(0, 0, 0, 0.92), 0 0 20px rgba(255, 230, 0, 0.25) !important;
  backdrop-filter: blur(14px) !important;
}

/* 戰術佈陣按鈕 (戰術水晶藍紫) */
#stableActionTactical, .stable-action-btn.tactical {
  background: linear-gradient(180deg, rgba(255,255,255,0.35) 0%, rgba(255,255,255,0) 45%), linear-gradient(180deg, #ca9eff 0%, #9254de 45%, #531dab 100%) !important;
  color: #ffffff !important;
  border: 1.5px solid rgba(220, 180, 255, 0.8) !important;
  border-radius: 14px !important;
  font-weight: 900 !important;
  font-size: 14px !important;
  text-shadow: 1.5px 1.5px 0 #000000 !important;
  box-shadow: inset 0 2px 3px rgba(255, 255, 255, 0.6), inset 0 -3px 6px rgba(0, 0, 0, 0.4), 0 6px 18px rgba(0, 0, 0, 0.7), 0 0 14px rgba(146, 84, 222, 0.4) !important;
  cursor: pointer !important;
}

#stableActionTactical:hover:not(:disabled), .stable-action-btn.tactical:hover:not(:disabled) {
  transform: translateY(-2.5px) !important;
  border-color: #ffffff !important;
  background: linear-gradient(180deg, rgba(255,255,255,0.45) 0%, rgba(255,255,255,0) 45%), linear-gradient(180deg, #d8b2ff 0%, #a264f5 45%, #642ab5 100%) !important;
  box-shadow: inset 0 2.5px 4px rgba(255, 255, 255, 0.8), inset 0 -3px 6px rgba(0, 0, 0, 0.4), 0 10px 24px rgba(0, 0, 0, 0.8), 0 0 22px rgba(146, 84, 222, 0.65) !important;
}

#stableActionTactical:active:not(:disabled), .stable-action-btn.tactical:active:not(:disabled) {
  transform: translateY(2px) !important;
  box-shadow: inset 0 3px 6px rgba(0, 0, 0, 0.6) !important;
}

#stableActionTactical.active, .stable-action-btn.tactical.active {
  border-color: #ffe600 !important;
  box-shadow: inset 0 2px 4px #ffffff, 0 0 22px #ffe600, 0 6px 18px rgba(0,0,0,0.8) !important;
}

/* 進攻宣言按鈕 (朱紅烈焰) */
#stableActionAttack, .stable-action-btn.attack {
  background: linear-gradient(180deg, rgba(255,255,255,0.35) 0%, rgba(255,255,255,0) 45%), linear-gradient(180deg, #ff9c9e 0%, #ff4d4f 45%, #cf1322 100%) !important;
  color: #ffffff !important;
  border: 1.5px solid rgba(255, 180, 180, 0.8) !important;
  border-radius: 14px !important;
  font-weight: 900 !important;
  font-size: 14px !important;
  text-shadow: 1.5px 1.5px 0 #000000 !important;
  box-shadow: inset 0 2px 3px rgba(255, 255, 255, 0.6), inset 0 -3px 6px rgba(0, 0, 0, 0.4), 0 6px 18px rgba(0, 0, 0, 0.7), 0 0 14px rgba(255, 77, 79, 0.4) !important;
  cursor: pointer !important;
}

#stableActionAttack:hover:not(:disabled), .stable-action-btn.attack:hover:not(:disabled) {
  transform: translateY(-2.5px) !important;
  border-color: #ffffff !important;
  background: linear-gradient(180deg, rgba(255,255,255,0.45) 0%, rgba(255,255,255,0) 45%), linear-gradient(180deg, #ffb3b5 0%, #ff6668 45%, #e01b2c 100%) !important;
  box-shadow: inset 0 2.5px 4px rgba(255, 255, 255, 0.8), inset 0 -3px 6px rgba(0, 0, 0, 0.4), 0 10px 24px rgba(0, 0, 0, 0.8), 0 0 22px rgba(255, 77, 79, 0.65) !important;
}

#stableActionAttack:active:not(:disabled), .stable-action-btn.attack:active:not(:disabled) {
  transform: translateY(2px) !important;
  box-shadow: inset 0 3px 6px rgba(0, 0, 0, 0.6) !important;
}

#stableActionAttack.active, .stable-action-btn.attack.active {
  border-color: #ffe600 !important;
  box-shadow: inset 0 2px 4px #ffffff, 0 0 22px #ffe600, 0 6px 18px rgba(0,0,0,0.8) !important;
}

/* 確認獻祭與取消選擇按鈕 */
#stableActionConfirm, .stable-action-btn.tribute {
  background: linear-gradient(180deg, rgba(255,255,255,0.35) 0%, rgba(255,255,255,0) 45%), linear-gradient(180deg, #fff7a0 0%, #ffd700 45%, #c99c00 100%) !important;
  color: #000000 !important;
  border: 1.5px solid rgba(255, 235, 120, 0.85) !important;
  border-radius: 14px !important;
  font-weight: 900 !important;
}

#stableActionCancel, .stable-action-btn.tribute-cancel {
  background: linear-gradient(180deg, rgba(255,255,255,0.2) 0%, rgba(255,255,255,0) 45%), linear-gradient(180deg, #595959 0%, #333333 45%, #141414 100%) !important;
  color: #ffffff !important;
  border: 1.5px solid rgba(200, 200, 200, 0.6) !important;
  border-radius: 14px !important;
  font-weight: 900 !important;
}

/* 9. 種族提示卡 3D 光滑圓角 */
#enemyRace, #playerRace {
  border: 1.5px solid rgba(255, 230, 100, 0.7) !important;
  border-radius: 14px !important;
  box-shadow: inset 0 2px 3px rgba(255, 255, 255, 0.45), inset 0 -3px 6px rgba(0, 0, 0, 0.4), 0 6px 20px rgba(0, 0, 0, 0.8), 0 0 14px rgba(255, 230, 0, 0.25) !important;
}

#enemyRace:hover, #playerRace:hover {
  box-shadow: inset 0 2.5px 4px rgba(255, 255, 255, 0.65), inset 0 -3px 6px rgba(0, 0, 0, 0.4), 0 8px 25px rgba(0, 0, 0, 0.9), 0 0 22px rgba(255, 230, 0, 0.5) !important;
}
"""

    css_content += smooth_3d_css
    open(css_path, 'w', encoding='utf-8').write(css_content)
    print("1. Updated static/style_v8.css with smooth, rounded 3D glassmorphic theme successfully!")

    # Update cache-buster in static/index.html to v=10.30-smooth-rounded-3d-theme
    idx_path = 'static/index.html'
    idx_content = open(idx_path, encoding='utf-8').read()
    idx_content = re.sub(r'game_v8\.js\?v=[^"\']+', 'game_v8.js?v=10.30-smooth-rounded-3d-theme', idx_content)
    idx_content = re.sub(r'style_v8\.css\?v=[^"\']+', 'style_v8.css?v=10.30-smooth-rounded-3d-theme', idx_content)
    open(idx_path, 'w', encoding='utf-8').write(idx_content)
    print("2. Updated static/index.html cache-buster successfully!")

if __name__ == '__main__':
    refine_buttons()
