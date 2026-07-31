# -*- coding: utf-8 -*-
import sys, re

def apply_restyle_and_fan():
    sys.stdout.reconfigure(encoding='utf-8')

    js_path = 'static/game_v8.js'
    css_path = 'static/style_v8.css'
    idx_path = 'static/index.html'

    # 1. Update static/game_v8.js to calculate and apply dynamic poker fan-out inside renderHand
    js_content = open(js_path, encoding='utf-8').read()

    old_render_hand_block = """    if (card.image) {
      cardEl.innerHTML = `<img src="${card.image}" alt="${card.name}"><div class="mini-meta">${card.name}<br>${metaText}</div>`;
    } else {
      cardEl.innerHTML = `<div class="fallback"><b>${card.name}</b><br>${metaText}</div>`;
    }"""

    new_render_hand_block = """    if (card.image) {
      cardEl.innerHTML = `<img src="${card.image}" alt="${card.name}"><div class="mini-meta">${card.name}<br>${metaText}</div>`;
    } else {
      cardEl.innerHTML = `<div class="fallback"><b>${card.name}</b><br>${metaText}</div>`;
    }

    // 動態撲克牌扇形展開效果 (Poker Fan-out)
    const isMobileLandscape = window.matchMedia("(max-width: 1400px) and (orientation: landscape)").matches;
    const rx = isMobileLandscape ? -15 : 0;
    const N = hand.length;
    const mid = (N - 1) / 2;
    const diff = idx - mid;
    const rot = diff * 5; // 每張牌旋轉 5 度
    const ty = Math.abs(diff) * 3; // 兩側牌向下微調 3px 呈圓弧
    const tx = diff * -4; // 微調間距使扇形收納緊湊
    cardEl.style.setProperty("transform", `perspective(300px) translate(${tx}px, ${ty}px) rotate(${rot}deg) rotateX(${rx}deg)`, "important");"""

    js_content = js_content.replace(old_render_hand_block, new_render_hand_block)
    open(js_path, 'w', encoding='utf-8').write(js_content)
    print("1. Programmed dynamic poker card fan-out in game_v8.js successfully!")

    # 2. Update static/style_v8.css: boardWrap translate to -35% and preview panel to position: fixed
    css_content = open(css_path, encoding='utf-8').read()

    # Update transform translate X to -35%
    css_content = css_content.replace(
        "transform: translate(-50%, -50%) scale(0.46) !important;",
        "transform: translate(-35%, -50%) scale(0.46) !important;"
    )

    # Update preview panel from position: absolute to position: fixed
    old_preview_panel = """  .xlw-left-card-panel, #xlwLeftCardPanel {
    position: absolute !important;
    left: 8px !important;
    bottom: 95px !important;
    top: auto !important;
    z-index: 10050 !important;
    transform: scale(0.65) !important;
    transform-origin: bottom left !important;
  }"""

    new_preview_panel = """  .xlw-left-card-panel, #xlwLeftCardPanel {
    position: fixed !important;
    left: 8px !important;
    bottom: 8px !important;
    top: auto !important;
    z-index: 10050 !important;
    transform: scale(0.65) !important;
    transform-origin: bottom left !important;
  }"""

    css_content = css_content.replace(old_preview_panel, new_preview_panel)

    open(css_path, 'w', encoding='utf-8').write(css_content)
    print("2. Updated board position and made preview panel position fixed in style_v8.css successfully!")

    # 3. Update cache-buster in static/index.html to v=18.80-poker-fan-and-centered
    idx_content = open(idx_path, encoding='utf-8').read()
    idx_content = re.sub(r'game_v8\.js\?v=[^"\']+', 'game_v8.js?v=18.80-poker-fan-and-centered', idx_content)
    idx_content = re.sub(r'style_v8\.css\?v=[^"\']+', 'style_v8.css?v=18.80-poker-fan-and-centered', idx_content)
    open(idx_path, 'w', encoding='utf-8').write(idx_content)
    print("3. Updated static/index.html cache-buster successfully!")

if __name__ == '__main__':
    apply_restyle_and_fan()
