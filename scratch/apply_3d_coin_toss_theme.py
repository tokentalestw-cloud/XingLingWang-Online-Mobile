# -*- coding: utf-8 -*-
import sys, re

def apply_coin_toss_3d():
    sys.stdout.reconfigure(encoding='utf-8')

    # 1. Update getOrCreateCoinTossOverlay HTML in static/game_v8.js
    js_path = 'static/game_v8.js'
    js_content = open(js_path, encoding='utf-8').read()

    old_overlay_code = """function getOrCreateCoinTossOverlay() {
  let overlay = document.getElementById("xlw-coin-toss-overlay");
  if (!overlay) {
    overlay = document.createElement("div");
    overlay.id = "xlw-coin-toss-overlay";
    overlay.className = "xlw-chain-overlay";
    overlay.style.cssText = `
      position: fixed;
      inset: 0;
      background: rgba(8, 6, 16, 0.9);
      display: none;
      align-items: center;
      justify-content: center;
      z-index: 1000000;
      backdrop-filter: blur(10px);
    `;
    overlay.innerHTML = `
      <div class="confirm-box" style="background: linear-gradient(135deg, #181414 0%, #0d0a0a 100%); border: 2px solid var(--gold-accent); border-radius: 16px; width: 420px; padding: 30px; text-align: center; box-shadow: 0 12px 50px rgba(0, 0, 0, 0.95), 0 0 25px rgba(205, 170, 82, 0.35); font-family: 'Outfit', sans-serif;">
        <h2 style="color: #ffd76a; font-family: 'Cinzel', serif; margin-top: 0; margin-bottom: 15px; font-size: 24px; text-shadow: 0 0 10px rgba(255,215,106,0.3);">🪙 命運硬幣投擲 🪙</h2>
        <div id="xlw-coin-graphic" style="font-size: 90px; margin: 25px 0; transition: transform 0.8s ease-in-out; display: inline-block;">🪙</div>
        <p id="xlw-coin-toss-status" style="color: #fff; font-size: 15px; margin-bottom: 25px; line-height: 1.6; font-weight: bold; min-height: 48px;"></p>
        <div id="xlw-coin-toss-actions" style="display: flex; gap: 15px; justify-content: center; align-items: center;"></div>
      </div>
    `;
    document.body.appendChild(overlay);
  }
  return overlay;
}"""

    new_overlay_code = """function getOrCreateCoinTossOverlay() {
  let overlay = document.getElementById("xlw-coin-toss-overlay");
  if (!overlay) {
    overlay = document.createElement("div");
    overlay.id = "xlw-coin-toss-overlay";
    overlay.className = "xlw-chain-overlay";
    overlay.style.cssText = `
      position: fixed;
      inset: 0;
      background: rgba(8, 6, 16, 0.92);
      display: none;
      align-items: center;
      justify-content: center;
      z-index: 1000000;
      backdrop-filter: blur(14px);
    `;
    overlay.innerHTML = `
      <div class="confirm-box xlw-coin-toss-box">
        <h2 class="xlw-coin-toss-title">🪙 命運硬幣投擲 🪙</h2>
        <div id="xlw-coin-graphic" class="xlw-coin-graphic">🪙</div>
        <div id="xlw-coin-toss-status" class="xlw-coin-toss-status-bar"></div>
        <div id="xlw-coin-toss-actions" class="xlw-coin-toss-actions-row"></div>
      </div>
    `;
    document.body.appendChild(overlay);
  }
  return overlay;
}"""

    if "function getOrCreateCoinTossOverlay()" in js_content:
        js_content = re.sub(r'function getOrCreateCoinTossOverlay\(\) \{.*?\n\}', new_overlay_code, js_content, flags=re.DOTALL)
        open(js_path, 'w', encoding='utf-8').write(js_content)
        print("1. Updated getOrCreateCoinTossOverlay in static/game_v8.js with 3D classes successfully!")

    # 2. Append 3D coin toss CSS rules to static/style_v8.css
    css_path = 'static/style_v8.css'
    css_content = open(css_path, encoding='utf-8').read()

    coin_3d_css = """

/* ==========================================================================
   ULTRA 3D FATE COIN TOSS DIALOG & STATUS BAR
   (命運硬幣投擲對話框、3D 金屬狀態列與立體按鈕全套重構)
   ========================================================================== */

.xlw-coin-toss-box {
  background: radial-gradient(circle at 50% 20%, rgba(255, 215, 0, 0.22) 0%, transparent 75%), linear-gradient(180deg, rgba(38, 28, 48, 0.98) 0%, rgba(14, 10, 20, 0.99) 100%) !important;
  border: 2.5px solid #ffe600 !important;
  border-bottom: 6px solid #8c6d00 !important;
  border-radius: 22px !important;
  width: 440px !important;
  padding: 28px !important;
  text-align: center !important;
  box-shadow: inset 0 2.5px 5px rgba(255, 255, 255, 0.65), inset 0 -5px 12px rgba(0, 0, 0, 0.7), 0 20px 50px rgba(0, 0, 0, 0.95), 0 0 35px rgba(255, 230, 0, 0.5) !important;
  box-sizing: border-box !important;
}

.xlw-coin-toss-title {
  color: #ffe600 !important;
  font-family: 'Cinzel', serif !important;
  margin-top: 0 !important;
  margin-bottom: 18px !important;
  font-size: 24px !important;
  font-weight: 900 !important;
  text-shadow: 0 0 14px rgba(255, 230, 0, 0.8), 2px 2px 0 #000 !important;
  letter-spacing: 0.8px !important;
}

.xlw-coin-graphic {
  font-size: 90px !important;
  margin: 20px 0 !important;
  transition: transform 0.8s ease-in-out !important;
  display: inline-block !important;
  filter: drop-shadow(0 0 22px rgba(255, 230, 0, 0.85)) drop-shadow(0 10px 18px rgba(0,0,0,0.9)) !important;
}

.xlw-coin-toss-status-bar {
  background: linear-gradient(180deg, rgba(255,255,255,0.18) 0%, rgba(0,0,0,0.6) 100%) !important;
  border: 1.5px solid rgba(255, 230, 100, 0.8) !important;
  border-bottom: 4px solid #7a6000 !important;
  border-radius: 14px !important;
  padding: 14px 18px !important;
  color: #fff6c2 !important;
  font-weight: 900 !important;
  font-size: 15px !important;
  line-height: 1.6 !important;
  margin-bottom: 25px !important;
  min-height: 52px !important;
  text-shadow: 1px 1px 2px #000, 0 0 8px rgba(255, 230, 0, 0.4) !important;
  box-shadow: inset 0 2px 3px rgba(255, 255, 255, 0.5), 0 6px 16px rgba(0, 0, 0, 0.7) !important;
  display: flex !important;
  align-items: center !important;
  justify-content: center !important;
  box-sizing: border-box !important;
}

.xlw-coin-toss-actions-row {
  display: flex !important;
  gap: 15px !important;
  justify-content: center !important;
  align-items: center !important;
}

.xlw-coin-toss-actions-row button {
  background: linear-gradient(180deg, rgba(255,255,255,0.35) 0%, rgba(255,255,255,0) 45%), linear-gradient(180deg, #fff7a0 0%, #ffd700 45%, #c99c00 100%) !important;
  color: #000000 !important;
  border: 1.5px solid rgba(255, 235, 120, 0.9) !important;
  border-radius: 14px !important;
  font-weight: 900 !important;
  font-size: 14px !important;
  padding: 10px 24px !important;
  min-width: 150px !important;
  cursor: pointer !important;
  box-shadow: inset 0 2px 3px rgba(255, 255, 255, 0.7), inset 0 -3px 6px rgba(0, 0, 0, 0.35), 0 8px 20px rgba(0, 0, 0, 0.7), 0 0 16px rgba(255, 215, 0, 0.4) !important;
  text-shadow: 0 1px 0 rgba(255, 255, 255, 0.5) !important;
  transition: transform 0.12s ease, box-shadow 0.12s ease !important;
}

.xlw-coin-toss-actions-row button:hover:not(:disabled) {
  transform: translateY(-2.5px) !important;
  border-color: #ffffff !important;
  background: linear-gradient(180deg, rgba(255,255,255,0.45) 0%, rgba(255,255,255,0) 45%), linear-gradient(180deg, #ffffb3 0%, #ffe033 45%, #e6aa00 100%) !important;
  box-shadow: inset 0 2.5px 4px rgba(255, 255, 255, 0.85), inset 0 -3px 6px rgba(0, 0, 0, 0.35), 0 10px 24px rgba(0, 0, 0, 0.8), 0 0 22px rgba(255, 230, 0, 0.65) !important;
}

.xlw-coin-toss-actions-row button:active:not(:disabled) {
  transform: translateY(2px) !important;
  box-shadow: inset 0 3px 6px rgba(0, 0, 0, 0.6) !important;
}

"""

    css_content += coin_3d_css
    open(css_path, 'w', encoding='utf-8').write(css_content)
    print("2. Appended ultra 3D coin toss CSS to static/style_v8.css successfully!")

    # Update cache-buster in static/index.html to v=10.60-3d-coin-toss-theme
    idx_path = 'static/index.html'
    idx_content = open(idx_path, encoding='utf-8').read()
    idx_content = re.sub(r'game_v8\.js\?v=[^"\']+', 'game_v8.js?v=10.60-3d-coin-toss-theme', idx_content)
    idx_content = re.sub(r'style_v8\.css\?v=[^"\']+', 'style_v8.css?v=10.60-3d-coin-toss-theme', idx_content)
    open(idx_path, 'w', encoding='utf-8').write(idx_content)
    print("3. Updated static/index.html cache-buster successfully!")

if __name__ == '__main__':
    apply_coin_toss_3d()
