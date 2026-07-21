# -*- coding: utf-8 -*-
import sys, re

def add_fullscreen_trigger():
    sys.stdout.reconfigure(encoding='utf-8')

    # 1. Update static/game_v8.js with Fullscreen API helper & listener
    js_path = 'static/game_v8.js'
    js_content = open(js_path, encoding='utf-8').read()

    fs_js_code = """
// ===== 📱 手機一鍵切換全螢幕與 iOS PWA 啟動引擎 =====
window.xlwRequestFullScreen = function() {
  const docEl = document.documentElement;
  try {
    if (docEl.requestFullscreen) {
      docEl.requestFullscreen().catch(e => {});
    } else if (docEl.webkitRequestFullscreen) {
      docEl.webkitRequestFullscreen();
    } else if (docEl.mozRequestFullScreen) {
      docEl.mozRequestFullScreen();
    } else if (docEl.msRequestFullscreen) {
      docEl.msRequestFullscreen();
    }
  } catch(e) {}

  const banner = document.getElementById("xlwMobileFsBanner");
  if (banner) banner.style.display = "none";
};

// Check if running in standalone PWA mode
window.xlwCheckStandalone = function() {
  const isStandalone = window.navigator.standalone || window.matchMedia('(display-mode: standalone)').matches;
  const banner = document.getElementById("xlwMobileFsBanner");
  if (isStandalone && banner) {
    banner.style.display = "none";
  }
};

document.addEventListener("DOMContentLoaded", () => {
  setTimeout(() => {
    if (typeof window.xlwCheckStandalone === 'function') window.xlwCheckStandalone();
  }, 200);
});
"""

    if "window.xlwRequestFullScreen" not in js_content:
        js_content += "\n" + fs_js_code

    open(js_path, 'w', encoding='utf-8').write(js_content)
    print("1. Injected Fullscreen API helper into static/game_v8.js successfully!")

    # 2. Add Mobile Fullscreen Banner to static/index.html
    idx_path = 'static/index.html'
    idx_content = open(idx_path, encoding='utf-8').read()

    fs_banner_html = """  <!-- 手機瀏覽器點擊全螢幕提示橫條 (Tap to Fullscreen Banner) -->
  <div id="xlwMobileFsBanner" class="xlw-mobile-fs-banner" onclick="window.xlwRequestFullScreen()">
    <span>📱 <b>點擊此處開啟手機全螢幕對戰</b>（或點擊 Safari 下方「分享 ➔ 加入主畫面」獲得 100% 滿版體驗）</span>
    <button class="fs-btn">進入全螢幕 ⛶</button>
  </div>"""

    if 'xlwMobileFsBanner' not in idx_content:
        idx_content = idx_content.replace('</body>', f'{fs_banner_html}\n</body>')

    # Update cache-buster to v=15.00-mobile-tap-fullscreen-trigger
    idx_content = re.sub(r'game_v8\.js\?v=[^"\']+', 'game_v8.js?v=15.00-mobile-tap-fullscreen-trigger', idx_content)
    idx_content = re.sub(r'style_v8\.css\?v=[^"\']+', 'style_v8.css?v=15.00-mobile-tap-fullscreen-trigger', idx_content)

    open(idx_path, 'w', encoding='utf-8').write(idx_content)
    print("2. Added Mobile Fullscreen Banner to static/index.html successfully!")

    # 3. Append Mobile Fullscreen Banner CSS to static/style_v8.css
    css_path = 'static/style_v8.css'
    css_content = open(css_path, encoding='utf-8').read()

    fs_css = """

/* ==========================================================================
   MOBILE TAP TO FULLSCREEN BANNER (手機瀏覽器點擊全螢幕橫條)
   ========================================================================== */

.xlw-mobile-fs-banner {
  display: none;
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 42px;
  background: linear-gradient(90deg, #2b1f0d 0%, #d4af37 50%, #2b1f0d 100%);
  color: #070505;
  font-weight: 900;
  font-size: 13px;
  align-items: center;
  justify-content: space-between;
  padding: 0 16px;
  z-index: 9999999;
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.7);
  cursor: pointer;
  box-sizing: border-box;
}

@media (max-width: 900px) {
  .xlw-mobile-fs-banner {
    display: flex !important;
  }
}

.xlw-mobile-fs-banner .fs-btn {
  background: #070505;
  color: #ffe600;
  border: 1px solid #ffe600;
  border-radius: 6px;
  padding: 4px 10px;
  font-size: 12px;
  font-weight: bold;
  cursor: pointer;
  white-space: nowrap;
}

"""

    css_content += fs_css
    open(css_path, 'w', encoding='utf-8').write(css_content)
    print("3. Appended Mobile Fullscreen Banner CSS to static/style_v8.css successfully!")

if __name__ == '__main__':
    add_fullscreen_trigger()
