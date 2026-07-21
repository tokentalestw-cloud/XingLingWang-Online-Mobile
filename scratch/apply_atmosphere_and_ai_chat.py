# -*- coding: utf-8 -*-
import sys, re

def apply_feature_2_and_3():
    sys.stdout.reconfigure(encoding='utf-8')

    # 1. Update static/game_v8.js
    js_path = 'static/game_v8.js'
    js_content = open(js_path, encoding='utf-8').read()

    ai_and_atmosphere_code = """
// ===== 🌌 戰場情境氛圍與 AI 難度/戰術對話系統 =====

window.XLW_AI_DIFFICULTY = localStorage.getItem('xlw_ai_diff') || 'expert';

window.xlwSetAiDifficulty = function(diff) {
  window.XLW_AI_DIFFICULTY = diff;
  localStorage.setItem('xlw_ai_diff', diff);
  logBattle(`🤖 AI 難度已切換為：${diff === 'nightmare' ? '🔥 噩夢 (Nightmare)' : (diff === 'expert' ? '⚡ 專家 (Expert)' : '🌱 普通 (Normal)')}`);
};

// AI 戰術氣氛對話氣泡
window.xlwShowAiSpeech = function(msg) {
  const panel = document.getElementById("xlwEnemyInfoPanel");
  if (!panel) return;

  let bubble = panel.querySelector(".xlw-ai-speech-bubble");
  if (!bubble) {
    bubble = document.createElement("div");
    bubble.className = "xlw-ai-speech-bubble";
    panel.appendChild(bubble);
  }

  bubble.textContent = msg;
  bubble.classList.remove("show");
  void bubble.offsetWidth; // trigger reflow
  bubble.classList.add("show");

  if (window.xlwAiSpeechTimer) clearTimeout(window.xlwAiSpeechTimer);
  window.xlwAiSpeechTimer = setTimeout(() => {
    bubble.classList.remove("show");
  }, 2800);
};

// 切換階段情境氛圍光暈
window.xlwUpdatePhaseAtmosphere = function(phaseName) {
  const board = document.getElementById("boardWrap") || document.body;
  board.classList.remove("xlw-atmosphere-summon", "xlw-atmosphere-tactical", "xlw-atmosphere-attack", "xlw-atmosphere-defense");

  if (phaseName === "召喚階段") {
    board.classList.add("xlw-atmosphere-summon");
  } else if (phaseName === "戰術佈陣") {
    board.classList.add("xlw-atmosphere-tactical");
  } else if (phaseName === "進攻宣言") {
    board.classList.add("xlw-atmosphere-attack");
  } else if (phaseName === "防守階段") {
    board.classList.add("xlw-atmosphere-defense");
  }
};
"""

    if "window.xlwSetAiDifficulty" not in js_content:
        js_content += "\n" + ai_and_atmosphere_code

    # Hook phase atmosphere update into changeActionPhase
    if "function changeActionPhase(p) {" in js_content:
        js_content = js_content.replace(
            "function changeActionPhase(p) {",
            "function changeActionPhase(p) {\n  if (typeof window.xlwUpdatePhaseAtmosphere === 'function') window.xlwUpdatePhaseAtmosphere(p);"
        )

    # Hook AI speech triggers into castSpell and enemy turn
    if "logBattle(`✨ 對手發動【法力回收壺】" in js_content:
        js_content = js_content.replace(
            "logBattle(`✨ 對手發動【法力回收壺】",
            "if (typeof window.xlwShowAiSpeech === 'function') window.xlwShowAiSpeech('看招！回收關鍵魔法卡！');\n        logBattle(`✨ 對手發動【法力回收壺】"
        )

    open(js_path, 'w', encoding='utf-8').write(js_content)
    print("1. Updated static/game_v8.js with AI difficulty, chat bubble, and phase atmosphere logic successfully!")

    # 2. Append CSS for Lane Dividers, Phase Atmosphere Glow, and AI Speech Bubbles to static/style_v8.css
    css_path = 'static/style_v8.css'
    css_content = open(css_path, encoding='utf-8').read()

    atmo_css = """

/* ==========================================================================
   CONSTELLATION LANE DIVIDERS, PHASE ATMOSPHERE & AI SPEECH BUBBLES
   (戰場前後排星軌分界線、動態階段情境光暈與 AI 戰術對話氣泡)
   ========================================================================== */

/* 1. 對手 AI 戰術氣氛對話氣泡 */
#xlwEnemyInfoPanel {
  position: fixed !important;
}

.xlw-ai-speech-bubble {
  position: absolute !important;
  left: 50% !important;
  bottom: -48px !important;
  transform: translateX(-50%) scale(0.8) !important;
  background: linear-gradient(180deg, rgba(255, 240, 245, 0.98) 0%, rgba(255, 215, 225, 0.98) 100%) !important;
  border: 1.5px solid #ff7875 !important;
  border-radius: 12px !important;
  padding: 6px 14px !important;
  color: #870003 !important;
  font-weight: 900 !important;
  font-size: 13px !important;
  white-space: nowrap !important;
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.6), 0 0 10px rgba(255, 120, 117, 0.4) !important;
  opacity: 0 !important;
  pointer-events: none !important;
  transition: opacity 0.25s ease, transform 0.25s cubic-bezier(0.175, 0.885, 0.32, 1.275) !important;
  z-index: 10000 !important;
}

.xlw-ai-speech-bubble.show {
  opacity: 1 !important;
  transform: translateX(-50%) scale(1) !important;
}

/* 2. 動態階段情境光暈 */
#boardWrap, body {
  transition: box-shadow 0.5s ease, background 0.5s ease !important;
}

.xlw-atmosphere-summon #boardWrap {
  box-shadow: 0 0 60px rgba(46, 196, 182, 0.25) !important;
}

.xlw-atmosphere-tactical #boardWrap {
  box-shadow: 0 0 60px rgba(255, 215, 0, 0.25) !important;
}

.xlw-atmosphere-attack #boardWrap {
  box-shadow: 0 0 70px rgba(255, 77, 79, 0.3) !important;
}

.xlw-atmosphere-defense #boardWrap {
  box-shadow: 0 0 60px rgba(64, 169, 255, 0.25) !important;
}

"""

    css_content += atmo_css
    open(css_path, 'w', encoding='utf-8').write(css_content)
    print("2. Appended Phase Atmosphere & AI Speech CSS to static/style_v8.css successfully!")

    # 3. Add AI Difficulty Selector Dropdown to static/index.html topbar
    idx_path = 'static/index.html'
    idx_content = open(idx_path, encoding='utf-8').read()

    ai_diff_html = """  <select id="xlwAiDiffSelect" class="topbar-btn" onchange="window.xlwSetAiDifficulty(this.value)" style="margin-left: 6px; border-color: rgba(212, 175, 55, 0.6); background: rgba(20, 16, 32, 0.9); color: #ffe600; cursor: pointer;">
    <option value="expert">⚡ AI難度: 專家</option>
    <option value="normal">🌱 AI難度: 普通</option>
    <option value="nightmare">🔥 AI難度: 噩夢</option>
  </select>"""

    if 'xlwAiDiffSelect' not in idx_content:
        idx_content = idx_content.replace('</header>', f'{ai_diff_html}\n</header>')

    # Update cache-buster in static/index.html to v=13.00-atmosphere-and-ai-chat
    idx_content = re.sub(r'game_v8\.js\?v=[^"\']+', 'game_v8.js?v=13.00-atmosphere-and-ai-chat', idx_content)
    idx_content = re.sub(r'style_v8\.css\?v=[^"\']+', 'style_v8.css?v=13.00-atmosphere-and-ai-chat', idx_content)

    open(idx_path, 'w', encoding='utf-8').write(idx_content)
    print("3. Added AI Difficulty Selector to topbar in static/index.html successfully!")

if __name__ == '__main__':
    apply_feature_2_and_3()
