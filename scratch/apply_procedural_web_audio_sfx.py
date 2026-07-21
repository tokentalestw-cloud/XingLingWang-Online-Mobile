# -*- coding: utf-8 -*-
import sys, re

def apply_sfx():
    sys.stdout.reconfigure(encoding='utf-8')

    # 1. Update static/game_v8.js with Web Audio API SFX engine
    js_path = 'static/game_v8.js'
    js_content = open(js_path, encoding='utf-8').read()

    sfx_engine_code = """
// ===== 🔊 輕柔沉浸 Web Audio API 音效系統 =====
(function() {
  let audioCtx = null;
  let sfxEnabled = localStorage.getItem('xlw_sfx_enabled') !== 'false';

  function getAudioContext() {
    if (!audioCtx) {
      const AudioContextClass = window.AudioContext || window.webkitAudioContext;
      if (AudioContextClass) {
        audioCtx = new AudioContextClass();
      }
    }
    if (audioCtx && audioCtx.state === 'suspended') {
      audioCtx.resume();
    }
    return audioCtx;
  }

  window.xlwToggleSFX = function() {
    sfxEnabled = !sfxEnabled;
    localStorage.setItem('xlw_sfx_enabled', sfxEnabled ? 'true' : 'false');
    const btn = document.getElementById('xlwSfxToggleBtn');
    if (btn) {
      btn.innerHTML = sfxEnabled ? '🔊 音效: 開' : '🔇 音效: 關';
    }
    if (sfxEnabled) window.xlwPlaySFX('phase');
  };

  window.xlwPlaySFX = function(type) {
    if (!sfxEnabled) return;
    try {
      const ctx = getAudioContext();
      if (!ctx) return;
      const now = ctx.currentTime;

      if (type === 'draw') {
        // 抽牌/滑牌聲 (柔和滑音)
        const osc = ctx.createOscillator();
        const gain = ctx.createGain();
        osc.type = 'sine';
        osc.frequency.setValueAtTime(300, now);
        osc.frequency.exponentialRampToValueAtTime(600, now + 0.08);
        gain.gain.setValueAtTime(0.12, now);
        gain.gain.exponentialRampToValueAtTime(0.001, now + 0.08);
        osc.connect(gain);
        gain.connect(ctx.destination);
        osc.start(now);
        osc.stop(now + 0.08);
      } else if (type === 'summon') {
        // 召喚/落牌聲 (金屬響亮回音)
        const osc = ctx.createOscillator();
        const gain = ctx.createGain();
        osc.type = 'triangle';
        osc.frequency.setValueAtTime(220, now);
        osc.frequency.exponentialRampToValueAtTime(520, now + 0.12);
        gain.gain.setValueAtTime(0.2, now);
        gain.gain.exponentialRampToValueAtTime(0.001, now + 0.15);
        osc.connect(gain);
        gain.connect(ctx.destination);
        osc.start(now);
        osc.stop(now + 0.15);
      } else if (type === 'spell') {
        // 魔法發動聲 (星光流動和弦)
        [523.25, 659.25, 783.99, 1046.50].forEach((freq, idx) => {
          const osc = ctx.createOscillator();
          const gain = ctx.createGain();
          osc.type = 'sine';
          osc.frequency.setValueAtTime(freq, now + idx * 0.04);
          gain.gain.setValueAtTime(0.1, now + idx * 0.04);
          gain.gain.exponentialRampToValueAtTime(0.001, now + idx * 0.04 + 0.25);
          osc.connect(gain);
          gain.connect(ctx.destination);
          osc.start(now + idx * 0.04);
          osc.stop(now + idx * 0.04 + 0.25);
        });
      } else if (type === 'coin') {
        // 投擲硬幣聲 (清脆清亮金屬迴響)
        const osc = ctx.createOscillator();
        const gain = ctx.createGain();
        osc.type = 'sine';
        osc.frequency.setValueAtTime(1200, now);
        osc.frequency.exponentialRampToValueAtTime(1800, now + 0.15);
        gain.gain.setValueAtTime(0.18, now);
        gain.gain.exponentialRampToValueAtTime(0.001, now + 0.2);
        osc.connect(gain);
        gain.connect(ctx.destination);
        osc.start(now);
        osc.stop(now + 0.2);
      } else if (type === 'attack') {
        // 攻擊撞擊聲 (重低音爆裂)
        const osc = ctx.createOscillator();
        const gain = ctx.createGain();
        osc.type = 'sawtooth';
        osc.frequency.setValueAtTime(140, now);
        osc.frequency.exponentialRampToValueAtTime(35, now + 0.18);
        gain.gain.setValueAtTime(0.25, now);
        gain.gain.exponentialRampToValueAtTime(0.001, now + 0.2);
        osc.connect(gain);
        gain.connect(ctx.destination);
        osc.start(now);
        osc.stop(now + 0.2);
      } else if (type === 'phase') {
        // 回合/階段切換聲 (溫和和弦)
        [440, 554.37].forEach((freq) => {
          const osc = ctx.createOscillator();
          const gain = ctx.createGain();
          osc.type = 'sine';
          osc.frequency.setValueAtTime(freq, now);
          gain.gain.setValueAtTime(0.1, now);
          gain.gain.exponentialRampToValueAtTime(0.001, now + 0.2);
          osc.connect(gain);
          gain.connect(ctx.destination);
          osc.start(now);
          osc.stop(now + 0.2);
        });
      }
    } catch (e) {}
  };
})();
"""

    if "window.xlwPlaySFX" not in js_content:
        js_content += "\n" + sfx_engine_code

    # Inject SFX triggers into key game functions:
    # 1. draw -> draw sound
    if "function draw(" in js_content:
        js_content = js_content.replace(
            "function draw(count = 1) {",
            "function draw(count = 1) {\n  if (typeof window.xlwPlaySFX === 'function') window.xlwPlaySFX('draw');"
        )

    # 2. castSpell -> spell sound
    if "async function castSpell(" in js_content:
        js_content = js_content.replace(
            "async function castSpell(card) {",
            "async function castSpell(card) {\n  if (typeof window.xlwPlaySFX === 'function') window.xlwPlaySFX('spell');"
        )

    # 3. startSinglePlayerCoinToss -> coin sound
    if "function startSinglePlayerCoinToss()" in js_content:
        js_content = js_content.replace(
            "function startSinglePlayerCoinToss() {",
            "function startSinglePlayerCoinToss() {\n  if (typeof window.xlwPlaySFX === 'function') window.xlwPlaySFX('coin');"
        )

    # 4. changeActionPhase -> phase sound
    if "function changeActionPhase(" in js_content:
        js_content = js_content.replace(
            "function changeActionPhase(p) {",
            "function changeActionPhase(p) {\n  if (typeof window.xlwPlaySFX === 'function') window.xlwPlaySFX('phase');"
        )

    open(js_path, 'w', encoding='utf-8').write(js_content)
    print("1. Injected procedural Web Audio SFX engine into static/game_v8.js successfully!")

    # 2. Add SFX toggle button to static/index.html topbar
    idx_path = 'static/index.html'
    idx_content = open(idx_path, encoding='utf-8').read()

    sfx_btn_html = '<button id="xlwSfxToggleBtn" class="topbar-btn" onclick="window.xlwToggleSFX()" style="margin-left: 8px; border-color: rgba(212, 175, 55, 0.6);">🔊 音效: 開</button>'
    if 'xlwSfxToggleBtn' not in idx_content:
        idx_content = idx_content.replace('</header>', f'  {sfx_btn_html}\n</header>')

    # Update cache-buster in static/index.html to v=12.60-procedural-web-audio-sfx
    idx_content = re.sub(r'game_v8\.js\?v=[^"\']+', 'game_v8.js?v=12.60-procedural-web-audio-sfx', idx_content)
    idx_content = re.sub(r'style_v8\.css\?v=[^"\']+', 'style_v8.css?v=12.60-procedural-web-audio-sfx', idx_content)

    open(idx_path, 'w', encoding='utf-8').write(idx_content)
    print("2. Added SFX toggle button to topbar in static/index.html successfully!")

if __name__ == '__main__':
    apply_sfx()
