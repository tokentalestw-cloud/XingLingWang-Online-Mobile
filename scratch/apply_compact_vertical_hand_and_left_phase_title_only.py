# -*- coding: utf-8 -*-
import os, sys, re

def apply_fixes():
    sys.stdout.reconfigure(encoding='utf-8')

    base_dir = os.getcwd()
    js_path = os.path.join(base_dir, 'static', 'game_v8.js')
    css_path = os.path.join(base_dir, 'static', 'style_v8.css')
    idx_path = os.path.join(base_dir, 'static', 'index.html')

    # 1. Update static/game_v8.js: 3D vertical upright tilt calculation in renderEnemyFloatingHand
    js_content = open(js_path, encoding='utf-8').read()

    old_floating_func_pattern = r'function renderEnemyFloatingHand\(\)\s*\{[\s\S]*?\n\}'

    new_floating_func = """function renderEnemyFloatingHand() {
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
  const midIndex = (handCount - 1) / 2;
  
  for (let i = 0; i < handCount; i++) {
    const offset = i - midIndex;
    const rotateDeg = (offset * 2.8).toFixed(1);
    
    cardsHTML += `
      <img src="/static/card_back.jpeg" 
           class="floating-enemy-card-back" 
           style="transform: rotateX(25deg) rotate(${rotateDeg}deg); transform-origin: bottom center;" 
           alt="對手手牌牌背">
    `;
  }
  
  container.innerHTML = `
    <div class="floating-enemy-hand-wrap">
      <span class="floating-enemy-count-badge">👾 對手手牌 (${handCount}張)</span>
      <div class="floating-enemy-cards-row">
        ${cardsHTML}
      </div>
    </div>
  `;
}"""

    js_content = re.sub(old_floating_func_pattern, new_floating_func, js_content)
    open(js_path, 'w', encoding='utf-8').write(js_content)
    print("1. Updated game_v8.js with 3D upright vertical tilt successfully!")

    # 2. Update static/style_v8.css: Move phase panel left & title-only, compact 3D vertical enemy hand
    css_content = open(css_path, encoding='utf-8').read()

    # Update #phaseDisplayPanelHard to shift left (right: 85px; top: 38px), hide help text
    old_phase_rule = r'body #phaseDisplayPanelHard,[\s\S]*?z-index: 999999 !important;[\s\S]*?padding: 4px 8px !important;[\s\S]*?}'

    new_phase_rule = """body #phaseDisplayPanelHard,
body.xlw-iphone14-sim-active #phaseDisplayPanelHard,
body.xlw-iphone14-sim-active .game-shell #phaseDisplayPanelHard,
.board #phaseDisplayPanelHard,
#phaseDisplayPanelHard {
  position: absolute !important;
  top: 38px !important;
  right: 85px !important;
  left: auto !important;
  width: auto !important;
  min-width: 120px !important;
  transform: none !important;
  z-index: 999999 !important;
  display: none;
  flex-direction: column !important;
  align-items: center !important;
  padding: 3px 12px !important;
  background: rgba(12, 8, 22, 0.95) !important;
  border: 1.5px solid rgba(255, 215, 106, 0.5) !important;
  border-radius: 20px !important;
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.8) !important;
}
.phase-hard-title { font-size: 12.5px !important; font-weight: bold !important; color: #ffd76a !important; line-height: 1.1 !important; margin: 0 !important; text-shadow: 0 0 8px rgba(255, 215, 106, 0.4) !important; white-space: nowrap !important; }
.phase-hard-help { display: none !important; }"""

    css_content = re.sub(old_phase_rule, new_phase_rule, css_content)

    # Replace floating enemy hand CSS: 3D upright perpendicular to ground (38px x 54px, top: -12px)
    old_floating_hand_css = """/* ===== 頂部中央對手懸浮手牌 (撲克牌攤開、透視微縮 52x72px、貼頂) ===== */
.xlw-enemy-floating-hand {
  position: absolute !important;
  top: 0px !important;
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
  gap: 1px !important;
}

.floating-enemy-count-badge {
  font-size: 9px !important;
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
  align-items: flex-end !important;
  padding-top: 2px !important;
}

.floating-enemy-card-back {
  width: 52px !important;
  height: 72px !important;
  object-fit: cover !important;
  border-radius: 4px !important;
  border: 1px solid rgba(255, 215, 106, 0.5) !important;
  box-shadow: 0 4px 14px rgba(0, 0, 0, 0.8), 0 0 8px rgba(255, 215, 106, 0.2) !important;
  margin-left: -22px !important;
  transition: all 0.2s ease !important;
}

.floating-enemy-card-back:first-child {
  margin-left: 0 !important;
}"""

    new_floating_hand_css = """/* ===== 頂部中央對手懸浮手牌 (3D立體垂直微縮 38x54px, top: -12px 絕不遮擋戰線) ===== */
.xlw-enemy-floating-hand {
  position: absolute !important;
  top: -12px !important;
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
  gap: 1px !important;
}

.floating-enemy-count-badge {
  font-size: 8.5px !important;
  font-weight: bold !important;
  color: #ffd76a !important;
  background: rgba(12, 8, 22, 0.9) !important;
  border: 0.5px solid rgba(255, 215, 106, 0.3) !important;
  border-radius: 10px !important;
  padding: 1px 6px !important;
  white-space: nowrap !important;
}

.floating-enemy-cards-row {
  display: flex !important;
  justify-content: center !important;
  align-items: flex-end !important;
  perspective: 400px !important;
  transform-style: preserve-3d !important;
}

.floating-enemy-card-back {
  width: 38px !important;
  height: 54px !important;
  object-fit: cover !important;
  border-radius: 3px !important;
  border: 1px solid rgba(255, 215, 106, 0.4) !important;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.8) !important;
  margin-left: -16px !important;
  transition: all 0.2s ease !important;
}

.floating-enemy-card-back:first-child {
  margin-left: 0 !important;
}"""

    css_content = css_content.replace(old_floating_hand_css, new_floating_hand_css)
    open(css_path, 'w', encoding='utf-8').write(css_content)
    print("2. Updated style_v8.css phase title-only & 3D upright enemy hand cards successfully!")

    # 3. Update index.html cache-buster
    idx_content = open(idx_path, encoding='utf-8').read()
    idx_content = re.sub(r'game_v8\.js\?v=[^"\']+', 'game_v8.js?v=21.40-vertical-hand-and-phase-title-only', idx_content)
    idx_content = re.sub(r'style_v8\.css\?v=[^"\']+', 'style_v8.css?v=21.40-vertical-hand-and-phase-title-only', idx_content)
    open(idx_content_path := idx_path, 'w', encoding='utf-8').write(idx_content)
    print("3. Updated index.html cache-buster successfully!")

if __name__ == '__main__':
    apply_fixes()
