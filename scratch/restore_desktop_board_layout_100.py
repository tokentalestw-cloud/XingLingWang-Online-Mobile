# -*- coding: utf-8 -*-
import sys, re

def restore_desktop_layout():
    sys.stdout.reconfigure(encoding='utf-8')

    # 1. Restore static/index.html HTML structure by removing wrapper divs
    idx_path = 'static/index.html'
    idx_content = open(idx_path, encoding='utf-8').read()

    # Remove wrapper tags
    idx_content = idx_content.replace(
        '<div id="xlwIphone14Frame" class="xlw-iphone14-frame-wrapper">\n    <div class="iphone14-device-bezel">\n      <div class="iphone14-notch"></div>\n      <div class="iphone14-home-bar"></div>\n      <div class="game-shell">',
        '<div class="game-shell">'
    )
    idx_content = idx_content.replace(
        '</aside>\n    </div><!-- /.iphone14-device-bezel -->\n  </div><!-- /#xlwIphone14Frame -->',
        '</aside>'
    )

    # Update cache-buster to v=13.70-restore-desktop-board-layout
    idx_content = re.sub(r'game_v8\.js\?v=[^"\']+', 'game_v8.js?v=13.70-restore-desktop-board-layout', idx_content)
    idx_content = re.sub(r'style_v8\.css\?v=[^"\']+', 'style_v8.css?v=13.70-restore-desktop-board-layout', idx_content)

    open(idx_path, 'w', encoding='utf-8').write(idx_content)
    print("1. Restored static/index.html HTML hierarchy to 100% original state successfully!")

    # 2. Update static/game_v8.js simulator toggle state to add/remove body class
    js_path = 'static/game_v8.js'
    js_content = open(js_path, encoding='utf-8').read()

    js_sim_code_clean = """
// ===== 📱 iPhone 14 橫向擬真螢幕模擬器 (844px x 390px - Zero DOM interference) =====
window.xlwIphone14SimActive = localStorage.getItem('xlw_iphone14_sim') === 'true';

window.xlwToggleIphone14Sim = function() {
  window.xlwIphone14SimActive = !window.xlwIphone14SimActive;
  localStorage.setItem('xlw_iphone14_sim', window.xlwIphone14SimActive ? 'true' : 'false');
  window.xlwApplyIphone14SimState();
};

window.xlwApplyIphone14SimState = function() {
  const btn = document.getElementById("xlwIphone14SimBtn");

  if (window.xlwIphone14SimActive) {
    document.body.classList.add("xlw-iphone14-sim-active");
    if (btn) btn.innerHTML = "📱 關閉 iPhone 模擬";
  } else {
    document.body.classList.remove("xlw-iphone14-sim-active");
    if (btn) btn.innerHTML = "📱 iPhone 14 模擬";
  }
};

document.addEventListener("DOMContentLoaded", () => {
  setTimeout(() => {
    if (typeof window.xlwApplyIphone14SimState === 'function') window.xlwApplyIphone14SimState();
  }, 100);
});
"""

    if "window.xlwToggleIphone14Sim" in js_content:
        block_start = js_content.find("// ===== 📱 iPhone 14 橫向擬真螢幕模擬器")
        if block_start >= 0:
            js_content = js_content[:block_start] + js_sim_code_clean
        else:
            js_content += "\n" + js_sim_code_clean

    open(js_path, 'w', encoding='utf-8').write(js_content)
    print("2. Updated static/game_v8.js with clean body class toggle logic successfully!")

    # 3. Clean CSS in static/style_v8.css
    css_path = 'static/style_v8.css'
    css_content = open(css_path, encoding='utf-8').read()

    # Clean old simulator block
    block_marker = "/* ==========================================================================\n   IPHONE 14 LANDSCAPE DEVICE SIMULATOR"
    if block_marker in css_content:
        css_content = css_content[:css_content.find(block_marker)]

    clean_sim_css = """/* ==========================================================================
   IPHONE 14 LANDSCAPE SIMULATOR (純 CSS body 類別切換，零電腦版排版干擾)
   ========================================================================== */

body.xlw-iphone14-sim-active {
  background: radial-gradient(circle at 50% 50%, #1c152a 0%, #07050a 100%) !important;
  display: flex !important;
  flex-direction: column !important;
  align-items: center !important;
}

body.xlw-iphone14-sim-active .game-shell {
  width: 844px !important;
  height: 390px !important;
  margin: 30px auto !important;
  border-radius: 44px !important;
  border: 12px solid #1c1c1e !important;
  outline: 2px solid #2c2c2e !important;
  box-shadow: 
    0 25px 70px rgba(0, 0, 0, 0.95),
    0 0 35px rgba(255, 215, 106, 0.3) !important;
  overflow: hidden !important;
  position: relative !important;
}

"""

    css_content += clean_sim_css
    open(css_path, 'w', encoding='utf-8').write(css_content)
    print("3. Updated static/style_v8.css with clean body.xlw-iphone14-sim-active CSS successfully!")

if __name__ == '__main__':
    restore_desktop_layout()
