# -*- coding: utf-8 -*-
import sys, re

def apply_forest_distinction():
    sys.stdout.reconfigure(encoding='utf-8')

    # 1. Update pForest state logic in static/game_v8.js
    js_path = 'static/game_v8.js'
    js_content = open(js_path, encoding='utf-8').read()

    old_forest_logic = """  // 森林召喚區域同步狀態
  const pForest = $("playerForest");
  if (pForest) {
    const canSum = (phase === "召喚階段" && !normalSummonUsed) || (phase === "戰術佈陣" && !tacticalSummonUsed);
    if (canSum) {
      pForest.style.pointerEvents = "auto";
      pForest.style.cursor = "pointer";
      pForest.style.opacity = "1";
      pForest.style.filter = "none";
      pForest.classList.remove("disabled-forest");
    } else {
      pForest.style.pointerEvents = "none";
      pForest.style.cursor = "not-allowed";
      pForest.style.opacity = "0.55";
      pForest.style.filter = "grayscale(0.45) brightness(0.75)";
      pForest.classList.add("disabled-forest");
    }
  }"""

    new_forest_logic = """  // 森林召喚區域同步狀態 (清晰區分可召喚與不可召喚狀態)
  const pForest = $("playerForest");
  if (pForest) {
    const canSum = isMyTurn && ((phase === "召喚階段" && !normalSummonUsed) || (phase === "戰術佈陣" && !tacticalSummonUsed));
    const forestOverlay = pForest.querySelector(".forest-3d-overlay");
    if (canSum) {
      pForest.style.pointerEvents = "auto";
      pForest.style.cursor = "pointer";
      pForest.style.opacity = "1";
      pForest.style.filter = "none";
      pForest.classList.remove("disabled-forest");
      pForest.classList.add("active-summon-forest");
      if (forestOverlay) {
        forestOverlay.innerHTML = `✨ 我方森林區<br><span style="color: #00ff7f; font-weight: 900; text-shadow: 0 0 8px #00ff7f;">▶ 點擊召喚 小旅人 ◀</span>`;
      }
    } else {
      pForest.style.pointerEvents = "none";
      pForest.style.cursor = "not-allowed";
      pForest.style.opacity = "0.45";
      pForest.style.filter = "grayscale(0.85) brightness(0.45)";
      pForest.classList.add("disabled-forest");
      pForest.classList.remove("active-summon-forest");
      if (forestOverlay) {
        forestOverlay.innerHTML = `🔒 我方森林區<br><span style="color: #aaaaaa; font-weight: bold;">(已使用本回合召喚)</span>`;
      }
    }
  }"""

    if "const canSum = (phase === \"召喚階段\"" in js_content or "const pForest = $(\"playerForest\");" in js_content:
        js_content = js_content.replace(old_forest_logic, new_forest_logic)
        open(js_path, 'w', encoding='utf-8').write(js_content)
        print("1. Updated pForest state logic in static/game_v8.js successfully!")

    # 2. Append CSS pulse animation and distinction styles to static/style_v8.css
    css_path = 'static/style_v8.css'
    css_content = open(css_path, encoding='utf-8').read()

    distinction_css = """

/* ==========================================================================
   FOREST CAN-SUMMON VS CANNOT-SUMMON VIVID VISUAL DISTINCTION
   (我方森林區【可召喚】與【不可召喚】極致明顯視覺差異與霓虹脈衝動畫)
   ========================================================================== */

#playerForest.active-summon-forest {
  border: 2.5px solid #00ff7f !important;
  box-shadow: 0 0 25px rgba(0, 255, 127, 0.9), inset 0 0 20px rgba(0, 255, 127, 0.45) !important;
  animation: forestCanSummonPulse 1.8s infinite ease-in-out !important;
  cursor: pointer !important;
}

#playerForest.active-summon-forest:hover {
  transform: translateY(-5px) scale(1.06) !important;
  box-shadow: 0 0 35px rgba(0, 255, 127, 1), inset 0 0 30px rgba(0, 255, 127, 0.65) !important;
}

#playerForest.disabled-forest {
  border: 2px solid #555555 !important;
  opacity: 0.45 !important;
  filter: grayscale(0.85) brightness(0.45) !important;
  box-shadow: none !important;
  animation: none !important;
  cursor: not-allowed !important;
}

@keyframes forestCanSummonPulse {
  0% {
    box-shadow: 0 0 15px rgba(0, 255, 127, 0.6), inset 0 0 12px rgba(0, 255, 127, 0.3);
    border-color: #00ff7f;
  }
  50% {
    box-shadow: 0 0 32px rgba(0, 255, 127, 1), inset 0 0 25px rgba(0, 255, 127, 0.65);
    border-color: #80ffc2;
  }
  100% {
    box-shadow: 0 0 15px rgba(0, 255, 127, 0.6), inset 0 0 12px rgba(0, 255, 127, 0.3);
    border-color: #00ff7f;
  }
}

"""

    css_content += distinction_css
    open(css_path, 'w', encoding='utf-8').write(css_content)
    print("2. Appended forest summon state distinction CSS to static/style_v8.css successfully!")

    # Update cache-buster in static/index.html to v=10.70-forest-summon-state-distinction
    idx_path = 'static/index.html'
    idx_content = open(idx_path, encoding='utf-8').read()
    idx_content = re.sub(r'game_v8\.js\?v=[^"\']+', 'game_v8.js?v=10.70-forest-summon-state-distinction', idx_content)
    idx_content = re.sub(r'style_v8\.css\?v=[^"\']+', 'style_v8.css?v=10.70-forest-summon-state-distinction', idx_content)
    open(idx_path, 'w', encoding='utf-8').write(idx_content)
    print("3. Updated static/index.html cache-buster successfully!")

if __name__ == '__main__':
    apply_forest_distinction()
