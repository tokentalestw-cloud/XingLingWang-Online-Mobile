# -*- coding: utf-8 -*-
import sys, re

def apply_comprehensive_sfx():
    sys.stdout.reconfigure(encoding='utf-8')

    js_path = 'static/game_v8.js'
    js_content = open(js_path, encoding='utf-8').read()

    # Enhanced 15-sound Web Audio API Synthesizer
    sfx_expanded_code = """
// ===== 🔊 全方位豐富 15 軌 Web Audio API 對戰音效系統 =====
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
        // 1. 抽牌/滑牌聲
        const osc = ctx.createOscillator();
        const gain = ctx.createGain();
        osc.type = 'sine';
        osc.frequency.setValueAtTime(280, now);
        osc.frequency.exponentialRampToValueAtTime(620, now + 0.08);
        gain.gain.setValueAtTime(0.12, now);
        gain.gain.exponentialRampToValueAtTime(0.001, now + 0.08);
        osc.connect(gain);
        gain.connect(ctx.destination);
        osc.start(now);
        osc.stop(now + 0.08);
      } else if (type === 'summon') {
        // 2. 普通召喚/落牌聲
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
      } else if (type === 'tribute') {
        // 3. 獻祭召喚鐘聲 (黃金和弦)
        [329.63, 440, 659.25].forEach((f, i) => {
          const osc = ctx.createOscillator();
          const gain = ctx.createGain();
          osc.type = 'sine';
          osc.frequency.setValueAtTime(f, now + i * 0.03);
          gain.gain.setValueAtTime(0.15, now + i * 0.03);
          gain.gain.exponentialRampToValueAtTime(0.001, now + i * 0.03 + 0.35);
          osc.connect(gain);
          gain.connect(ctx.destination);
          osc.start(now + i * 0.03);
          osc.stop(now + i * 0.03 + 0.35);
        });
      } else if (type === 'spell') {
        // 4. 魔法發動聲 (星茫流光)
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
      } else if (type === 'field') {
        // 5. 場地魔法卡發動聲 (深邃共鳴)
        const osc = ctx.createOscillator();
        const gain = ctx.createGain();
        osc.type = 'sine';
        osc.frequency.setValueAtTime(150, now);
        osc.frequency.exponentialRampToValueAtTime(320, now + 0.3);
        gain.gain.setValueAtTime(0.2, now);
        gain.gain.exponentialRampToValueAtTime(0.001, now + 0.35);
        osc.connect(gain);
        gain.connect(ctx.destination);
        osc.start(now);
        osc.stop(now + 0.35);
      } else if (type === 'coin') {
        // 6. 命運硬幣旋轉聲
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
        // 7. 攻擊打擊聲
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
      } else if (type === 'destroy') {
        // 8. 單位碎裂破壞聲
        const osc = ctx.createOscillator();
        const gain = ctx.createGain();
        osc.type = 'square';
        osc.frequency.setValueAtTime(400, now);
        osc.frequency.exponentialRampToValueAtTime(80, now + 0.15);
        gain.gain.setValueAtTime(0.18, now);
        gain.gain.exponentialRampToValueAtTime(0.001, now + 0.15);
        osc.connect(gain);
        gain.connect(ctx.destination);
        osc.start(now);
        osc.stop(now + 0.15);
      } else if (type === 'shield') {
        // 9. 盾牌抵擋金屬聲
        const osc = ctx.createOscillator();
        const gain = ctx.createGain();
        osc.type = 'triangle';
        osc.frequency.setValueAtTime(880, now);
        osc.frequency.exponentialRampToValueAtTime(440, now + 0.1);
        gain.gain.setValueAtTime(0.15, now);
        gain.gain.exponentialRampToValueAtTime(0.001, now + 0.12);
        osc.connect(gain);
        gain.connect(ctx.destination);
        osc.start(now);
        osc.stop(now + 0.12);
      } else if (type === 'potion') {
        // 10. 裝備/藥水效果聲
        [600, 900].forEach((f, idx) => {
          const osc = ctx.createOscillator();
          const gain = ctx.createGain();
          osc.type = 'sine';
          osc.frequency.setValueAtTime(f, now + idx * 0.05);
          gain.gain.setValueAtTime(0.08, now + idx * 0.05);
          gain.gain.exponentialRampToValueAtTime(0.001, now + idx * 0.05 + 0.15);
          osc.connect(gain);
          gain.connect(ctx.destination);
          osc.start(now + idx * 0.05);
          osc.stop(now + idx * 0.05 + 0.15);
        });
      } else if (type === 'click') {
        // 11. 按鈕點擊聲
        const osc = ctx.createOscillator();
        const gain = ctx.createGain();
        osc.type = 'sine';
        osc.frequency.setValueAtTime(400, now);
        gain.gain.setValueAtTime(0.06, now);
        gain.gain.exponentialRampToValueAtTime(0.001, now + 0.04);
        osc.connect(gain);
        gain.connect(ctx.destination);
        osc.start(now);
        osc.stop(now + 0.04);
      } else if (type === 'phase') {
        // 12. 回合/階段切換聲
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
      } else if (type === 'victory') {
        // 13. 勝利和弦
        [523.25, 659.25, 783.99, 1046.50, 1318.51].forEach((f, i) => {
          const osc = ctx.createOscillator();
          const gain = ctx.createGain();
          osc.type = 'triangle';
          osc.frequency.setValueAtTime(f, now + i * 0.06);
          gain.gain.setValueAtTime(0.15, now + i * 0.06);
          gain.gain.exponentialRampToValueAtTime(0.001, now + i * 0.06 + 0.4);
          osc.connect(gain);
          gain.connect(ctx.destination);
          osc.start(now + i * 0.06);
          osc.stop(now + i * 0.06 + 0.4);
        });
      } else if (type === 'defeat') {
        // 14. 失敗低音
        [220, 196, 174.61, 146.83].forEach((f, i) => {
          const osc = ctx.createOscillator();
          const gain = ctx.createGain();
          osc.type = 'sine';
          osc.frequency.setValueAtTime(f, now + i * 0.08);
          gain.gain.setValueAtTime(0.15, now + i * 0.08);
          gain.gain.exponentialRampToValueAtTime(0.001, now + i * 0.08 + 0.35);
          osc.connect(gain);
          gain.connect(ctx.destination);
          osc.start(now + i * 0.08);
          osc.stop(now + i * 0.08 + 0.35);
        });
      } else if (type === 'graveyard') {
        // 15. 墓地回收/除外聲
        const osc = ctx.createOscillator();
        const gain = ctx.createGain();
        osc.type = 'sine';
        osc.frequency.setValueAtTime(350, now);
        osc.frequency.exponentialRampToValueAtTime(180, now + 0.15);
        gain.gain.setValueAtTime(0.1, now);
        gain.gain.exponentialRampToValueAtTime(0.001, now + 0.15);
        osc.connect(gain);
        gain.connect(ctx.destination);
        osc.start(now);
        osc.stop(now + 0.15);
      }
    } catch (e) {}
  };
})();
"""

    # Replace old SFX block if exists
    if "window.xlwPlaySFX = function(type)" in js_content:
        block_start = js_content.find("// ===== 🔊 輕柔沉浸 Web Audio API 音效系統 =====")
        if block_start >= 0:
            js_content = js_content[:block_start] + sfx_expanded_code
        else:
            js_content += "\n" + sfx_expanded_code
    else:
        js_content += "\n" + sfx_expanded_code

    # Add SFX trigger to confirmTribute (獻祭)
    if "function confirmTribute()" in js_content:
        js_content = js_content.replace(
            "function confirmTribute() {",
            "function confirmTribute() {\n  if (typeof window.xlwPlaySFX === 'function') window.xlwPlaySFX('tribute');"
        )

    # Add SFX trigger to button clicks
    if "function changeActionPhase(" in js_content:
        js_content = js_content.replace(
            "function changeActionPhase(p) {\n  if (typeof window.xlwPlaySFX === 'function') window.xlwPlaySFX('phase');",
            "function changeActionPhase(p) {\n  if (typeof window.xlwPlaySFX === 'function') { window.xlwPlaySFX('click'); window.xlwPlaySFX('phase'); }"
        )

    open(js_path, 'w', encoding='utf-8').write(js_content)
    print("1. Updated static/game_v8.js with 15-track expanded SFX engine successfully!")

    # Update cache-buster in static/index.html to v=13.10-comprehensive-15-track-sfx
    idx_path = 'static/index.html'
    idx_content = open(idx_path, encoding='utf-8').read()
    idx_content = re.sub(r'game_v8\.js\?v=[^"\']+', 'game_v8.js?v=13.10-comprehensive-15-track-sfx', idx_content)
    idx_content = re.sub(r'style_v8\.css\?v=[^"\']+', 'style_v8.css?v=13.10-comprehensive-15-track-sfx', idx_content)
    open(idx_path, 'w', encoding='utf-8').write(idx_content)
    print("2. Updated static/index.html cache-buster successfully!")

if __name__ == '__main__':
    apply_comprehensive_sfx()
