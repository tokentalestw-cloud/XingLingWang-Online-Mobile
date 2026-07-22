# -*- coding: utf-8 -*-
import sys, re

def add_orientation_lock_and_prompt():
    sys.stdout.reconfigure(encoding='utf-8')

    js_path = 'static/game_v8.js'
    css_path = 'static/style_v8.css'
    idx_path = 'static/index.html'

    # 1. Update static/index.html to add rotation overlay
    idx_content = open(idx_path, encoding='utf-8').read()

    overlay_html = """  <!-- 螢幕直向時的轉橫向提示遮罩 (Rotate to Landscape Prompt Overlay) -->
  <div id="xlwOrientationOverlay" class="xlw-orientation-overlay">
    <div class="orientation-box">
      <div class="phone-rotate-icon"></div>
      <h2>📱 請旋轉手機至橫向</h2>
      <p>為了獲得最佳的星靈王對戰體驗，請開啟手機螢幕自動旋轉，並將手機橫放進行遊玩。</p>
    </div>
  </div>"""

    if 'xlwOrientationOverlay' not in idx_content:
        idx_content = idx_content.replace('</body>', f'{overlay_html}\n</body>')

    open(idx_path, 'w', encoding='utf-8').write(idx_content)
    print("1. Added orientation prompt HTML overlay to static/index.html successfully!")

    # 2. Update static/style_v8.css to add overlay and rotating phone animations
    css_content = open(css_path, encoding='utf-8').read()

    # Clean old block if rerun
    block_marker = "/* ==========================================================================\n   ROTATE TO LANDSCAPE PROMPT OVERLAY"
    if block_marker in css_content:
        css_content = css_content[:css_content.find(block_marker)]

    overlay_css = """/* ==========================================================================
   ROTATE TO LANDSCAPE PROMPT OVERLAY (直立螢幕強制旋轉橫屏提示遮罩)
   ========================================================================== */

.xlw-orientation-overlay {
  display: none;
  position: fixed;
  top: 0;
  left: 0;
  width: 100vw;
  height: 100vh;
  background: radial-gradient(circle at 50% 50%, #170d2a 0%, #070509 100%) !important;
  z-index: 99999999 !important;
  align-items: center;
  justify-content: center;
  color: #ffffff !important;
  font-family: "Microsoft JhengHei", "微軟正黑體", sans-serif !important;
  text-align: center !important;
  box-sizing: border-box !important;
}

/* 僅當偵測到小螢幕且處於直向 (Portrait) 狀態時觸發遮罩 */
@media screen and (orientation: portrait) and (max-width: 900px) {
  .xlw-orientation-overlay {
    display: flex !important;
  }
}

.orientation-box {
  max-width: 320px;
  padding: 24px;
  border-radius: 18px;
  border: 1.5px solid rgba(255, 215, 106, 0.4) !important;
  background: rgba(12, 8, 20, 0.95) !important;
  box-shadow: 0 10px 40px rgba(0, 0, 0, 0.8), 0 0 25px rgba(255, 215, 106, 0.1) !important;
  display: flex !important;
  flex-direction: column !important;
  align-items: center !important;
  gap: 16px !important;
}

.orientation-box h2 {
  font-size: 20px !important;
  color: #ffd76a !important;
  margin: 0 !important;
  font-weight: bold !important;
  text-shadow: 0 0 8px rgba(255, 215, 106, 0.3) !important;
}

.orientation-box p {
  font-size: 13.5px !important;
  line-height: 1.6 !important;
  color: #cccccc !important;
  margin: 0 !important;
}

/* 旋轉手機動畫圖示 */
.phone-rotate-icon {
  width: 42px;
  height: 70px;
  border: 3px solid #ffd76a;
  border-radius: 8px;
  position: relative;
  animation: phoneRotateAnim 2s infinite ease-in-out;
  box-shadow: 0 0 15px rgba(255, 215, 106, 0.2);
}

.phone-rotate-icon::before {
  content: "";
  position: absolute;
  width: 10px;
  height: 4px;
  background: #ffd76a;
  bottom: 4px;
  left: 50%;
  transform: translateX(-50%);
  border-radius: 2px;
}

@keyframes phoneRotateAnim {
  0% {
    transform: rotate(0deg);
  }
  50% {
    transform: rotate(-90deg);
  }
  100% {
    transform: rotate(0deg);
  }
}

"""

    css_content += overlay_css
    open(css_path, 'w', encoding='utf-8').write(css_content)
    print("2. Added orientation prompt CSS to static/style_v8.css successfully!")

    # 3. Update static/game_v8.js to programmatically lock screen orientation
    js_content = open(js_path, encoding='utf-8').read()

    # Clean old lock code block if rerun
    block_marker = "// ===== 📱 橫向螢幕鎖定 API 執行引擎 ====="
    if block_marker in js_content:
        js_content = js_content[:js_content.find(block_marker)]

    orientation_js_code = """// ===== 📱 橫向螢幕鎖定 API 執行引擎 =====
window.xlwLockOrientation = function() {
  try {
    if (screen.orientation && typeof screen.orientation.lock === 'function') {
      screen.orientation.lock("landscape").catch(e => {
        console.log("Screen orientation lock rejected by browser security constraint:", e);
      });
    } else if (screen.lockOrientation) {
      screen.lockOrientation("landscape");
    } else if (screen.webkitLockOrientation) {
      screen.webkitLockOrientation("landscape");
    }
  } catch(e) {}
};

document.addEventListener("DOMContentLoaded", () => {
  window.xlwLockOrientation();
  document.body.addEventListener("click", window.xlwLockOrientation, { once: true });
});
"""

    js_content += "\n" + orientation_js_code

    open(js_path, 'w', encoding='utf-8').write(js_content)
    print("3. Injected programmatic orientation lock into static/game_v8.js successfully!")

    # 4. Update cache-buster in static/index.html to v=15.60-orientation-prompt-lock
    idx_content = open(idx_path, encoding='utf-8').read()
    idx_content = re.sub(r'game_v8\.js\?v=[^"\']+', 'game_v8.js?v=15.60-orientation-prompt-lock', idx_content)
    idx_content = re.sub(r'style_v8\.css\?v=[^"\']+', 'style_v8.css?v=15.60-orientation-prompt-lock', idx_content)
    open(idx_path, 'w', encoding='utf-8').write(idx_content)
    print("4. Updated static/index.html cache-buster successfully!")

if __name__ == '__main__':
    add_orientation_lock_and_prompt()
