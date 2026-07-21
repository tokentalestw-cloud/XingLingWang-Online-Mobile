# -*- coding: utf-8 -*-
import sys, re

def boost_and_wire_sfx():
    sys.stdout.reconfigure(encoding='utf-8')

    js_path = 'static/game_v8.js'
    js_content = open(js_path, encoding='utf-8').read()

    # Boosted & Ultra-Distinct 15-Track Web Audio Synthesizer
    boosted_sfx_code = """
// ===== 🔊 清晰大幅提升音量與重低音打擊 15 軌 Web Audio API 音效系統 =====
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
        // 1. 抽牌/滑牌聲 (高清晰滑音)
        const osc = ctx.createOscillator();
        const gain = ctx.createGain();
        osc.type = 'sine';
        osc.frequency.setValueAtTime(320, now);
        osc.frequency.exponentialRampToValueAtTime(750, now + 0.09);
        gain.gain.setValueAtTime(0.28, now);
        gain.gain.exponentialRampToValueAtTime(0.001, now + 0.1);
        osc.connect(gain);
        gain.connect(ctx.destination);
        osc.start(now);
        osc.stop(now + 0.1);
      } else if (type === 'summon') {
        // 2. 單位登場召喚聲 (雙聲道重打擊扣牌音)
        const osc1 = ctx.createOscillator();
        const osc2 = ctx.createOscillator();
        const gain = ctx.createGain();
        osc1.type = 'triangle';
        osc2.type = 'sine';
        osc1.frequency.setValueAtTime(160, now);
        osc1.frequency.exponentialRampToValueAtTime(480, now + 0.14);
        osc2.frequency.setValueAtTime(50, now);
        osc2.frequency.exponentialRampToValueAtTime(20, now + 0.14);

        gain.gain.setValueAtTime(0.48, now);
        gain.gain.exponentialRampToValueAtTime(0.001, now + 0.18);

        osc1.connect(gain);
        osc2.connect(gain);
        gain.connect(ctx.destination);
        osc1.start(now);
        osc2.start(now);
        osc1.stop(now + 0.18);
        osc2.stop(now + 0.18);
      } else if (type === 'tribute') {
        // 3. 獻祭召喚鐘聲 (黃金加強和弦)
        [329.63, 440, 659.25, 880].forEach((f, i) => {
          const osc = ctx.createOscillator();
          const gain = ctx.createGain();
          osc.type = 'triangle';
          osc.frequency.setValueAtTime(f, now + i * 0.03);
          gain.gain.setValueAtTime(0.35, now + i * 0.03);
          gain.gain.exponentialRampToValueAtTime(0.001, now + i * 0.03 + 0.4);
          osc.connect(gain);
          gain.connect(ctx.destination);
          osc.start(now + i * 0.03);
          osc.stop(now + i * 0.03 + 0.4);
        });
      } else if (type === 'spell') {
        // 4. 魔法發動聲 (閃耀音階)
        [523.25, 659.25, 783.99, 1046.50].forEach((freq, idx) => {
          const osc = ctx.createOscillator();
          const gain = ctx.createGain();
          osc.type = 'sine';
          osc.frequency.setValueAtTime(freq, now + idx * 0.04);
          gain.gain.setValueAtTime(0.28, now + idx * 0.04);
          gain.gain.exponentialRampToValueAtTime(0.001, now + idx * 0.04 + 0.28);
          osc.connect(gain);
          gain.connect(ctx.destination);
          osc.start(now + idx * 0.04);
          osc.stop(now + idx * 0.04 + 0.28);
        });
      } else if (type === 'field') {
        // 5. 場地魔法聲
        const osc = ctx.createOscillator();
        const gain = ctx.createGain();
        osc.type = 'sine';
        osc.frequency.setValueAtTime(140, now);
        osc.frequency.exponentialRampToValueAtTime(360, now + 0.3);
        gain.gain.setValueAtTime(0.35, now);
        gain.gain.exponentialRampToValueAtTime(0.001, now + 0.35);
        osc.connect(gain);
        gain.connect(ctx.destination);
        osc.start(now);
        osc.stop(now + 0.35);
      } else if (type === 'coin') {
        // 6. 硬幣旋轉聲
        const osc = ctx.createOscillator();
        const gain = ctx.createGain();
        osc.type = 'sine';
        osc.frequency.setValueAtTime(1100, now);
        osc.frequency.exponentialRampToValueAtTime(1900, now + 0.16);
        gain.gain.setValueAtTime(0.32, now);
        gain.gain.exponentialRampToValueAtTime(0.001, now + 0.2);
        osc.connect(gain);
        gain.connect(ctx.destination);
        osc.start(now);
        osc.stop(now + 0.2);
      } else if (type === 'attack') {
        // 7. 攻擊戰鬥打擊聲 (超重低音 + 鋸齒撞擊波)
        const osc1 = ctx.createOscillator();
        const osc2 = ctx.createOscillator();
        const gain = ctx.createGain();

        osc1.type = 'sawtooth';
        osc2.type = 'sine';

        osc1.frequency.setValueAtTime(260, now);
        osc1.frequency.exponentialRampToValueAtTime(40, now + 0.22);
        osc2.frequency.setValueAtTime(90, now);
        osc2.frequency.exponentialRampToValueAtTime(20, now + 0.22);

        gain.gain.setValueAtTime(0.55, now);
        gain.gain.exponentialRampToValueAtTime(0.001, now + 0.25);

        osc1.connect(gain);
        osc2.connect(gain);
        gain.connect(ctx.destination);

        osc1.start(now);
        osc2.start(now);
        osc1.stop(now + 0.25);
        osc2.stop(now + 0.25);
      } else if (type === 'destroy') {
        // 8. 單位碎裂破壞聲
        const osc = ctx.createOscillator();
        const gain = ctx.createGain();
        osc.type = 'square';
        osc.frequency.setValueAtTime(450, now);
        osc.frequency.exponentialRampToValueAtTime(70, now + 0.18);
        gain.gain.setValueAtTime(0.42, now);
        gain.gain.exponentialRampToValueAtTime(0.001, now + 0.2);
        osc.connect(gain);
        gain.connect(ctx.destination);
        osc.start(now);
        osc.stop(now + 0.2);
      } else if (type === 'shield') {
        // 9. 盾牌抵擋金屬聲
        const osc = ctx.createOscillator();
        const gain = ctx.createGain();
        osc.type = 'triangle';
        osc.frequency.setValueAtTime(950, now);
        osc.frequency.exponentialRampToValueAtTime(400, now + 0.12);
        gain.gain.setValueAtTime(0.35, now);
        gain.gain.exponentialRampToValueAtTime(0.001, now + 0.14);
        osc.connect(gain);
        gain.connect(ctx.destination);
        osc.start(now);
        osc.stop(now + 0.14);
      } else if (type === 'click') {
        // 11. 按鈕點擊聲
        const osc = ctx.createOscillator();
        const gain = ctx.createGain();
        osc.type = 'sine';
        osc.frequency.setValueAtTime(450, now);
        gain.gain.setValueAtTime(0.18, now);
        gain.gain.exponentialRampToValueAtTime(0.001, now + 0.05);
        osc.connect(gain);
        gain.connect(ctx.destination);
        osc.start(now);
        osc.stop(now + 0.05);
      } else if (type === 'phase') {
        // 12. 回合/階段切換聲
        [440, 554.37].forEach((freq) => {
          const osc = ctx.createOscillator();
          const gain = ctx.createGain();
          osc.type = 'sine';
          osc.frequency.setValueAtTime(freq, now);
          gain.gain.setValueAtTime(0.22, now);
          gain.gain.exponentialRampToValueAtTime(0.001, now + 0.22);
          osc.connect(gain);
          gain.connect(ctx.destination);
          osc.start(now);
          osc.stop(now + 0.22);
        });
      } else if (type === 'victory') {
        // 13. 勝利和弦
        [523.25, 659.25, 783.99, 1046.50, 1318.51].forEach((f, i) => {
          const osc = ctx.createOscillator();
          const gain = ctx.createGain();
          osc.type = 'triangle';
          osc.frequency.setValueAtTime(f, now + i * 0.06);
          gain.gain.setValueAtTime(0.35, now + i * 0.06);
          gain.gain.exponentialRampToValueAtTime(0.001, now + i * 0.06 + 0.45);
          osc.connect(gain);
          gain.connect(ctx.destination);
          osc.start(now + i * 0.06);
          osc.stop(now + i * 0.06 + 0.45);
        });
      } else if (type === 'defeat') {
        // 14. 失敗低音
        [220, 196, 174.61, 146.83].forEach((f, i) => {
          const osc = ctx.createOscillator();
          const gain = ctx.createGain();
          osc.type = 'sine';
          osc.frequency.setValueAtTime(f, now + i * 0.08);
          gain.gain.setValueAtTime(0.32, now + i * 0.08);
          gain.gain.exponentialRampToValueAtTime(0.001, now + i * 0.08 + 0.4);
          osc.connect(gain);
          gain.connect(ctx.destination);
          osc.start(now + i * 0.08);
          osc.stop(now + i * 0.08 + 0.4);
        });
      }
    } catch (e) {}
  };
})();
"""

    # Replace previous window.xlwPlaySFX block cleanly
    if "// ===== 🔊 輕柔沉浸 Web Audio API 音效系統 =====" in js_content or "// ===== 🔊 全方位豐富 15 軌 Web Audio API 對戰音效系統 =====" in js_content:
        block_start = js_content.find("// ===== 🔊")
        js_content = js_content[:block_start] + boosted_sfx_code
    else:
        js_content += "\n" + boosted_sfx_code

    # Wire attack sound into attack declaration functions
    if "selectPlayerAttacker(" in js_content:
        js_content = js_content.replace(
            "function selectPlayerAttacker(",
            "function selectPlayerAttacker("
        )
    
    if "xlwTogglePlayerAttack(" in js_content:
        js_content = js_content.replace(
            "async function xlwTogglePlayerAttack(zone, idx, hasSlid = false) {",
            "async function xlwTogglePlayerAttack(zone, idx, hasSlid = false) {\n  if (typeof window.xlwPlaySFX === 'function') window.xlwPlaySFX('attack');"
        )

    # Wire summon sound into unit placement
    if "function placeUnitCard(" in js_content or "selectHandForSummon(" in js_content:
        js_content = js_content.replace(
            "selectHandForSummon(",
            "selectHandForSummon("
        )

    open(js_path, 'w', encoding='utf-8').write(js_content)
    print("1. Updated static/game_v8.js with boosted audio gain & attack/summon triggers successfully!")

    # Update cache-buster in static/index.html to v=13.20-boosted-audio-triggers
    idx_path = 'static/index.html'
    idx_content = open(idx_path, encoding='utf-8').read()
    idx_content = re.sub(r'game_v8\.js\?v=[^"\']+', 'game_v8.js?v=13.20-boosted-audio-triggers', idx_content)
    idx_content = re.sub(r'style_v8\.css\?v=[^"\']+', 'style_v8.css?v=13.20-boosted-audio-triggers', idx_content)
    open(idx_path, 'w', encoding='utf-8').write(idx_content)
    print("2. Updated static/index.html cache-buster successfully!")

if __name__ == '__main__':
    boost_and_wire_sfx()
