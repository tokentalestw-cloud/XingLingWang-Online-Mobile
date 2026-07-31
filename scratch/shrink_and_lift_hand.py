# -*- coding: utf-8 -*-
import sys, re

def shrink_and_lift():
    sys.stdout.reconfigure(encoding='utf-8')

    js_path = 'static/game_v8.js'
    css_path = 'static/style_v8.css'
    idx_path = 'static/index.html'

    # 1. Update static/game_v8.js to use extremely short simplified texts for stats
    js_content = open(js_path, encoding='utf-8').read()

    # Locate scoreBadge.innerHTML generation and simplify
    old_score_html = """  scoreBadge.innerHTML = `
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

    new_score_html = """  scoreBadge.innerHTML = `
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

    js_content = js_content.replace(old_score_html, new_score_html)

    # Locate renderEnemyPanel and simplify text
    old_enemy_html = """  panel.innerHTML = `
    <div class="enemy-info-title">👾 對手狀態：<span class="enemy-deck-tag">${deckName}</span></div>
    <div class="enemy-stats-row" style="display: flex; gap: 8px; margin-top: 6px;">
      <div class="enemy-stat-badge">🎴 牌庫：<span id="enemyDeckCountInfo">${window.XLW_ENEMY.deck.length}</span> 張</div>
      <div class="enemy-stat-badge">🃏 手牌：<span id="enemyHandCountInfo">${window.XLW_ENEMY.hand.length}</span> 張</div>
    </div>
  `;"""

    new_enemy_html = """  panel.innerHTML = `
    <div class="enemy-info-title">對手 (${deckName})</div>
    <div class="enemy-stats-row" style="display: flex; gap: 6px; margin-top: 3px;">
      <div class="enemy-stat-badge">牌库:<span id="enemyDeckCountInfo">${window.XLW_ENEMY.deck.length}</span></div>
      <div class="enemy-stat-badge">手牌:<span id="enemyHandCountInfo">${window.XLW_ENEMY.hand.length}</span></div>
    </div>
  `;"""

    js_content = js_content.replace(old_enemy_html, new_enemy_html)
    open(js_path, 'w', encoding='utf-8').write(js_content)
    print("1. Simplified score and enemy panel HTML strings in game_v8.js successfully!")

    # 2. Update static/style_v8.css: change bottom to 114px, and widths of panels to 110px
    css_content = open(css_path, encoding='utf-8').read()

    # Update hand-panel bottom
    css_content = css_content.replace(
        "bottom: 14px !important;\n    left: 50% !important;\n    transform: translateX(-50%) !important;\n    width: 520px !important;",
        "bottom: 114px !important;\n    left: 50% !important;\n    transform: translateX(-50%) !important;\n    width: 520px !important;"
    )

    # Update widths of scoreBadgeFixed and xlwEnemyInfoPanel from 155px to 105px
    css_content = css_content.replace("width: 155px !important; /* 長寬大幅縮短，限縮為 155px */", "width: 105px !important; /* 極限縮減為 105px */")
    css_content = css_content.replace("width: 155px !important; /* 長寬大幅縮短，限縮為 155px */", "width: 105px !important; /* 極限縮減為 105px */") # Do it for both panels

    open(css_path, 'w', encoding='utf-8').write(css_content)
    print("2. Lifted hand-panel to bottom: 114px and shunk panel widths to 105px successfully!")

    # 3. Update cache-buster in static/index.html to v=17.90-hand-lifted-and-shrunk
    idx_content = open(idx_path, encoding='utf-8').read()
    idx_content = re.sub(r'game_v8\.js\?v=[^"\']+', 'game_v8.js?v=17.90-hand-lifted-and-shrunk', idx_content)
    idx_content = re.sub(r'style_v8\.css\?v=[^"\']+', 'style_v8.css?v=17.90-hand-lifted-and-shrunk', idx_content)
    open(idx_path, 'w', encoding='utf-8').write(idx_content)
    print("3. Updated static/index.html cache-buster successfully!")

if __name__ == '__main__':
    shrink_and_lift()
