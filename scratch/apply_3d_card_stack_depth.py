# -*- coding: utf-8 -*-
import sys, re

def apply_3d_stack_depth():
    sys.stdout.reconfigure(encoding='utf-8')

    # 1. Update static/game_v8.js
    js_path = 'static/game_v8.js'
    js_content = open(js_path, encoding='utf-8').read()

    js_stack_code = """
// ===== 🎴 牌庫與墓地 3D 堆疊卡牌厚度系統 =====
window.xlwRender3DStacks = function() {
  const pDeckEl = document.getElementById("playerDeck");
  const pGraveEl = document.getElementById("playerGraveyard") || document.getElementById("graveyard");
  const eDeckEl = document.getElementById("enemyDeck");
  const eGraveEl = document.getElementById("enemyGraveyard") || document.getElementById("enemyGrave");

  const pDeckCount = (typeof deck !== "undefined" && deck) ? deck.length : 26;
  const pGraveCount = (typeof graveyard !== "undefined" && graveyard) ? graveyard.length : 0;
  const eDeckCount = (window.XLW_ENEMY && window.XLW_ENEMY.deck) ? window.XLW_ENEMY.deck.length : 26;
  const eGraveCount = (window.XLW_ENEMY && window.XLW_ENEMY.grave) ? window.XLW_ENEMY.grave.length : 0;

  const applyDepth = (el, count) => {
    if (!el) return;
    el.classList.remove("xlw-stack-depth-1", "xlw-stack-depth-2", "xlw-stack-depth-3", "xlw-stack-depth-4");
    let depth = 0;
    if (count >= 20) depth = 4;
    else if (count >= 13) depth = 3;
    else if (count >= 6) depth = 2;
    else if (count >= 1) depth = 1;

    if (depth > 0) {
      el.classList.add(`xlw-stack-depth-${depth}`);
    }
  };

  applyDepth(pDeckEl, pDeckCount);
  applyDepth(pGraveEl, pGraveCount);
  applyDepth(eDeckEl, eDeckCount);
  applyDepth(eGraveEl, eGraveCount);
};
"""

    if "window.xlwRender3DStacks" not in js_content:
        js_content += "\n" + js_stack_code

    # Add call to window.xlwRender3DStacks in render()
    if "renderRaceCards();" in js_content:
        js_content = js_content.replace("renderRaceCards();", "renderRaceCards();\n  if (typeof window.xlwRender3DStacks === 'function') window.xlwRender3DStacks();")

    open(js_path, 'w', encoding='utf-8').write(js_content)
    print("1. Updated static/game_v8.js with 3D stack render logic successfully!")

    # 2. Append 3D Stack Thickness CSS to static/style_v8.css
    css_path = 'static/style_v8.css'
    css_content = open(css_path, encoding='utf-8').read()

    stack_css = """

/* ==========================================================================
   3D CARD DECK & GRAVEYARD STACK HEIGHT & THICKNESS SHADOWS
   (雙方牌庫與墓地依卡牌剩餘張數呈現動態 3D 卡牌堆疊厚度與層次光影)
   ========================================================================== */

#playerDeck, #enemyDeck, #playerGraveyard, #enemyGraveyard, #graveyard, #enemyGrave,
.zone.side.dark, .zone.side.purple {
  transition: transform 0.25s cubic-bezier(0.16, 1, 0.3, 1), box-shadow 0.25s ease !important;
  position: relative !important;
}

/* 1 層堆疊厚度 (1~5 張) */
.xlw-stack-depth-1 {
  transform: translateY(-2px) !important;
  box-shadow: 
    1.5px 1.5px 0 #281d38,
    3px 3px 8px rgba(0, 0, 0, 0.75) !important;
}

/* 2 層堆疊厚度 (6~12 張) */
.xlw-stack-depth-2 {
  transform: translateY(-4px) !important;
  box-shadow: 
    1.5px 1.5px 0 #281d38,
    3px 3px 0 #191026,
    5px 5px 12px rgba(0, 0, 0, 0.85) !important;
}

/* 3 層堆疊厚度 (13~19 張) */
.xlw-stack-depth-3 {
  transform: translateY(-6px) !important;
  box-shadow: 
    1.5px 1.5px 0 #281d38,
    3px 3px 0 #191026,
    4.5px 4.5px 0 #0f091a,
    7px 7px 16px rgba(0, 0, 0, 0.9) !important;
}

/* 4 層滿疊厚度 (20+ 張) */
.xlw-stack-depth-4 {
  transform: translateY(-8px) !important;
  box-shadow: 
    1.5px 1.5px 0 rgba(212, 175, 55, 0.8),
    3px 3px 0 #281d38,
    4.5px 4.5px 0 #191026,
    6px 6px 0 #0f091a,
    8px 8px 0 #08040d,
    10px 10px 22px rgba(0, 0, 0, 0.95) !important;
}

"""

    css_content += stack_css
    open(css_path, 'w', encoding='utf-8').write(css_content)
    print("2. Appended 3D stack depth CSS to static/style_v8.css successfully!")

    # Update cache-buster in static/index.html to v=12.40-3d-card-stack-depth
    idx_path = 'static/index.html'
    idx_content = open(idx_path, encoding='utf-8').read()
    idx_content = re.sub(r'game_v8\.js\?v=[^"\']+', 'game_v8.js?v=12.40-3d-card-stack-depth', idx_content)
    idx_content = re.sub(r'style_v8\.css\?v=[^"\']+', 'style_v8.css?v=12.40-3d-card-stack-depth', idx_content)
    open(idx_path, 'w', encoding='utf-8').write(idx_content)
    print("3. Updated static/index.html cache-buster successfully!")

if __name__ == '__main__':
    apply_3d_stack_depth()
