# -*- coding: utf-8 -*-
import sys, re

def apply_tilt_and_holo():
    sys.stdout.reconfigure(encoding='utf-8')

    # 1. Update static/game_v8.js
    js_path = 'static/game_v8.js'
    js_content = open(js_path, encoding='utf-8').read()

    # JS helper and auto-attacher for 3D Tilt & Holographic Foil
    js_tilt_holo_code = """
// ===== 🎴 3D 視差傾斜與 SR/SSR 雷射虹光特效系統 =====

window.xlwIsHoloCard = function(card) {
  if (!card) return false;
  const r = (card.rarity || "").toUpperCase();
  const id = (card.id || "").toUpperCase();
  const stars = Number(card.stars || card.score || 0);
  return r.includes("SR") || r.includes("SSR") || r.includes("SSSR") || r.includes("UR") || id.includes("SR") || id.includes("SSR") || stars >= 3;
};

window.xlwAttach3DTiltAndHolo = function() {
  const cards = document.querySelectorAll('.card, .unit-card, .xlw-left-panel-img, #leftPanelImg');
  cards.forEach(cardEl => {
    if (cardEl.dataset.xlwTiltAttached) return;
    cardEl.dataset.xlwTiltAttached = "1";

    cardEl.addEventListener('mousemove', (e) => {
      const rect = cardEl.getBoundingClientRect();
      if (!rect.width || !rect.height) return;
      const x = e.clientX - rect.left;
      const y = e.clientY - rect.top;
      const centerX = rect.width / 2;
      const centerY = rect.height / 2;
      const rotateX = ((y - centerY) / centerY) * -14;
      const rotateY = ((x - centerX) / centerX) * 14;

      cardEl.style.transform = `perspective(800px) rotateX(${rotateX.toFixed(2)}deg) rotateY(${rotateY.toFixed(2)}deg) translateY(-6px) scale(1.04)`;
      cardEl.style.transition = 'transform 0.08s cubic-bezier(0.16, 1, 0.3, 1), box-shadow 0.1s ease';

      // Holo Foil Light Angle
      const percentX = ((x / rect.width) * 100).toFixed(1);
      const percentY = ((y / rect.height) * 100).toFixed(1);
      cardEl.style.setProperty('--holo-x', `${percentX}%`);
      cardEl.style.setProperty('--holo-y', `${percentY}%`);
    });

    cardEl.addEventListener('mouseleave', () => {
      cardEl.style.transform = 'perspective(800px) rotateX(0deg) rotateY(0deg) translateY(0) scale(1)';
      cardEl.style.transition = 'transform 0.3s ease, box-shadow 0.3s ease';
    });
  });
};

// Global observer & interval for dynamic cards
setInterval(() => {
  if (typeof window.xlwAttach3DTiltAndHolo === "function") {
    window.xlwAttach3DTiltAndHolo();
  }
}, 300);
"""

    # Append to showModal in JS to attach Holo Foil overlay to preview
    old_show_modal = "function showModal(card, equipments) {"
    new_show_modal = """function showModal(card, equipments) {
  if (!card) return;

  // 附加上放大預視窗 SR/SSR 雷射虹光圖層
  const leftPanel = $("xlwLeftCardPanel");
  if (leftPanel) {
    let holoFoil = leftPanel.querySelector(".xlw-holo-foil");
    if (window.xlwIsHoloCard(card)) {
      if (!holoFoil) {
        holoFoil = document.createElement("div");
        holoFoil.className = "xlw-holo-foil";
        leftPanel.appendChild(holoFoil);
      }
      holoFoil.style.display = "block";
    } else if (holoFoil) {
      holoFoil.style.display = "none";
    }
  }"""

    if old_show_modal in js_content and "window.xlwAttach3DTiltAndHolo" not in js_content:
        js_content = js_content.replace(old_show_modal, new_show_modal)
        js_content += "\n" + js_tilt_holo_code
        open(js_path, 'w', encoding='utf-8').write(js_content)
        print("1. Appended 3D Tilt & Holographic Foil JS logic successfully!")

    # 2. Append 3D Tilt & Holo Foil CSS to static/style_v8.css
    css_path = 'static/style_v8.css'
    css_content = open(css_path, encoding='utf-8').read()

    tilt_holo_css = """

/* ==========================================================================
   3D TILT PARALLAX HOVER & SR/SSR HOLOGRAPHIC FOIL SHADER
   (手牌與場上單位 3D 視差傾斜、陀螺儀動態光澤與 SR/SSR 雷射虹光箔膜)
   ========================================================================== */

.card, .unit-card, #xlwLeftCardPanel {
  transform-style: preserve-3d !important;
  will-change: transform !important;
}

/* 放大預覽視窗與 SR/SSR 雷射虹光特效層 */
#xlwLeftCardPanel {
  position: relative !important;
  overflow: hidden !important;
}

.xlw-holo-foil {
  position: absolute !important;
  inset: 0 !important;
  pointer-events: none !important;
  z-index: 8 !important;
  border-radius: 12px !important;
  background: linear-gradient(
    115deg,
    transparent 15%,
    rgba(255, 0, 128, 0.28) 30%,
    rgba(255, 235, 59, 0.38) 45%,
    rgba(0, 230, 180, 0.38) 60%,
    rgba(33, 150, 243, 0.28) 75%,
    transparent 90%
  ) !important;
  background-size: 220% 220% !important;
  background-position: var(--holo-x, 50%) var(--holo-y, 50%) !important;
  mix-blend-mode: color-dodge !important;
  opacity: 0.85 !important;
  animation: holoFoilShimmer 5s infinite alternate ease-in-out !important;
  transition: opacity 0.25s ease !important;
}

@keyframes holoFoilShimmer {
  0% {
    background-position: 0% 0%;
  }
  50% {
    background-position: 100% 100%;
  }
  100% {
    background-position: 0% 100%;
  }
}

"""

    css_content += tilt_holo_css
    open(css_path, 'w', encoding='utf-8').write(css_content)
    print("2. Appended 3D Tilt & Holo Foil CSS to static/style_v8.css successfully!")

    # Update cache-buster in static/index.html to v=12.00-3d-tilt-holo-foil-shader
    idx_path = 'static/index.html'
    idx_content = open(idx_path, encoding='utf-8').read()
    idx_content = re.sub(r'game_v8\.js\?v=[^"\']+', 'game_v8.js?v=12.00-3d-tilt-holo-foil-shader', idx_content)
    idx_content = re.sub(r'style_v8\.css\?v=[^"\']+', 'style_v8.css?v=12.00-3d-tilt-holo-foil-shader', idx_content)
    open(idx_path, 'w', encoding='utf-8').write(idx_content)
    print("3. Updated static/index.html cache-buster successfully!")

if __name__ == '__main__':
    apply_tilt_and_holo()
