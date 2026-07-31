# -*- coding: utf-8 -*-
import sys, re

def further_shrink_lift():
    sys.stdout.reconfigure(encoding='utf-8')

    js_path = 'static/game_v8.js'
    css_path = 'static/style_v8.css'
    idx_path = 'static/index.html'

    # 1. Update static/game_v8.js to use ultra-abbreviated texts to fit 55px width
    js_content = open(js_path, encoding='utf-8').read()

    # Simplify score badge innerHTML
    old_score_html = """  scoreBadge.innerHTML = `
    <div class="score-badge-section">
      <div class="score-badge-card player">
        <div class="score-badge-row">
          <span class="score-badge-label">我方</span>
          <span class="score-badge-num player-num">${playerStars}★</span>
        </div>
        <div class="score-badge-subrow">
          <span>場上:${playerFieldStars}★|額外:${playerBonusScore}★</span>
        </div>
      </div>
      <div class="score-badge-card enemy">
        <div class="score-badge-row">
          <span class="score-badge-label enemy-label">對手</span>
          <span class="score-badge-num enemy-num">${enemyStars}★</span>
        </div>
        <div class="score-badge-subrow">
          <span>場上:${enemyFieldStars}★|額外:${enemyBonusScore}★</span>
        </div>
      </div>
    </div>
  `;"""

    new_score_html = """  scoreBadge.innerHTML = `
    <div class="score-badge-section">
      <div class="score-badge-card player">
        <div class="score-badge-row" style="display:flex; justify-content:space-between; align-items:center;">
          <span class="score-badge-label" style="font-size:8px;">我方</span>
          <span class="score-badge-num player-num" style="font-size:10px;">${playerStars}★</span>
        </div>
        <div class="score-badge-subrow" style="font-size:7px; opacity:0.8;">
          <span>場:${playerFieldStars}|加:${playerBonusScore}</span>
        </div>
      </div>
      <div class="score-badge-card enemy" style="margin-top:2px;">
        <div class="score-badge-row" style="display:flex; justify-content:space-between; align-items:center;">
          <span class="score-badge-label enemy-label" style="font-size:8px;">對手</span>
          <span class="score-badge-num enemy-num" style="font-size:10px;">${enemyStars}★</span>
        </div>
        <div class="score-badge-subrow" style="font-size:7px; opacity:0.8;">
          <span>場:${enemyFieldStars}|加:${enemyBonusScore}</span>
        </div>
      </div>
    </div>
  `;"""

    js_content = js_content.replace(old_score_html, new_score_html)

    # Simplify enemy status panel innerHTML
    old_enemy_html = """  panel.innerHTML = `
    <div class="enemy-info-title">對手 (${deckName})</div>
    <div class="enemy-stats-row" style="display: flex; gap: 6px; margin-top: 3px;">
      <div class="enemy-stat-badge">牌库:<span id="enemyDeckCountInfo">${window.XLW_ENEMY.deck.length}</span></div>
      <div class="enemy-stat-badge">手牌:<span id="enemyHandCountInfo">${window.XLW_ENEMY.hand.length}</span></div>
    </div>
  `;"""

    new_enemy_html = """  panel.innerHTML = `
    <div class="enemy-info-title" style="font-size:8px; white-space:nowrap; overflow:hidden; text-overflow:ellipsis;">AI (${deckName})</div>
    <div class="enemy-stats-row" style="display: flex; flex-direction:column; gap: 1px; margin-top: 2px; font-size:7px;">
      <div>牌:${window.XLW_ENEMY.deck.length}</div>
      <div>手:${window.XLW_ENEMY.hand.length}</div>
    </div>
  `;"""

    js_content = js_content.replace(old_enemy_html, new_enemy_html)
    open(js_path, 'w', encoding='utf-8').write(js_content)
    print("1. Ultra-simplified stats HUD strings in game_v8.js successfully!")

    # 2. Update static/style_v8.css: change bottom to 220px, and widths of panels to 55px
    css_content = open(css_path, encoding='utf-8').read()

    # Update hand-panel bottom from 114px to 220px
    css_content = css_content.replace(
        "bottom: 114px !important;\n    left: 50% !important;\n    transform: translateX(-50%) !important;\n    width: 520px !important;",
        "bottom: 220px !important;\n    left: 50% !important;\n    transform: translateX(-50%) !important;\n    width: 520px !important;"
    )

    # Update widths of scoreBadgeFixed and xlwEnemyInfoPanel from 105px to 55px
    css_content = css_content.replace("width: 105px !important; /* 極限縮減為 105px */", "width: 55px !important; /* 寬度對半縮小至 55px */")
    css_content = css_content.replace("width: 105px !important; /* 極限縮減為 105px */", "width: 55px !important; /* 寬度對半縮小至 55px */") # For both matches

    open(css_path, 'w', encoding='utf-8').write(css_content)
    print("2. Lifted hand-panel to bottom: 220px and halved HUD widths to 55px successfully!")

    # 3. Update cache-buster in static/index.html to v=18.00-further-shrunk-and-lifted
    idx_content = open(idx_path, encoding='utf-8').read()
    idx_content = re.sub(r'game_v8\.js\?v=[^"\']+', 'game_v8.js?v=18.00-further-shrunk-and-lifted', idx_content)
    idx_content = re.sub(r'style_v8\.css\?v=[^"\']+', 'style_v8.css?v=18.00-further-shrunk-and-lifted', idx_content)
    open(idx_path, 'w', encoding='utf-8').write(idx_content)
    print("3. Updated static/index.html cache-buster successfully!")

if __name__ == '__main__':
    further_shrink_lift()
