# -*- coding: utf-8 -*-
import sys, re

def restore_balanced():
    sys.stdout.reconfigure(encoding='utf-8')

    js_path = 'static/game_v8.js'
    css_path = 'static/style_v8.css'
    idx_path = 'static/index.html'

    # 1. Restore game_v8.js HTML templates to readable standard labels
    js_content = open(js_path, encoding='utf-8').read()

    # Revert score badge html
    old_score_html = """  scoreBadge.innerHTML = `
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

    new_score_html = """  scoreBadge.innerHTML = `
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

    js_content = js_content.replace(old_score_html, new_score_html)

    # Revert enemy panel html
    old_enemy_html = """  panel.innerHTML = `
    <div class="enemy-info-title" style="font-size:8px; white-space:nowrap; overflow:hidden; text-overflow:ellipsis;">AI (${deckName})</div>
    <div class="enemy-stats-row" style="display: flex; flex-direction:column; gap: 1px; margin-top: 2px; font-size:7px;">
      <div>牌:${window.XLW_ENEMY.deck.length}</div>
      <div>手:${window.XLW_ENEMY.hand.length}</div>
    </div>
  `;"""

    new_enemy_html = """  panel.innerHTML = `
    <div class="enemy-info-title">👾 對手狀態：<span class="enemy-deck-tag">${deckName}</span></div>
    <div class="enemy-stats-row" style="display: flex; gap: 8px; margin-top: 6px;">
      <div class="enemy-stat-badge">🎴 牌庫：<span id="enemyDeckCountInfo">${window.XLW_ENEMY.deck.length}</span> 張</div>
      <div class="enemy-stat-badge">🃏 手牌：<span id="enemyHandCountInfo">${window.XLW_ENEMY.hand.length}</span> 張</div>
    </div>
  `;"""

    js_content = js_content.replace(old_enemy_html, new_enemy_html)
    open(js_path, 'w', encoding='utf-8').write(js_content)
    print("1. Restored JS templates to standard readable formats successfully!")

    # 2. Update static/style_v8.css: Revert bottom to 14px, and widths of panels to 230px
    css_content = open(css_path, encoding='utf-8').read()

    # Revert hand-panel bottom from 220px to 14px
    css_content = css_content.replace(
        "bottom: 220px !important;\n    left: 50% !important;\n    transform: translateX(-50%) !important;\n    width: 520px !important;",
        "bottom: 14px !important;\n    left: 50% !important;\n    transform: translateX(-50%) !important;\n    width: 520px !important;"
    )

    # Revert widths of scoreBadgeFixed and xlwEnemyInfoPanel from 55px to 230px
    # And z-indexes, font-sizes
    css_content = css_content.replace(
        """  #scoreBadgeFixed {
    position: absolute !important;
    left: 6px !important;
    top: 32px !important;
    right: auto !important;
    bottom: auto !important;
    z-index: 10000 !important;
    background: rgba(10, 8, 20, 0.85) !important;
    border: 1px solid rgba(255, 215, 106, 0.3) !important;
    border-radius: 6px !important;
    padding: 3px 5px !important;
    transform: scale(0.32) !important;
    transform-origin: top left !important;
    width: 55px !important; /* 寬度對半縮小至 55px */
    height: auto !important;
    margin: 0 !important;
  }""",
        """  #scoreBadgeFixed {
    position: absolute !important;
    left: 8px !important;
    top: 32px !important;
    right: auto !important;
    bottom: auto !important;
    z-index: 10000 !important;
    background: rgba(10, 8, 20, 0.85) !important;
    border: 1px solid rgba(255, 215, 106, 0.3) !important;
    border-radius: 8px !important;
    padding: 4px 6px !important;
    transform: scale(0.36) !important;
    transform-origin: top left !important;
    width: 230px !important;
    height: auto !important;
    margin: 0 !important;
  }"""
    )

    # Revert enemy info panel styles
    css_content = css_content.replace(
        """  #xlwEnemyInfoPanel {
    position: absolute !important;
    left: 6px !important;
    top: 86px !important; /* 向上靠緊分數看板 */
    right: auto !important;
    bottom: auto !important;
    z-index: 10000 !important;
    transform: scale(0.32) !important;
    transform-origin: top left !important;
    background: rgba(15, 10, 25, 0.85) !important;
    border: 1px solid rgba(255, 215, 106, 0.3) !important;
    border-radius: 6px !important;
    padding: 3px 5px !important;
    width: 55px !important; /* 寬度對半縮小至 55px */
    height: auto !important;
    margin: 0 !important;
    display: block !important;
  }""",
        """  #xlwEnemyInfoPanel {
    position: absolute !important;
    left: 8px !important;
    top: 100px !important;
    right: auto !important;
    bottom: auto !important;
    z-index: 10000 !important;
    transform: scale(0.36) !important;
    transform-origin: top left !important;
    background: rgba(15, 10, 25, 0.85) !important;
    border: 1px solid rgba(255, 215, 106, 0.3) !important;
    border-radius: 8px !important;
    padding: 4px 6px !important;
    margin: 0 !important;
    display: block !important;
    width: 230px !important;
  }"""
    )

    # Revert stableActionPanel styles
    css_content = css_content.replace(
        """  #stableActionPanel {
    position: absolute !important;
    right: 8px !important;
    bottom: 12px !important;
    top: auto !important;
    left: auto !important;
    z-index: 10000 !important;
    transform: scale(0.30) !important;
    transform-origin: bottom right !important;
    display: flex !important;
    flex-direction: column !important;
    gap: 5px !important;
    background: rgba(15, 10, 25, 0.85) !important;
    border: 1px solid rgba(255, 215, 106, 0.3) !important;
    border-radius: 8px !important;
    padding: 6px !important;
    box-shadow: 0 4px 15px rgba(0, 0, 0, 0.7) !important;
    margin: 0 !important;
    width: 120px !important;
  }""",
        """  #stableActionPanel {
    position: absolute !important;
    right: 8px !important;
    bottom: 12px !important;
    top: auto !important;
    left: auto !important;
    z-index: 10000 !important;
    transform: scale(0.32) !important;
    transform-origin: bottom right !important;
    display: flex !important;
    flex-direction: column !important;
    gap: 5px !important;
    background: rgba(15, 10, 25, 0.85) !important;
    border: 1px solid rgba(255, 215, 106, 0.3) !important;
    border-radius: 8px !important;
    padding: 6px !important;
    box-shadow: 0 4px 15px rgba(0, 0, 0, 0.7) !important;
    margin: 0 !important;
    width: 120px !important;
  }"""
    )

    open(css_path, 'w', encoding='utf-8').write(css_content)
    print("2. Restored CSS dimensions and layout coordinates in style_v8.css successfully!")

    # 3. Update cache-buster in static/index.html to v=18.20-proportions-restored
    idx_content = open(idx_path, encoding='utf-8').read()
    idx_content = re.sub(r'game_v8\.js\?v=[^"\']+', 'game_v8.js?v=18.20-proportions-restored', idx_content)
    idx_content = re.sub(r'style_v8\.css\?v=[^"\']+', 'style_v8.css?v=18.20-proportions-restored', idx_content)
    open(idx_path, 'w', encoding='utf-8').write(idx_content)
    print("3. Updated static/index.html cache-buster successfully!")

if __name__ == '__main__':
    restore_balanced()
