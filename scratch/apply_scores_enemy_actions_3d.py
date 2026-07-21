# -*- coding: utf-8 -*-
import sys, re

def apply_scores_enemy_actions_3d():
    sys.stdout.reconfigure(encoding='utf-8')

    css_path = 'static/style_v8.css'
    css_content = open(css_path, encoding='utf-8').read()

    new_scores_3d_css = """

/* ==========================================================================
   3D TACTILE SCORE BOXES, OPPONENT STATUS PANEL & ACTION BUTTONS
   (雙方總分、對手狀態欄位與戰術佈陣/進攻宣言按鈕全面立體化)
   ========================================================================== */

/* 1. 雙方總分計分板 (Score Boxes & Panel) */
.score-box, #scoreBoard, #scorePanel .score-card, #enemyScore, #playerScore {
  background: linear-gradient(180deg, rgba(28, 20, 38, 0.96) 0%, rgba(14, 10, 20, 0.98) 100%) !important;
  border: 2.5px solid #ffe600 !important;
  border-bottom: 5px solid #8c6d00 !important;
  border-radius: 12px !important;
  color: #ffffff !important;
  font-weight: 900 !important;
  box-shadow: inset 0 1.5px 0 rgba(255, 255, 255, 0.4), 0 8px 25px rgba(0, 0, 0, 0.85), 0 0 18px rgba(255, 230, 0, 0.3) !important;
  text-shadow: 1px 1px 2px #000 !important;
  transition: transform 0.2s ease, box-shadow 0.2s ease !important;
}

.score-box:hover, #enemyScore:hover, #playerScore:hover {
  transform: translateY(-2px) !important;
  box-shadow: inset 0 1.5px 0 rgba(255, 255, 255, 0.6), 0 10px 30px rgba(0, 0, 0, 0.9), 0 0 24px rgba(255, 230, 0, 0.5) !important;
}

.score-val, #enemyScoreVal, #playerScoreVal {
  color: #ffe600 !important;
  font-weight: 900 !important;
  text-shadow: 0 0 12px rgba(255, 230, 0, 0.8), 2px 2px 0 #000 !important;
}

/* 2. 對手狀態欄位 (#xlwEnemyInfoPanel) */
#xlwEnemyInfoPanel, .xlw-enemy-info-panel {
  background: linear-gradient(180deg, rgba(36, 16, 26, 0.96) 0%, rgba(16, 8, 14, 0.98) 100%) !important;
  border: 2.5px solid #ff4d4f !important;
  border-bottom: 5px solid #870003 !important;
  border-radius: 14px !important;
  color: #fff0f2 !important;
  padding: 12px 16px !important;
  font-weight: 800 !important;
  box-shadow: inset 0 1.5px 0 rgba(255, 255, 255, 0.35), 0 8px 25px rgba(0, 0, 0, 0.9), 0 0 18px rgba(255, 77, 79, 0.35) !important;
  backdrop-filter: blur(12px) !important;
  transition: all 0.2s ease !important;
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

/* 3. 右下主操作面板與按鈕 (#stableActionPanel) */
#stableActionPanel {
  background: linear-gradient(180deg, rgba(20, 15, 28, 0.96) 0%, rgba(10, 8, 16, 0.98) 100%) !important;
  border: 2.5px solid #ffe600 !important;
  border-bottom: 5px solid #8c6d00 !important;
  border-radius: 16px !important;
  padding: 12px !important;
  box-shadow: inset 0 1.5px 0 rgba(255, 255, 255, 0.35), 0 10px 30px rgba(0, 0, 0, 0.92), 0 0 20px rgba(255, 230, 0, 0.3) !important;
  backdrop-filter: blur(12px) !important;
}

/* 戰術佈陣按鈕 */
#stableActionTactical, .stable-action-btn.tactical {
  background: linear-gradient(180deg, #b37feb 0%, #722ed1 48%, #391085 100%) !important;
  color: #ffffff !important;
  border: 2px solid #d3ade6 !important;
  border-bottom: 4.5px solid #22075e !important;
  border-radius: 10px !important;
  font-weight: 900 !important;
  font-size: 14px !important;
  text-shadow: 1.5px 1.5px 0 #000000 !important;
  box-shadow: inset 0 1.5px 0 rgba(255, 255, 255, 0.6), 0 6px 18px rgba(0, 0, 0, 0.7), 0 0 12px rgba(114, 46, 209, 0.4) !important;
  cursor: pointer !important;
  transition: transform 0.12s ease, box-shadow 0.12s ease !important;
}

#stableActionTactical:hover:not(:disabled), .stable-action-btn.tactical:hover:not(:disabled) {
  transform: translateY(-2px) !important;
  background: linear-gradient(180deg, #c896ff 0%, #853ee3 48%, #4a17a8 100%) !important;
  box-shadow: inset 0 2px 0 rgba(255, 255, 255, 0.8), 0 8px 22px rgba(0, 0, 0, 0.8), 0 0 18px rgba(114, 46, 209, 0.65) !important;
}

#stableActionTactical:active:not(:disabled), .stable-action-btn.tactical:active:not(:disabled) {
  transform: translateY(3px) !important;
  border-bottom-width: 2px !important;
  box-shadow: inset 0 2px 6px rgba(0, 0, 0, 0.6) !important;
}

#stableActionTactical.active, .stable-action-btn.tactical.active {
  border-color: #ffe600 !important;
  box-shadow: inset 0 1.5px 0 #ffffff, 0 0 22px #ffe600, 0 6px 18px rgba(0,0,0,0.8) !important;
}

/* 進攻宣言按鈕 */
#stableActionAttack, .stable-action-btn.attack {
  background: linear-gradient(180deg, #ff7875 0%, #ff4d4f 48%, #a8071a 100%) !important;
  color: #ffffff !important;
  border: 2px solid #ffccc7 !important;
  border-bottom: 4.5px solid #5c0011 !important;
  border-radius: 10px !important;
  font-weight: 900 !important;
  font-size: 14px !important;
  text-shadow: 1.5px 1.5px 0 #000000 !important;
  box-shadow: inset 0 1.5px 0 rgba(255, 255, 255, 0.6), 0 6px 18px rgba(0, 0, 0, 0.7), 0 0 12px rgba(255, 77, 79, 0.4) !important;
  cursor: pointer !important;
  transition: transform 0.12s ease, box-shadow 0.12s ease !important;
}

#stableActionAttack:hover:not(:disabled), .stable-action-btn.attack:hover:not(:disabled) {
  transform: translateY(-2px) !important;
  background: linear-gradient(180deg, #ff9c99 0%, #ff6b6d 48%, #c40a20 100%) !important;
  box-shadow: inset 0 2px 0 rgba(255, 255, 255, 0.8), 0 8px 22px rgba(0, 0, 0, 0.8), 0 0 18px rgba(255, 77, 79, 0.65) !important;
}

#stableActionAttack:active:not(:disabled), .stable-action-btn.attack:active:not(:disabled) {
  transform: translateY(3px) !important;
  border-bottom-width: 2px !important;
  box-shadow: inset 0 2px 6px rgba(0, 0, 0, 0.6) !important;
}

#stableActionAttack.active, .stable-action-btn.attack.active {
  border-color: #ffe600 !important;
  box-shadow: inset 0 1.5px 0 #ffffff, 0 0 22px #ffe600, 0 6px 18px rgba(0,0,0,0.8) !important;
}

/* 確認獻祭與取消選擇按鈕 */
#stableActionConfirm, .stable-action-btn.tribute {
  background: linear-gradient(180deg, #fffaaa 0%, #ffd700 48%, #b88600 100%) !important;
  color: #000000 !important;
  border: 2px solid #000000 !important;
  border-bottom: 4.5px solid #664d00 !important;
  border-radius: 10px !important;
  font-weight: 900 !important;
}

#stableActionCancel, .stable-action-btn.tribute-cancel {
  background: linear-gradient(180deg, #434343 0%, #262626 48%, #000000 100%) !important;
  color: #ffffff !important;
  border: 2px solid #bfbfbf !important;
  border-bottom: 4.5px solid #000000 !important;
  border-radius: 10px !important;
  font-weight: 900 !important;
}

"""

    css_content += new_scores_3d_css
    open(css_path, 'w', encoding='utf-8').write(css_content)
    print("1. Appended 3D score boxes, opponent status & action buttons CSS successfully!")

    # Update cache-buster in static/index.html to v=10.20-scores-enemy-actions-3d
    idx_path = 'static/index.html'
    idx_content = open(idx_path, encoding='utf-8').read()
    idx_content = re.sub(r'game_v8\.js\?v=[^"\']+', 'game_v8.js?v=10.20-scores-enemy-actions-3d', idx_content)
    idx_content = re.sub(r'style_v8\.css\?v=[^"\']+', 'style_v8.css?v=10.20-scores-enemy-actions-3d', idx_content)
    open(idx_path, 'w', encoding='utf-8').write(idx_content)
    print("2. Updated static/index.html cache-buster successfully!")

if __name__ == '__main__':
    apply_scores_enemy_actions_3d()
