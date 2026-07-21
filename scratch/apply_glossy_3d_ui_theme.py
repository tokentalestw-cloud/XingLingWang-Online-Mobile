# -*- coding: utf-8 -*-
import sys, re

def apply_3d_theme():
    sys.stdout.reconfigure(encoding='utf-8')

    css_path = 'static/style_v8.css'
    css_content = open(css_path, encoding='utf-8').read()

    new_3d_css = """

/* ==========================================================================
   ULTRA-GLOSSY 3D TACTILE UI THEME (不改動任何比例與佈局座標)
   ========================================================================== */

/* 1. 遊戲中央 status 狀態提示列 */
#status, .status-bar, .xlw-status-box {
  background: linear-gradient(180deg, rgba(28, 20, 38, 0.96) 0%, rgba(14, 10, 20, 0.98) 100%) !important;
  border: 2px solid #ffe600 !important;
  border-bottom: 4.5px solid #9e7b00 !important;
  border-radius: 12px !important;
  color: #fff6c2 !important;
  font-weight: 900 !important;
  letter-spacing: 0.6px !important;
  text-shadow: 1.5px 1.5px 3px rgba(0, 0, 0, 0.95), 0 0 8px rgba(255, 230, 0, 0.4) !important;
  box-shadow: inset 0 1.5px 0 rgba(255, 255, 255, 0.35), 0 8px 25px rgba(0, 0, 0, 0.85), 0 0 18px rgba(255, 230, 0, 0.25) !important;
  padding: 10px 18px !important;
  backdrop-filter: blur(12px) !important;
  transition: all 0.2s ease !important;
}

/* 2. 結束回合與動作控制按鈕 */
#endTurnBtn, .end-turn-btn {
  background: linear-gradient(180deg, #ff7070 0%, #e61919 48%, #870000 100%) !important;
  color: #ffffff !important;
  border: 2.5px solid #ffe600 !important;
  border-bottom: 5px solid #4a0000 !important;
  border-radius: 10px !important;
  font-weight: 900 !important;
  font-size: 15px !important;
  text-shadow: 1.5px 1.5px 0 #000000 !important;
  box-shadow: inset 0 2px 0 rgba(255, 255, 255, 0.5), 0 6px 18px rgba(0, 0, 0, 0.7), 0 0 12px rgba(255, 31, 76, 0.4) !important;
  cursor: pointer !important;
  transition: transform 0.12s ease, box-shadow 0.12s ease !important;
}

#endTurnBtn:hover:not(:disabled), .end-turn-btn:hover:not(:disabled) {
  transform: translateY(-2px) !important;
  background: linear-gradient(180deg, #ff9494 0%, #ff2e2e 48%, #a30000 100%) !important;
  box-shadow: inset 0 2px 0 rgba(255, 255, 255, 0.7), 0 9px 24px rgba(0, 0, 0, 0.8), 0 0 20px rgba(255, 31, 76, 0.7) !important;
}

#endTurnBtn:active:not(:disabled), .end-turn-btn:active:not(:disabled) {
  transform: translateY(3px) !important;
  border-bottom-width: 2px !important;
  box-shadow: inset 0 2px 6px rgba(0,0,0,0.6) !important;
}

/* 3. 種族提示卡 3D 質感外框 (嚴格保持原始尺寸與座標) */
#enemyRace, #playerRace {
  border: 2px solid #ffe600 !important;
  border-bottom: 4.5px solid #8c6d00 !important;
  border-radius: 10px !important;
  box-shadow: inset 0 1.5px 0 rgba(255, 255, 255, 0.45), 0 6px 20px rgba(0, 0, 0, 0.8), 0 0 12px rgba(255, 230, 0, 0.25) !important;
  transition: transform 0.2s ease, box-shadow 0.2s ease !important;
}

#enemyRace:hover, #playerRace:hover {
  box-shadow: inset 0 1.5px 0 rgba(255, 255, 255, 0.65), 0 8px 25px rgba(0, 0, 0, 0.9), 0 0 20px rgba(255, 230, 0, 0.5) !important;
}

/* 4. 通用彈窗、對話框與選單按鈕 3D 質感 */
button:not(.slot), select, .modal-content button, .xlw-modal button, .forest-summon-btn {
  border-radius: 8px !important;
  font-weight: 800 !important;
  letter-spacing: 0.4px !important;
  box-shadow: inset 0 1.5px 0 rgba(255, 255, 255, 0.4), 0 4px 12px rgba(0, 0, 0, 0.6) !important;
  transition: transform 0.12s ease, box-shadow 0.12s ease !important;
}

button:hover:not(:disabled), select:hover {
  filter: brightness(1.1) !important;
}

button:active:not(:disabled), select:active {
  transform: translateY(2px) !important;
}

"""

    css_content += new_3d_css
    open(css_path, 'w', encoding='utf-8').write(css_content)
    print("1. Appended ultra-glossy 3D tactile theme to static/style_v8.css successfully!")

    # Update cache-buster in static/index.html to v=10.10-glossy-3d-theme
    idx_path = 'static/index.html'
    idx_content = open(idx_path, encoding='utf-8').read()
    idx_content = re.sub(r'game_v8\.js\?v=[^"\']+', 'game_v8.js?v=10.10-glossy-3d-theme', idx_content)
    idx_content = re.sub(r'style_v8\.css\?v=[^"\']+', 'style_v8.css?v=10.10-glossy-3d-theme', idx_content)
    open(idx_path, 'w', encoding='utf-8').write(idx_content)
    print("2. Updated static/index.html cache-buster successfully!")

if __name__ == '__main__':
    apply_3d_theme()
