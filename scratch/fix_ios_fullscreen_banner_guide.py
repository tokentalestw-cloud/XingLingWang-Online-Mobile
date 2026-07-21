# -*- coding: utf-8 -*-
import sys, re

def fix_ios_banner_guide():
    sys.stdout.reconfigure(encoding='utf-8')

    js_path = 'static/game_v8.js'
    js_content = open(js_path, encoding='utf-8').read()

    # Clean old fullscreen block
    block_marker = "// ===== 📱 手機一鍵切換全螢幕與 iOS PWA 啟動引擎 ====="
    if block_marker in js_content:
        js_content = js_content[:js_content.find(block_marker)]

    ios_banner_js = """// ===== 📱 手機一鍵切換全螢幕與 iOS PWA 啟動引擎 =====
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

window.xlwCheckStandalone = function() {
  const isStandalone = window.navigator.standalone || window.matchMedia('(display-mode: standalone)').matches;
  const isIOS = /iPad|iPhone|iPod/.test(navigator.userAgent) && !window.MSStream;
  const banner = document.getElementById("xlwMobileFsBanner");
  
  if (banner) {
    if (isStandalone) {
      banner.style.display = "none";
    } else if (isIOS) {
      // iPhone Safari does not support requestFullscreen on standard HTML elements.
      // Dynamically display PWA installation guide on the banner to avoid non-functional clicks.
      banner.innerHTML = `<span>💡 <b>iPhone 滿版提示：</b>點擊 Safari 下方「<b>分享 ➔</b>」按鈕，選擇「<b>加入主畫面</b>」即可開啟全螢幕 App！</span>`;
      banner.removeAttribute("onclick");
      banner.style.background = "linear-gradient(90deg, #1b0d2b 0%, #fa541c 50%, #1b0d2b 100%)";
      banner.style.color = "#ffffff";
      banner.style.justifyContent = "center";
    }
  }
};

document.addEventListener("DOMContentLoaded", () => {
  setTimeout(() => {
    if (typeof window.xlwCheckStandalone === 'function') window.xlwCheckStandalone();
  }, 200);
});
"""

    js_content += "\n" + ios_banner_js
    open(js_path, 'w', encoding='utf-8').write(js_content)
    print("1. Updated static/game_v8.js with iOS detection and PWA instruction banner successfully!")

    # Update cache-buster in static/index.html to v=15.20-ios-pwa-fullscreen-guide
    idx_path = 'static/index.html'
    idx_content = open(idx_path, encoding='utf-8').read()
    idx_content = re.sub(r'game_v8\.js\?v=[^"\']+', 'game_v8.js?v=15.20-ios-pwa-fullscreen-guide', idx_content)
    idx_content = re.sub(r'style_v8\.css\?v=[^"\']+', 'style_v8.css?v=15.20-ios-pwa-fullscreen-guide', idx_content)
    open(idx_path, 'w', encoding='utf-8').write(idx_content)
    print("2. Updated static/index.html cache-buster successfully!")

if __name__ == '__main__':
    fix_ios_banner_guide()
