# -*- coding: utf-8 -*-
import sys, re

def fix_js_scaling_engine():
    sys.stdout.reconfigure(encoding='utf-8')

    js_path = 'static/game_v8.js'
    js_content = open(js_path, encoding='utf-8').read()

    # Define the updated function
    updated_adjust_scale_js = """// 實作動態自適應縮放引擎 (單螢幕無滾動佈局)
function adjustBoardScale() {
  const board = $("boardWrap");
  if (!board) return;

  const isMobile = window.matchMedia("(max-width: 900px), (pointer: coarse)").matches;
  const isPortraitMobile = window.matchMedia("(max-width: 900px) and (orientation: portrait), (pointer: coarse) and (max-width: 900px)").matches;
  const isLandscapeMobile = isMobile && !isPortraitMobile;

  const boardNaturalHeight = isPortraitMobile ? 920 : 940;
  const boardNaturalWidth = isPortraitMobile ? 760 : 980;

  let finalScale;
  if (isMobile) {
    if (isLandscapeMobile) {
      // 📱 橫向手機：改依螢幕高度與寬度取最小值，限制上限 0.38 確保不溢出
      const topbarH = 34;
      const padding = 8;
      const availableHeight = Math.max(300, window.innerHeight - topbarH - padding);
      const scaleH = availableHeight / boardNaturalHeight;
      const scaleW = (window.innerWidth - 130) / boardNaturalWidth;
      finalScale = Math.min(scaleH, scaleW, 0.38);
      document.documentElement.classList.add("xlw-mobile-layout");
      document.body.classList.add("xlw-mobile-layout");
    } else {
      // 📱 直向手機：依螢幕寬度盡量吃滿
      const safeSidePadding = 0;
      const availableWidth = Math.max(320, window.innerWidth - safeSidePadding);
      finalScale = Math.min((availableWidth / boardNaturalWidth), 0.94);
      document.documentElement.classList.add("xlw-mobile-layout");
      document.body.classList.add("xlw-mobile-layout");
    }
  } else {
    // 💻 電腦版
    const topbarH = 48;
    const handPanelH = 200;
    const padding = 16;
    const availableHeight = window.innerHeight - topbarH - handPanelH - padding;
    const availableWidth = window.innerWidth - 32;
    const scaleH = availableHeight / boardNaturalHeight;
    const scaleW = availableWidth / boardNaturalWidth;
    finalScale = Math.min(scaleH, scaleW, 1.0);
    document.documentElement.classList.remove("xlw-mobile-layout");
    document.body.classList.remove("xlw-mobile-layout");
  }

  // 設定 CSS 變數與縮放樣式
  document.documentElement.style.setProperty("--xlw-mobile-scale", String(finalScale));
  
  if (isMobile && isLandscapeMobile) {
    board.style.transform = `translate(-50%, -46%) scale(${finalScale})`;
    board.style.transformOrigin = "center center";
    board.style.position = "absolute";
    board.style.top = "50%";
    board.style.left = "50%";
    board.style.margin = "0";
  } else {
    board.style.transform = `scale(${finalScale})`;
    board.style.transformOrigin = "top center";
    board.style.position = "";
    board.style.top = "";
    board.style.left = "";
    board.style.margin = "0 auto";
  }

  const shell = document.querySelector(".game-shell");
  const wrap = document.querySelector(".board-wrap");

  if (isMobile && isLandscapeMobile) {
    if (shell) {
      shell.style.height = "100vh";
      shell.style.minHeight = "100vh";
    }
    if (wrap) {
      wrap.style.height = "100%";
      wrap.style.minHeight = "100%";
    }
  } else {
    if (shell) {
      const h = Math.ceil(boardNaturalHeight * finalScale);
      shell.style.height = `${h}px`;
      shell.style.minHeight = `${h}px`;
    }
    if (wrap) {
      const h = Math.ceil(boardNaturalHeight * finalScale);
      wrap.style.height = `${h}px`;
      wrap.style.minHeight = `${h}px`;
    }
  }
}"""

    # Locate and replace adjustBoardScale in js
    start_marker = "function adjustBoardScale() {"
    idx = js_content.find(start_marker)
    if idx >= 0:
        # Find closing brace of function
        brace_count = 0
        end_idx = idx
        for i in range(idx + len(start_marker), len(js_content)):
            if js_content[i] == '{':
                brace_count += 1
            elif js_content[i] == '}':
                if brace_count == 0:
                    end_idx = i + 1
                    break
                else:
                    brace_count -= 1
        
        js_content = js_content[:idx] + updated_adjust_scale_js + js_content[end_idx:]

    open(js_path, 'w', encoding='utf-8').write(js_content)
    print("1. Updated static/game_v8.js adjustBoardScale function successfully!")

    # Update cache-buster in static/index.html to v=15.50-js-scaling-engine-fixed
    idx_path = 'static/index.html'
    idx_content = open(idx_path, encoding='utf-8').read()
    idx_content = re.sub(r'game_v8\.js\?v=[^"\']+', 'game_v8.js?v=15.50-js-scaling-engine-fixed', idx_content)
    idx_content = re.sub(r'style_v8\.css\?v=[^"\']+', 'style_v8.css?v=15.50-js-scaling-engine-fixed', idx_content)
    open(idx_path, 'w', encoding='utf-8').write(idx_content)
    print("2. Updated static/index.html cache-buster successfully!")

if __name__ == '__main__':
    fix_js_scaling_engine()
