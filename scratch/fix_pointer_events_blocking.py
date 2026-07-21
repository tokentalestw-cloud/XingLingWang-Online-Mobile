# -*- coding: utf-8 -*-
import sys, re

def fix_pointer_events():
    sys.stdout.reconfigure(encoding='utf-8')
    js_path = 'static/game_v8.js'
    js_content = open(js_path, encoding='utf-8').read()

    new_spell_overlay_code = """function xlwShowSpellActivationOverlay(card, side) {
  return new Promise((resolve) => {
    let overlay = document.getElementById("xlw-spell-activation-overlay");
    if (!overlay) {
      overlay = document.createElement("div");
      overlay.id = "xlw-spell-activation-overlay";
      overlay.className = "xlw-spell-activation-overlay";
      document.body.appendChild(overlay);
    }

    // 保底強制 Fixed 全螢幕居中樣式
    overlay.style.position = "fixed";
    overlay.style.top = "0";
    overlay.style.left = "0";
    overlay.style.width = "100vw";
    overlay.style.height = "100vh";
    overlay.style.background = "rgba(0, 0, 0, 0.75)";
    overlay.style.display = "flex";
    overlay.style.flexDirection = "column";
    overlay.style.alignItems = "center";
    overlay.style.justifyContent = "center";
    overlay.style.zIndex = "99999";
    overlay.style.pointerEvents = "none";
    overlay.style.opacity = "0";
    overlay.style.transition = "opacity 0.25s ease, transform 0.25s cubic-bezier(0.175, 0.885, 0.32, 1.275)";
    overlay.style.transform = "scale(0.85)";

    const isPlayer = side === "player" || side === "me" || side === "player_front" || side === "player_back";
    const titleText = isPlayer ? "✨ 我方發動魔法卡！ ✨" : "✨ 對手發動魔法卡！ ✨";
    const titleColor = isPlayer ? "#00ff7f" : "#ff4d4f";

    overlay.innerHTML = `
      <div class="xlw-spell-activation-title" style="color: ${titleColor}; font-size: 24px; font-weight: 900; margin-bottom: 12px; text-shadow: 0 0 10px ${titleColor}, 2px 2px 0 #000;">${titleText}</div>
      <div class="xlw-spell-activation-card-box" style="background: rgba(18, 12, 16, 0.95); border: 2.5px solid #ffe600; border-radius: 14px; padding: 14px; box-shadow: 0 10px 40px rgba(0,0,0,0.95), 0 0 20px rgba(255, 230, 0, 0.4); display: flex; flex-direction: column; align-items: center; max-width: 280px; text-align: center;">
        <img class="xlw-spell-activation-card-img" src="${card.image || "/static/card_back.jpeg"}" alt="${card.name}" style="width: 170px; height: 240px; object-fit: fill; border-radius: 8px; border: 2px solid #ffffff; box-shadow: 0 4px 12px rgba(0,0,0,0.8); margin-bottom: 10px;">
        <div class="xlw-spell-activation-card-name" style="font-size: 18px; font-weight: 900; color: #ffe600; text-shadow: 1px 1px 0 #000; margin-bottom: 4px;">${card.name}</div>
        <div class="xlw-spell-activation-card-effect" style="font-size: 12px; color: #e0e0e0; line-height: 1.4;">${card.effect_text || ""}</div>
      </div>
    `;

    requestAnimationFrame(() => {
      overlay.style.opacity = "1";
      overlay.style.pointerEvents = "none"; // 不攔截任何滑鼠點擊
      overlay.style.transform = "scale(1)";
    });

    setTimeout(() => {
      overlay.style.opacity = "0";
      overlay.style.pointerEvents = "none";
      overlay.style.transform = "scale(0.85)";
      setTimeout(() => {
        if (overlay && overlay.parentNode) overlay.remove();
        resolve();
      }, 250);
    }, 1500);
  });
}

function xlwShowTributeSummonOverlay(card, side) {
  return new Promise((resolve) => {
    let overlay = document.getElementById("xlw-tribute-activation-overlay");
    if (!overlay) {
      overlay = document.createElement("div");
      overlay.id = "xlw-tribute-activation-overlay";
      overlay.className = "xlw-tribute-activation-overlay";
      document.body.appendChild(overlay);
    }

    overlay.style.position = "fixed";
    overlay.style.top = "0";
    overlay.style.left = "0";
    overlay.style.width = "100vw";
    overlay.style.height = "100vh";
    overlay.style.background = "rgba(0, 0, 0, 0.75)";
    overlay.style.display = "flex";
    overlay.style.flexDirection = "column";
    overlay.style.alignItems = "center";
    overlay.style.justifyContent = "center";
    overlay.style.zIndex = "99999";
    overlay.style.pointerEvents = "none";
    overlay.style.opacity = "0";
    overlay.style.transition = "opacity 0.25s ease, transform 0.25s cubic-bezier(0.175, 0.885, 0.32, 1.275)";
    overlay.style.transform = "scale(0.85)";

    const isPlayer = side === "player" || side === "me" || side === "player_front" || side === "player_back";
    const titleText = "🌟 獻祭召喚 🌟";
    const subtitleText = isPlayer ? "我方強大星靈降臨！" : "對手強大星靈降臨！";
    const subtitleColor = isPlayer ? "#00ff7f" : "#ff4d4f";

    const atk = card.atk ?? card.attack ?? 0;
    const stars = card.stars ?? card.score ?? 0;
    const race = card.race || card.faction || "一般";

    overlay.innerHTML = `
      <div class="xlw-tribute-activation-title-container" style="text-align: center; margin-bottom: 12px;">
        <div class="xlw-tribute-activation-title" style="font-size: 24px; font-weight: 900; color: #ffe600; text-shadow: 0 0 10px #ffe600, 2px 2px 0 #000;">${titleText}</div>
        <div class="xlw-tribute-activation-subtitle" style="color: ${subtitleColor}; font-size: 14px; font-weight: bold;">${subtitleText}</div>
      </div>
      <div class="xlw-tribute-activation-card-box" style="background: rgba(18, 12, 16, 0.95); border: 2.5px solid #ffe600; border-radius: 14px; padding: 14px; box-shadow: 0 10px 40px rgba(0,0,0,0.95), 0 0 20px rgba(255, 230, 0, 0.4); display: flex; flex-direction: column; align-items: center; max-width: 280px; text-align: center;">
        <img class="xlw-tribute-activation-card-img" src="${card.image || "/static/card_back.jpeg"}" alt="${card.name}" style="width: 170px; height: 240px; object-fit: fill; border-radius: 8px; border: 2px solid #ffffff; box-shadow: 0 4px 12px rgba(0,0,0,0.8); margin-bottom: 10px;">
        <div class="xlw-tribute-activation-card-name" style="font-size: 18px; font-weight: 900; color: #ffe600; text-shadow: 1px 1px 0 #000; margin-bottom: 4px;">${card.name}</div>
        <div class="xlw-tribute-activation-card-stats" style="display: flex; gap: 6px; margin-bottom: 8px;">
          <div class="xlw-tribute-activation-stat-badge" style="background: #000; color: #ffe600; border: 1px solid #ffe600; border-radius: 4px; padding: 2px 6px; font-size: 11px; font-weight: bold;">⭐ ${stars}星</div>
          <div class="xlw-tribute-activation-stat-badge" style="background: #000; color: #ffe600; border: 1px solid #ffe600; border-radius: 4px; padding: 2px 6px; font-size: 11px; font-weight: bold;">⚔️ ${atk}</div>
          <div class="xlw-tribute-activation-stat-badge" style="background: #000; color: #ffe600; border: 1px solid #ffe600; border-radius: 4px; padding: 2px 6px; font-size: 11px; font-weight: bold;">👥 ${race}</div>
        </div>
        <div class="xlw-tribute-activation-card-effect" style="font-size: 12px; color: #e0e0e0; line-height: 1.4;">${card.effect_text || "無特殊效果"}</div>
      </div>
    `;

    requestAnimationFrame(() => {
      overlay.style.opacity = "1";
      overlay.style.pointerEvents = "none";
      overlay.style.transform = "scale(1)";
    });

    setTimeout(() => {
      overlay.style.opacity = "0";
      overlay.style.pointerEvents = "none";
      overlay.style.transform = "scale(0.85)";
      setTimeout(() => {
        if (overlay && overlay.parentNode) overlay.remove();
        resolve();
      }, 250);
    }, 1500);
  });
}"""

    o_start = js_content.find("function xlwShowSpellActivationOverlay(card, side) {")
    o_end = js_content.find("function showSpellChainUI(stack) {")

    if o_start >= 0 and o_end >= 0:
        js_content = js_content[:o_start] + new_spell_overlay_code + "\n\n" + js_content[o_end:]
        open(js_path, 'w', encoding='utf-8').write(js_content)
        print("1. Updated xlwShowSpellActivationOverlay & xlwShowTributeSummonOverlay in static/game_v8.js with pointerEvents = 'none'!")

    # 2. Update style_v8.css to ensure pointer-events: none !important on overlays
    css_path = 'static/style_v8.css'
    css_content = open(css_path, encoding='utf-8').read()

    new_overlay_css = """

/* ==========================================================================
   SPELL & TRIBUTE OVERLAY POINTER EVENTS UNBLOCK
   ========================================================================== */

.xlw-spell-activation-overlay,
.xlw-tribute-activation-overlay {
  pointer-events: none !important;
}

"""

    css_content += new_overlay_css
    open(css_path, 'w', encoding='utf-8').write(css_content)

    # Update cache-buster in static/index.html to v=10.00-unblock-pointer-events
    idx_path = 'static/index.html'
    idx_content = open(idx_path, encoding='utf-8').read()
    idx_content = re.sub(r'game_v8\.js\?v=[^"\']+', 'game_v8.js?v=10.00-unblock-pointer-events', idx_content)
    idx_content = re.sub(r'style_v8\.css\?v=[^"\']+', 'style_v8.css?v=10.00-unblock-pointer-events', idx_content)
    open(idx_path, 'w', encoding='utf-8').write(idx_content)
    print("2. Updated static/index.html cache-buster successfully!")

if __name__ == '__main__':
    fix_pointer_events()
