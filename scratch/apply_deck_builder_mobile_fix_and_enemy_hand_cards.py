# -*- coding: utf-8 -*-
import os, sys, re

def apply_fixes():
    sys.stdout.reconfigure(encoding='utf-8')

    base_dir = os.getcwd()
    js_path = os.path.join(base_dir, 'static', 'game_v8.js')
    css_path = os.path.join(base_dir, 'static', 'style_v8.css')
    idx_path = os.path.join(base_dir, 'static', 'index.html')
    builder_path = os.path.join(base_dir, 'static', 'deck_builder.html')

    # 1. Fix deck_builder.html CSS media queries for all mobile screen sizes (max-width: 1200px, max-height: 750px)
    builder_content = open(builder_path, encoding='utf-8').read()

    # Expand media query from max-width 900px to max-width 1200px or max-height 750px
    builder_content = builder_content.replace(
        '@media (max-width: 900px)',
        '@media (max-width: 1200px), (max-height: 750px)'
    )

    open(builder_path, 'w', encoding='utf-8').write(builder_content)
    print("1. Updated deck_builder.html mobile RWD query successfully!")

    # 2. Update static/game_v8.js: renderEnemyFloatingHand
    js_content = open(js_path, encoding='utf-8').read()

    floating_hand_js = """
function renderEnemyFloatingHand() {
  let container = document.getElementById("xlwEnemyFloatingHand");
  if (!container) {
    container = document.createElement("div");
    container.id = "xlwEnemyFloatingHand";
    container.className = "xlw-enemy-floating-hand";
    document.body.appendChild(container);
  }
  
  if (!window.XLW_gameInProgress) {
    container.style.display = "none";
    return;
  }
  
  container.style.display = "flex";
  const handCount = window.XLW_ENEMY ? (window.XLW_ENEMY.hand ? window.XLW_ENEMY.hand.length : 0) : 0;
  
  let cardsHTML = '';
  for (let i = 0; i < handCount; i++) {
    cardsHTML += `<img src="/static/card_back.jpeg" class="floating-enemy-card-back" alt="對手手牌牌背">`;
  }
  
  container.innerHTML = `
    <div class="floating-enemy-hand-wrap">
      <span class="floating-enemy-count-badge">👾 對手手牌 (${handCount}張)</span>
      <div class="floating-enemy-cards-row">
        ${cardsHTML}
      </div>
    </div>
  `;
}
"""

    js_content += floating_hand_js

    # Hook renderEnemyFloatingHand into render()
    js_content = js_content.replace('function render() {', 'function render() {\n  renderEnemyFloatingHand();')
    js_content = js_content.replace('function startSinglePlayerGameActual(playerGoesFirst) {', 'function startSinglePlayerGameActual(playerGoesFirst) {\n  renderEnemyFloatingHand();')

    # Hide floating hand in returnToTitle and initGameEmptyState
    js_content = js_content.replace(
      'window.xlwReturnToTitle = function() {',
      'window.xlwReturnToTitle = function() {\n  const fh = document.getElementById("xlwEnemyFloatingHand"); if (fh) fh.style.display = "none";'
    )
    js_content = js_content.replace(
      'function initGameEmptyState() {',
      'function initGameEmptyState() {\n  const fh = document.getElementById("xlwEnemyFloatingHand"); if (fh) fh.style.display = "none";'
    )

    open(js_path, 'w', encoding='utf-8').write(js_content)
    print("2. Injected renderEnemyFloatingHand into game_v8.js successfully!")

    # 3. Update static/style_v8.css
    css_content = open(css_path, encoding='utf-8').read()

    # Move #phaseDisplayPanelHard next to player exile zone & shorten width
    old_phase_css = """  #phaseDisplayPanelHard {
    position: absolute !important;
    top: 0px !important;
    left: 205px !important;
    width: 500px !important;
    transform: scale(0.38) !important;
    transform-origin: top left !important;
    z-index: 999999 !important;
    display: none;
    flex-direction: column !important;
    align-items: center !important;
    padding: 2px 8px !important;
  }"""

    new_phase_css = """  #phaseDisplayPanelHard {
    position: absolute !important;
    top: 467.5px !important;
    right: 200px !important;
    left: auto !important;
    width: 230px !important;
    transform: scale(0.70) !important;
    transform-origin: top left !important;
    z-index: 99999 !important;
    display: none;
    flex-direction: column !important;
    align-items: center !important;
    padding: 4px 8px !important;
    background: rgba(12, 8, 22, 0.92) !important;
    border: 1px solid rgba(255, 215, 106, 0.4) !important;
    border-radius: 8px !important;
    box-shadow: 0 4px 15px rgba(0, 0, 0, 0.7) !important;
  }"""

    css_content = css_content.replace(old_phase_css, new_phase_css)

    # Append styles for floating opponent hand cards (top center)
    enemy_floating_hand_css = """

/* ===== 頂部中央對手懸浮手牌 (僅顯示牌背) ===== */
.xlw-enemy-floating-hand {
  position: absolute !important;
  top: 2px !important;
  left: 50% !important;
  transform: translateX(-50%) !important;
  z-index: 10000 !important;
  display: flex !important;
  flex-direction: column !important;
  align-items: center !important;
  pointer-events: none !important;
}

.floating-enemy-hand-wrap {
  display: flex !important;
  flex-direction: column !important;
  align-items: center !important;
  gap: 2px !important;
}

.floating-enemy-count-badge {
  font-size: 10px !important;
  font-weight: bold !important;
  color: #ffd76a !important;
  background: rgba(12, 8, 22, 0.85) !important;
  border: 0.5px solid rgba(255, 215, 106, 0.3) !important;
  border-radius: 10px !important;
  padding: 1px 6px !important;
  white-space: nowrap !important;
}

.floating-enemy-cards-row {
  display: flex !important;
  justify-content: center !important;
  align-items: center !important;
}

.floating-enemy-card-back {
  width: 28px !important;
  height: 42px !important;
  object-fit: cover !important;
  border-radius: 3px !important;
  border: 0.5px solid rgba(255, 215, 106, 0.4) !important;
  box-shadow: 0 2px 6px rgba(0, 0, 0, 0.6) !important;
  margin-left: -12px !important;
  transition: all 0.2s ease !important;
}

.floating-enemy-card-back:first-child {
  margin-left: 0 !important;
}
"""
    css_content += enemy_floating_hand_css

    open(css_path, 'w', encoding='utf-8').write(css_content)
    print("3. Updated style_v8.css with exile-aligned phase panel & top-center floating enemy hand cards successfully!")

    # 4. Update index.html cache-buster
    idx_content = open(idx_path, encoding='utf-8').read()
    idx_content = re.sub(r'game_v8\.js\?v=[^"\']+', 'game_v8.js?v=21.10-exile-phase-and-floating-enemy-hand', idx_content)
    idx_content = re.sub(r'style_v8\.css\?v=[^"\']+', 'style_v8.css?v=21.10-exile-phase-and-floating-enemy-hand', idx_content)
    open(idx_path, 'w', encoding='utf-8').write(idx_content)
    print("4. Updated index.html cache-buster successfully!")

if __name__ == '__main__':
    apply_fixes()
