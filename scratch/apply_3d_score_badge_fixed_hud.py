# -*- coding: utf-8 -*-
import sys, re

def apply_3d_score_hud():
    sys.stdout.reconfigure(encoding='utf-8')

    # 1. Update renderScore HTML in static/game_v8.js for 3D card structure
    js_path = 'static/game_v8.js'
    js_content = open(js_path, encoding='utf-8').read()

    old_score_badge_html = """  scoreBadge.innerHTML = `
    <div class="score-badge-section">
      <div class="score-badge-row">
        <span class="score-badge-label">我方總分</span>
        <span class="score-badge-num">${playerStars} ★</span>
      </div>
      <div class="score-badge-subrow">
        <span>場上星星: <span style="color: #ffd76a;">${playerFieldStars} ★</span> | 額外分數: <span style="color: #ff5252;">${playerBonusScore} ★</span></span>
      </div>
      <div class="score-badge-row" style="margin-top: 6px;">
        <span class="score-badge-label">對手總分</span>
        <span class="score-badge-num">${enemyStars} ★</span>
      </div>
      <div class="score-badge-subrow">
        <span>場上星星: <span style="color: #ffd76a;">${enemyFieldStars} ★</span> | 額外分數: <span style="color: #ff5252;">${enemyBonusScore} ★</span></span>
      </div>
    </div>
  `;"""

    new_score_badge_html = """  scoreBadge.innerHTML = `
    <div class="score-badge-section">
      <div class="score-badge-card player">
        <div class="score-badge-row">
          <span class="score-badge-label">👑 我方總分</span>
          <span class="score-badge-num player-num">${playerStars} ★</span>
        </div>
        <div class="score-badge-subrow">
          <span>場上單位: <span style="color: #ffe600; font-weight: 900;">${playerFieldStars} ★</span> | 額外加分: <span style="color: #ff7875; font-weight: 900;">${playerBonusScore} ★</span></span>
        </div>
      </div>
      <div class="score-badge-card enemy">
        <div class="score-badge-row">
          <span class="score-badge-label enemy-label">👾 對手總分</span>
          <span class="score-badge-num enemy-num">${enemyStars} ★</span>
        </div>
        <div class="score-badge-subrow">
          <span>場上單位: <span style="color: #ffe600; font-weight: 900;">${enemyFieldStars} ★</span> | 額外加分: <span style="color: #ff7875; font-weight: 900;">${enemyBonusScore} ★</span></span>
        </div>
      </div>
    </div>
  `;"""

    if "scoreBadge.innerHTML =" in js_content:
        js_content = js_content.replace(old_score_badge_html, new_score_badge_html)
        open(js_path, 'w', encoding='utf-8').write(js_content)
        print("1. Updated scoreBadge.innerHTML in static/game_v8.js with 3D cards successfully!")

    # 2. Append 3D HUD score CSS rules to static/style_v8.css
    css_path = 'static/style_v8.css'
    css_content = open(css_path, encoding='utf-8').read()

    hud_3d_css = """

/* ==========================================================================
   ULTRA 3D HUD TOTAL SCORE STATUS PANEL (.score-badge-fixed)
   (主畫面左上角【我方總分】與【對手總分】3D 金屬水晶 HUD 重構)
   ========================================================================== */

.score-badge-fixed {
  background: radial-gradient(circle at 50% 20%, rgba(255, 215, 0, 0.18) 0%, transparent 75%), linear-gradient(180deg, rgba(32, 24, 44, 0.97) 0%, rgba(14, 10, 22, 0.99) 100%) !important;
  border: 2px solid #ffe600 !important;
  border-bottom: 5.5px solid #8c6d00 !important;
  border-radius: 18px !important;
  width: 300px !important;
  padding: 14px 16px !important;
  box-shadow: inset 0 2px 4px rgba(255, 255, 255, 0.5), inset 0 -4px 8px rgba(0, 0, 0, 0.6), 0 12px 35px rgba(0, 0, 0, 0.92), 0 0 25px rgba(255, 230, 0, 0.4) !important;
  backdrop-filter: blur(16px) !important;
  transition: transform 0.25s cubic-bezier(0.16, 1, 0.3, 1), box-shadow 0.25s ease !important;
}

.score-badge-fixed:hover {
  transform: translateY(-3px) scale(1.02) !important;
  box-shadow: inset 0 2.5px 5px rgba(255, 255, 255, 0.75), inset 0 -4px 8px rgba(0, 0, 0, 0.6), 0 16px 40px rgba(0, 0, 0, 0.98), 0 0 32px rgba(255, 230, 0, 0.6) !important;
}

.score-badge-section {
  display: flex !important;
  flex-direction: column !important;
  gap: 10px !important;
}

.score-badge-card {
  background: linear-gradient(180deg, rgba(255,255,255,0.12) 0%, rgba(0,0,0,0.45) 100%) !important;
  border: 1.5px solid rgba(255, 230, 100, 0.6) !important;
  border-bottom: 3.5px solid #665000 !important;
  border-radius: 14px !important;
  padding: 8px 12px !important;
  box-shadow: inset 0 1.5px 0 rgba(255, 255, 255, 0.4), 0 4px 12px rgba(0, 0, 0, 0.6) !important;
  transition: transform 0.2s ease !important;
}

.score-badge-card.enemy {
  border-color: rgba(255, 100, 100, 0.65) !important;
  border-bottom-color: #870003 !important;
  background: linear-gradient(180deg, rgba(255,255,255,0.1) 0%, rgba(30,10,15,0.5) 100%) !important;
}

.score-badge-card:hover {
  transform: translateY(-2px) !important;
}

.score-badge-row {
  display: flex !important;
  align-items: center !important;
  justify-content: space-between !important;
  margin-bottom: 4px !important;
}

.score-badge-label {
  font-size: 15px !important;
  font-weight: 900 !important;
  color: #ffe600 !important;
  text-shadow: 1px 1px 0 #000, 0 0 8px rgba(255, 230, 0, 0.5) !important;
  width: auto !important;
}

.score-badge-label.enemy-label {
  color: #ff7875 !important;
  text-shadow: 1px 1px 0 #000, 0 0 8px rgba(255, 77, 79, 0.5) !important;
}

.score-badge-num {
  display: inline-block !important;
  background: linear-gradient(180deg, rgba(255,255,255,0.3) 0%, rgba(0,0,0,0.5) 100%) !important;
  border: 1.5px solid #ffe600 !important;
  border-bottom: 3px solid #8c6d00 !important;
  border-radius: 10px !important;
  padding: 2px 10px !important;
  color: #ffe600 !important;
  font-weight: 900 !important;
  font-size: 17px !important;
  text-shadow: 0 0 10px rgba(255, 230, 0, 0.9), 1.5px 1.5px 0 #000 !important;
  box-shadow: inset 0 1.5px 0 #ffffff, 0 3px 8px rgba(0,0,0,0.6), 0 0 12px rgba(255,230,0,0.5) !important;
  width: auto !important;
  text-align: center !important;
}

.score-badge-num.enemy-num {
  border-color: #ff4d4f !important;
  border-bottom-color: #870003 !important;
  color: #ff7875 !important;
  text-shadow: 0 0 10px rgba(255, 77, 79, 0.9), 1.5px 1.5px 0 #000 !important;
  box-shadow: inset 0 1.5px 0 #ffffff, 0 3px 8px rgba(0,0,0,0.6), 0 0 12px rgba(255,77,79,0.5) !important;
}

.score-badge-subrow {
  background: rgba(0, 0, 0, 0.45) !important;
  border: 1px solid rgba(255, 230, 100, 0.35) !important;
  border-radius: 8px !important;
  padding: 4px 8px !important;
  font-size: 11.5px !important;
  color: rgba(255, 255, 255, 0.85) !important;
  font-weight: bold !important;
  box-shadow: inset 0 1px 3px rgba(0, 0, 0, 0.5) !important;
}

"""

    css_content += hud_3d_css
    open(css_path, 'w', encoding='utf-8').write(css_content)
    print("2. Appended ultra 3D HUD score CSS to static/style_v8.css successfully!")

    # Update cache-buster in static/index.html to v=10.80-3d-score-badge-fixed-hud
    idx_path = 'static/index.html'
    idx_content = open(idx_path, encoding='utf-8').read()
    idx_content = re.sub(r'game_v8\.js\?v=[^"\']+', 'game_v8.js?v=10.80-3d-score-badge-fixed-hud', idx_content)
    idx_content = re.sub(r'style_v8\.css\?v=[^"\']+', 'style_v8.css?v=10.80-3d-score-badge-fixed-hud', idx_content)
    open(idx_path, 'w', encoding='utf-8').write(idx_content)
    print("3. Updated static/index.html cache-buster successfully!")

if __name__ == '__main__':
    apply_3d_score_hud()
