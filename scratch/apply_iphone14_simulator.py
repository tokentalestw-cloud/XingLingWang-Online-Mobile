# -*- coding: utf-8 -*-
import sys, re

def apply_iphone14_simulator():
    sys.stdout.reconfigure(encoding='utf-8')

    # 1. Update static/index.html to add iPhone 14 simulator toggle button and container wrappers
    idx_path = 'static/index.html'
    idx_content = open(idx_path, encoding='utf-8').read()

    sim_btn_html = '<button id="xlwIphone14SimBtn" class="topbar-setting-btn" onclick="window.xlwToggleIphone14Sim()" style="border-color: #ffd76a; color: #ffe600;">📱 iPhone 14 模擬</button>'
    if 'xlwIphone14SimBtn' not in idx_content:
        idx_content = idx_content.replace('<button id="xlwSfxToggleBtn"', f'{sim_btn_html}\n      <button id="xlwSfxToggleBtn"')

    # Wrap main board content inside iPhone 14 Frame wrapper if not wrapped
    if '<div id="xlwIphone14Frame" class="xlw-iphone14-frame-wrapper">' not in idx_content:
        idx_content = idx_content.replace(
            '<div class="game-shell">',
            '<div id="xlwIphone14Frame" class="xlw-iphone14-frame-wrapper">\n    <div class="iphone14-device-bezel">\n      <div class="iphone14-notch"></div>\n      <div class="iphone14-home-bar"></div>\n      <div class="game-shell">'
        )
        idx_content = idx_content.replace(
            '</aside>\n        \n        <!-- 對手功能區域 (左側) -->',
            '</aside>\n    </div><!-- /.iphone14-device-bezel -->\n  </div><!-- /#xlwIphone14Frame -->\n        \n        <!-- 對手功能區域 (左側) -->'
        )

    # Update cache-buster to v=13.60-iphone14-landscape-simulator
    idx_content = re.sub(r'game_v8\.js\?v=[^"\']+', 'game_v8.js?v=13.60-iphone14-landscape-simulator', idx_content)
    idx_content = re.sub(r'style_v8\.css\?v=[^"\']+', 'style_v8.css?v=13.60-iphone14-landscape-simulator', idx_content)

    open(idx_path, 'w', encoding='utf-8').write(idx_content)
    print("1. Updated static/index.html with iPhone 14 simulator button & device wrappers successfully!")

    # 2. Update static/game_v8.js with toggle function
    js_path = 'static/game_v8.js'
    js_content = open(js_path, encoding='utf-8').read()

    js_sim_code = """
// ===== 📱 iPhone 14 橫向擬真螢幕模擬器 (844px x 390px) =====
window.xlwIphone14SimActive = localStorage.getItem('xlw_iphone14_sim') === 'true';

window.xlwToggleIphone14Sim = function() {
  window.xlwIphone14SimActive = !window.xlwIphone14SimActive;
  localStorage.setItem('xlw_iphone14_sim', window.xlwIphone14SimActive ? 'true' : 'false');
  window.xlwApplyIphone14SimState();
};

window.xlwApplyIphone14SimState = function() {
  const frame = document.getElementById("xlwIphone14Frame");
  const btn = document.getElementById("xlwIphone14SimBtn");
  if (!frame) return;

  if (window.xlwIphone14SimActive) {
    frame.classList.add("sim-active");
    if (btn) btn.innerHTML = "📱 關閉 iPhone 模擬";
  } else {
    frame.classList.remove("sim-active");
    if (btn) btn.innerHTML = "📱 iPhone 14 模擬";
  }
};

// Auto apply on load
document.addEventListener("DOMContentLoaded", () => {
  setTimeout(() => {
    if (typeof window.xlwApplyIphone14SimState === 'function') window.xlwApplyIphone14SimState();
  }, 100);
});
"""

    if "window.xlwToggleIphone14Sim" not in js_content:
        js_content += "\n" + js_sim_code

    open(js_path, 'w', encoding='utf-8').write(js_content)
    print("2. Updated static/game_v8.js with iPhone 14 simulator toggle state logic successfully!")

    # 3. Append iPhone 14 Frame CSS to static/style_v8.css
    css_path = 'static/style_v8.css'
    css_content = open(css_path, encoding='utf-8').read()

    sim_css = """

/* ==========================================================================
   IPHONE 14 LANDSCAPE DEVICE SIMULATOR (844px x 390px 精準電腦端模擬器)
   ========================================================================== */

.xlw-iphone14-frame-wrapper {
  width: 100%;
  height: 100%;
  display: flex;
  justify-content: center;
  align-items: center;
  transition: all 0.35s cubic-bezier(0.16, 1, 0.3, 1);
}

.xlw-iphone14-frame-wrapper.sim-active {
  padding: 40px 0;
  background: radial-gradient(circle at 50% 50%, #1a1426 0%, #07050a 100%) !important;
}

.xlw-iphone14-frame-wrapper.sim-active .iphone14-device-bezel {
  width: 844px !important;
  height: 390px !important;
  position: relative !important;
  border-radius: 44px !important;
  background: #000000 !important;
  border: 12px solid #1c1c1e !important;
  outline: 2px solid #2c2c2e !important;
  box-shadow: 
    0 25px 70px rgba(0, 0, 0, 0.95),
    0 0 35px rgba(255, 215, 106, 0.25) !important;
  overflow: hidden !important;
  flex-shrink: 0 !important;
}

/* iPhone 14 瀏海/動態島指示器 */
.iphone14-device-bezel .iphone14-notch {
  display: none;
}

.sim-active .iphone14-device-bezel .iphone14-notch {
  display: block !important;
  position: absolute !important;
  left: 0 !important;
  top: 50% !important;
  transform: translateY(-50%) !important;
  width: 24px !important;
  height: 120px !important;
  background: #000000 !important;
  border-radius: 0 16px 16px 0 !important;
  z-index: 999999 !important;
}

/* iOS Home Bar 底部指示條 */
.iphone14-device-bezel .iphone14-home-bar {
  display: none;
}

.sim-active .iphone14-device-bezel .iphone14-home-bar {
  display: block !important;
  position: absolute !important;
  bottom: 8px !important;
  left: 50% !important;
  transform: translateX(-50%) !important;
  width: 140px !important;
  height: 4.5px !important;
  background: rgba(255, 255, 255, 0.6) !important;
  border-radius: 4px !important;
  z-index: 999999 !important;
}

.sim-active .game-shell {
  width: 100% !important;
  height: 100% !important;
  border-radius: 32px !important;
  overflow: hidden !important;
}

"""

    css_content += sim_css
    open(css_path, 'w', encoding='utf-8').write(css_content)
    print("3. Appended iPhone 14 Device Frame CSS to static/style_v8.css successfully!")

if __name__ == '__main__':
    apply_iphone14_simulator()
