# -*- coding: utf-8 -*-
import sys, re

def apply_harmonious_palette():
    sys.stdout.reconfigure(encoding='utf-8')

    css_path = 'static/style_v8.css'
    css_content = open(css_path, encoding='utf-8').read()

    harmonious_css = """

/* ==========================================================================
   HARMONIOUS DARK OBSIDIAN PALETTE & SUBDUED NON-DISTRACTING UI
   (將按鈕與狀態欄調成沉穩高級黑曜石色調，突顯中央主要卡牌對戰畫面)
   ========================================================================== */

/* 1. 對手狀態欄 (#xlwEnemyInfoPanel) 沉穩暗紅黑曜石調 */
#xlwEnemyInfoPanel, .xlw-enemy-info-panel {
  background: linear-gradient(180deg, rgba(34, 18, 26, 0.95) 0%, rgba(16, 9, 13, 0.98) 100%) !important;
  border: 1.5px solid rgba(200, 90, 90, 0.55) !important;
  border-bottom: 4px solid #571013 !important;
  color: #f5e6e8 !important;
  box-shadow: inset 0 1.5px 0 rgba(255,255,255,0.25), 0 8px 25px rgba(0, 0, 0, 0.85) !important;
}

#xlwEnemyInfoPanel:hover {
  transform: translateY(-2px) !important;
  box-shadow: inset 0 2px 0 rgba(255,255,255,0.35), 0 12px 30px rgba(0, 0, 0, 0.95) !important;
}

#xlwEnemyInfoPanel .enemy-info-title {
  color: #fca5a5 !important;
  text-shadow: 0 1px 2px rgba(0, 0, 0, 0.8) !important;
}

#xlwEnemyInfoPanel .enemy-deck-tag {
  color: #fef08a !important;
  background: rgba(0, 0, 0, 0.45) !important;
  border: 1px solid rgba(234, 179, 8, 0.6) !important;
  box-shadow: none !important;
}

.enemy-stat-badge {
  background: linear-gradient(180deg, rgba(255,255,255,0.08) 0%, rgba(0,0,0,0.45) 100%) !important;
  border: 1px solid rgba(234, 179, 8, 0.5) !important;
  border-bottom: 2.5px solid #473708 !important;
  color: #fef08a !important;
  box-shadow: inset 0 1px 0 rgba(255,255,255,0.2), 0 3px 8px rgba(0,0,0,0.5) !important;
}

.enemy-stat-badge span {
  color: #fef08a !important;
  text-shadow: 0 1px 2px rgba(0, 0, 0, 0.8) !important;
}

/* 2. 主畫面左上角 HUD 雙方總分欄 (.score-badge-fixed) 沉穩暗金黑曜石調 */
.score-badge-fixed {
  background: linear-gradient(180deg, rgba(28, 22, 34, 0.95) 0%, rgba(12, 10, 16, 0.98) 100%) !important;
  border: 1.5px solid rgba(212, 175, 55, 0.55) !important;
  border-bottom: 4px solid #574610 !important;
  color: #f5f0e6 !important;
  box-shadow: inset 0 1.5px 0 rgba(255,255,255,0.25), 0 8px 25px rgba(0, 0, 0, 0.85) !important;
}

.score-badge-fixed:hover {
  transform: translateY(-2px) !important;
  box-shadow: inset 0 2px 0 rgba(255,255,255,0.35), 0 12px 30px rgba(0, 0, 0, 0.95) !important;
}

.score-badge-card {
  background: linear-gradient(180deg, rgba(255,255,255,0.06) 0%, rgba(0,0,0,0.35) 100%) !important;
  border: 1px solid rgba(212, 175, 55, 0.45) !important;
  border-bottom: 2.5px solid #4a3c0c !important;
}

.score-badge-card.enemy {
  border-color: rgba(200, 90, 90, 0.45) !important;
  border-bottom-color: #571013 !important;
}

.score-badge-label {
  color: #fef08a !important;
  text-shadow: 0 1px 2px rgba(0, 0, 0, 0.8) !important;
}

.score-badge-label.enemy-label {
  color: #fca5a5 !important;
  text-shadow: 0 1px 2px rgba(0, 0, 0, 0.8) !important;
}

.score-badge-num {
  background: linear-gradient(180deg, rgba(255,255,255,0.12) 0%, rgba(0,0,0,0.45) 100%) !important;
  border: 1px solid rgba(234, 179, 8, 0.6) !important;
  border-bottom: 2px solid #574610 !important;
  color: #fef08a !important;
  text-shadow: 0 1px 2px rgba(0, 0, 0, 0.8) !important;
  box-shadow: inset 0 1px 0 rgba(255,255,255,0.2), 0 2px 6px rgba(0,0,0,0.5) !important;
}

.score-badge-num.enemy-num {
  border-color: rgba(239, 68, 68, 0.6) !important;
  border-bottom-color: #571013 !important;
  color: #fca5a5 !important;
  text-shadow: 0 1px 2px rgba(0, 0, 0, 0.8) !important;
  box-shadow: inset 0 1px 0 rgba(255,255,255,0.2), 0 2px 6px rgba(0,0,0,0.5) !important;
}

/* 3. 戰術佈陣與進攻宣言按鈕調成沉穩黑曜金屬調 */
#stableActionTactical, .stable-action-btn.tactical {
  background: linear-gradient(180deg, rgba(255,255,255,0.18) 0%, rgba(0,0,0,0) 45%), linear-gradient(180deg, #473819 0%, #291e0a 100%) !important;
  color: #fef08a !important;
  border: 1.5px solid rgba(212, 175, 55, 0.65) !important;
  border-radius: 12px !important;
  box-shadow: inset 0 1.5px 0 rgba(255, 255, 255, 0.35), 0 4px 12px rgba(0, 0, 0, 0.6) !important;
}

#stableActionTactical:hover:not(:disabled), .stable-action-btn.tactical:hover:not(:disabled) {
  background: linear-gradient(180deg, rgba(255,255,255,0.25) 0%, rgba(0,0,0,0) 45%), linear-gradient(180deg, #594821 0%, #36290f 100%) !important;
  border-color: #fef08a !important;
  box-shadow: inset 0 2px 0 rgba(255, 255, 255, 0.5), 0 6px 16px rgba(0, 0, 0, 0.75) !important;
}

#stableActionAttack, .stable-action-btn.attack {
  background: linear-gradient(180deg, rgba(255,255,255,0.18) 0%, rgba(0,0,0,0) 45%), linear-gradient(180deg, #4a1f22 0%, #260c0e 100%) !important;
  color: #fca5a5 !important;
  border: 1.5px solid rgba(200, 90, 90, 0.65) !important;
  border-radius: 12px !important;
  box-shadow: inset 0 1.5px 0 rgba(255, 255, 255, 0.35), 0 4px 12px rgba(0, 0, 0, 0.6) !important;
}

#stableActionAttack:hover:not(:disabled), .stable-action-btn.attack:hover:not(:disabled) {
  background: linear-gradient(180deg, rgba(255,255,255,0.25) 0%, rgba(0,0,0,0) 45%), linear-gradient(180deg, #5c272a 0%, #331013 100%) !important;
  border-color: #fca5a5 !important;
  box-shadow: inset 0 2px 0 rgba(255, 255, 255, 0.5), 0 6px 16px rgba(0, 0, 0, 0.75) !important;
}

/* 4. 結束回合按鈕調成沉穩暗紫黑曜石調 */
#endTurnBtn, .end-turn-btn {
  background: linear-gradient(180deg, rgba(255,255,255,0.18) 0%, rgba(0,0,0,0) 45%), linear-gradient(180deg, #362247 0%, #1a0d24 100%) !important;
  color: #e9d5ff !important;
  border: 1.5px solid rgba(168, 85, 247, 0.55) !important;
  border-radius: 12px !important;
  box-shadow: inset 0 1.5px 0 rgba(255, 255, 255, 0.3), 0 4px 12px rgba(0, 0, 0, 0.6) !important;
}

#endTurnBtn:hover:not(:disabled), .end-turn-btn:hover:not(:disabled) {
  background: linear-gradient(180deg, rgba(255,255,255,0.25) 0%, rgba(0,0,0,0) 45%), linear-gradient(180deg, #462c5c 0%, #241233 100%) !important;
  border-color: #e9d5ff !important;
  box-shadow: inset 0 2px 0 rgba(255, 255, 255, 0.45), 0 6px 16px rgba(0, 0, 0, 0.75) !important;
}

/* 5. 我方森林區可召喚脈衝光柔和自然化 */
#playerForest.active-summon-forest {
  border: 2px solid #2ec4b6 !important;
  box-shadow: 0 0 16px rgba(46, 196, 182, 0.6), inset 0 0 12px rgba(46, 196, 182, 0.3) !important;
}

@keyframes forestCanSummonPulse {
  0% {
    box-shadow: 0 0 10px rgba(46, 196, 182, 0.4), inset 0 0 8px rgba(46, 196, 182, 0.2);
    border-color: #2ec4b6;
  }
  50% {
    box-shadow: 0 0 20px rgba(46, 196, 182, 0.75), inset 0 0 15px rgba(46, 196, 182, 0.4);
    border-color: #80e5ff;
  }
  100% {
    box-shadow: 0 0 10px rgba(46, 196, 182, 0.4), inset 0 0 8px rgba(46, 196, 182, 0.2);
    border-color: #2ec4b6;
  }
}

"""

    css_content += harmonious_css
    open(css_path, 'w', encoding='utf-8').write(css_content)
    print("1. Updated static/style_v8.css with harmonious dark obsidian palette successfully!")

    # Update cache-buster in static/index.html to v=11.60-harmonious-obsidian-palette
    idx_path = 'static/index.html'
    idx_content = open(idx_path, encoding='utf-8').read()
    idx_content = re.sub(r'game_v8\.js\?v=[^"\']+', 'game_v8.js?v=11.60-harmonious-obsidian-palette', idx_content)
    idx_content = re.sub(r'style_v8\.css\?v=[^"\']+', 'style_v8.css?v=11.60-harmonious-obsidian-palette', idx_content)
    open(idx_path, 'w', encoding='utf-8').write(idx_content)
    print("2. Updated static/index.html cache-buster successfully!")

if __name__ == '__main__':
    apply_harmonious_palette()
